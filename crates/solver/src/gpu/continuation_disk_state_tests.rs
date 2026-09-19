//! Test-only disk parking. No production session format or APIs change.
use std::fs::{self, File, OpenOptions};
use std::io::{self, BufWriter, Read, Write};
use std::path::{Path, PathBuf};

const MAGIC: u64 = 0x47544f5353440001;
const HEADER_BYTES: u64 = 72;

fn invalid(message: &str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message)
}

fn bytes(values: &[f32]) -> &[u8] {
    assert!(cfg!(target_endian = "little"));
    // Every f32 bit pattern is valid; alignment is preserved by the owning Vec.
    unsafe { std::slice::from_raw_parts(values.as_ptr().cast(), values.len() * 4) }
}

fn checksum(arrays: &[Vec<f32>; 4]) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for a in arrays {
        for v in a {
            h = (h ^ u64::from(v.to_bits())).wrapping_mul(0x100000001b3);
        }
    }
    h
}

pub(super) struct DiskState {
    root: PathBuf,
    key: u64,
    generation: u64,
    iteration: u32,
    lengths: [usize; 4],
    hash: u64,
}

impl DiskState {
    pub(super) fn create(root: &Path, key: u64, arrays: &[Vec<f32>; 4], iteration: u32) -> io::Result<Self> {
        let mut state = Self {
            root: root.to_path_buf(), key, generation: 0, iteration,
            lengths: std::array::from_fn(|k| arrays[k].len()), hash: checksum(arrays),
        };
        state.write_generation(arrays, 0, iteration)?;
        // Validate the committed bytes before exposing the new record.
        state.load()?;
        Ok(state)
    }

    fn path(&self, generation: u64, suffix: &str) -> PathBuf {
        self.root.join(format!("entry-{}-generation-{generation}.{suffix}", self.key))
    }

    fn header(&self, generation: u64, iteration: u32, hash: u64) -> [u64; 9] {
        [MAGIC, self.key, generation, u64::from(iteration), self.lengths[0] as u64,
            self.lengths[1] as u64, self.lengths[2] as u64, self.lengths[3] as u64, hash]
    }

    fn write_generation(&mut self, arrays: &[Vec<f32>; 4], generation: u64, iteration: u32) -> io::Result<()> {
        if std::array::from_fn::<_, 4, _>(|k| arrays[k].len()) != self.lengths {
            return Err(invalid("State shape changed"));
        }
        let temporary = self.path(generation, "pending");
        let destination = self.path(generation, "bin");
        if destination.exists() { return Err(invalid("Destination generation already exists")); }
        let mut writer = BufWriter::with_capacity(1024 * 1024,
            OpenOptions::new().write(true).create_new(true).open(&temporary)?);
        let hash = checksum(arrays);
        for v in self.header(generation, iteration, hash) { writer.write_all(&v.to_le_bytes())?; }
        for a in arrays { writer.write_all(bytes(a))?; }
        writer.flush()?;
        writer.get_ref().sync_all()?;
        drop(writer);
        // The dedicated directory has one writer; distinct generations never overwrite.
        fs::rename(&temporary, &destination)?;
        Ok(())
    }

    pub(super) fn payload_bytes(&self) -> u64 { self.lengths.iter().map(|n| *n as u64 * 4).sum() }

    pub(super) fn load(&self) -> io::Result<[Vec<f32>; 4]> {
        let mut file = File::open(self.path(self.generation, "bin"))?;
        if file.metadata()?.len() != HEADER_BYTES + self.payload_bytes() { return Err(invalid("Wrong file length")); }
        let expected = self.header(self.generation, self.iteration, self.hash);
        for v in expected {
            let mut b = [0u8; 8]; file.read_exact(&mut b)?;
            if u64::from_le_bytes(b) != v { return Err(invalid("Wrong identity, version, shape, iteration, generation or checksum header")); }
        }
        let mut arrays = std::array::from_fn(|k| vec![0f32; self.lengths[k]]);
        for a in &mut arrays {
            assert!(cfg!(target_endian = "little"));
            let target = unsafe { std::slice::from_raw_parts_mut(a.as_mut_ptr().cast::<u8>(), a.len() * 4) };
            file.read_exact(target)?;
        }
        if checksum(&arrays) != self.hash { return Err(invalid("Payload checksum mismatch")); }
        Ok(arrays)
    }

    pub(super) fn replace(&mut self, arrays: &[Vec<f32>; 4], iteration: u32) -> io::Result<()> {
        let next = self.generation.checked_add(1).ok_or_else(|| invalid("Generation overflow"))?;
        self.write_generation(arrays, next, iteration)?;
        let previous = self.path(self.generation, "bin");
        self.generation = next;
        self.iteration = iteration;
        self.hash = checksum(arrays);
        // Only this entry's former committed file is retired. Failure stops the test;
        // the new generation remains readable. No recursive cleanup or external paths.
        fs::remove_file(previous)?;
        Ok(())
    }
}

#[test]
fn rejects_damage_and_keeps_previous_generation_on_failed_write() {
    let root = PathBuf::from(std::env::var("GTO_SSD_STUDY_DIR").unwrap()).join("format-checks");
    fs::create_dir(&root).unwrap();
    let arrays = [vec![0., -0., 1.], vec![-2., 3.], vec![4.], vec![5., 6.]];
    let mut state = DiskState::create(&root, 99, &arrays, 17).unwrap();
    let path = state.path(0, "bin");
    let original = fs::read(&path).unwrap();
    for (label, offset) in [("identity", 8), ("generation", 16), ("iteration", 24), ("shape", 32), ("checksum", 64), ("payload", 73)] {
        let mut damaged = original.clone(); damaged[offset] ^= 1;
        fs::write(&path, damaged).unwrap();
        assert!(state.load().is_err(), "accepted {label} damage");
    }
    fs::write(&path, &original[..original.len() - 1]).unwrap();
    assert!(state.load().is_err());
    fs::write(&path, &original).unwrap();
    let pending = state.path(1, "pending");
    fs::write(&pending, b"simulate interrupted writer").unwrap();
    assert!(state.replace(&arrays, 18).is_err());
    assert_eq!(state.generation, 0);
    assert_eq!(fs::read(&path).unwrap(), original);
    assert_eq!(state.load().unwrap()[0][1].to_bits(), (-0f32).to_bits());
    fs::remove_file(pending).unwrap();
    state.replace(&arrays, 18).unwrap();
    assert_eq!(state.generation, 1);
    assert!(!path.exists());
    state.load().unwrap();
    println!("SSD_FORMAT_CHECKS {{\"passed\":true,\"checks\":9}}");
}
