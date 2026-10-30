//! Optional postflop compiler; the caller retains its original PTX cache/fallback.
use cudarc::{driver::sys, nvrtc::Ptx};
use libloading::os::windows::Library;
use std::{
    ffi::{c_char, c_int, c_void, CStr, CString, OsString},
    path::{Path, PathBuf},
    ptr,
};

type ProgramHandle = *mut c_void;
type Destroy = unsafe extern "C" fn(*mut ProgramHandle) -> c_int;
struct Program {
    handle: ProgramHandle,
    destroy: Destroy,
}
impl Program {
    fn finish(&mut self) -> Result<(), String> {
        let mut owned = std::mem::replace(&mut self.handle, ptr::null_mut());
        check("destroy", unsafe { (self.destroy)(&mut owned) })
    }
}
impl Drop for Program {
    fn drop(&mut self) {
        if !self.handle.is_null() {
            let result = self.finish();
            if let Err(error) = result {
                eprintln!("gpu: optional NVRTC13 cleanup: {error}");
            }
        }
    }
}
fn check(stage: &str, code: c_int) -> Result<(), String> {
    if code == 0 {
        Ok(())
    } else {
        Err(format!("NVRTC13 {stage} returned {code}"))
    }
}

#[link(name = "kernel32")]
extern "system" {
    fn GetModuleFileNameW(module: *mut c_void, buffer: *mut u16, size: u32) -> u32;
}
fn load_exact(path: &Path) -> Result<Library, String> {
    let library =
        unsafe { Library::new(path) }.map_err(|e| format!("load {}: {e}", path.display()))?;
    // Reconstitute the same owned reference immediately; no duplicated handle.
    let raw = library.into_raw();
    let library = unsafe { Library::from_raw(raw) };
    let mut buffer = vec![0u16; 32768];
    let size =
        unsafe { GetModuleFileNameW(raw as *mut c_void, buffer.as_mut_ptr(), buffer.len() as u32) };
    if size == 0 || size as usize >= buffer.len() {
        return Err("cannot verify private compiler module path".into());
    }
    use std::os::windows::ffi::OsStringExt;
    let actual = PathBuf::from(OsString::from_wide(&buffer[..size as usize]))
        .canonicalize()
        .map_err(|e| e.to_string())?;
    if actual != path.canonicalize().map_err(|e| e.to_string())? {
        return Err("private compiler module path differs".into());
    }
    Ok(library)
}
fn directory() -> Option<PathBuf> {
    let path = match std::env::var_os("GTOPEN_POSTFLOP_NVRTC13_DIR") {
        Some(value) => PathBuf::from(value),
        None => PathBuf::from(option_env!("CARGO_MANIFEST_DIR")?)
            .join("../../.cuda-nvrtc/nvidia/cu13/bin/x86_64"),
    };
    if !path.is_absolute() {
        return None;
    }
    let path = path.canonicalize().ok()?;
    if !path.join("nvrtc-builtins64_130.dll").is_file() || !path.join("nvrtc64_130_0.dll").is_file()
    {
        return None;
    }
    Some(path)
}

/// Only the supported target and private runtime opt in; all declines use the caller's original compiler.
pub(super) fn try_compile(arch: &str, source: &str) -> Option<Ptx> {
    if arch != "compute_120" {
        return None;
    }
    let directory = directory()?;
    let mut driver = 0;
    if unsafe { sys::cuDriverGetVersion(&mut driver) } != sys::CUresult::CUDA_SUCCESS
        || driver < 13000
    {
        return None;
    }
    match compile(&directory, arch, source) {
        Ok(ptx) => {
            eprintln!("gpu: postflop NVRTC13.0 runtime compiler");
            Some(ptx)
        }
        Err(error) => {
            eprintln!("gpu: optional postflop NVRTC13 declined: {error}; using original compiler");
            None
        }
    }
}

fn compile(directory: &Path, arch: &str, source: &str) -> Result<Ptx, String> {
    let source = CString::new(source).map_err(|e| e.to_string())?;
    let option = CString::new(format!("--gpu-architecture={arch}")).map_err(|e| e.to_string())?;
    let options = [option.as_ptr()];
    // Keep the explicitly bound dependency alive until the primary DLL closes.
    let builtins = load_exact(&directory.join("nvrtc-builtins64_130.dll"))?;
    let library = load_exact(&directory.join("nvrtc64_130_0.dll"))?;
    macro_rules! symbol {
        ($name:literal,$kind:ty) => {
            unsafe {
                *library
                    .get::<$kind>(concat!($name, "\0").as_bytes())
                    .map_err(|e| format!("{}: {e}", $name))?
            }
        };
    }
    let version = symbol!(
        "nvrtcVersion",
        unsafe extern "C" fn(*mut c_int, *mut c_int) -> c_int
    );
    let create = symbol!(
        "nvrtcCreateProgram",
        unsafe extern "C" fn(
            *mut ProgramHandle,
            *const c_char,
            *const c_char,
            c_int,
            *const *const c_char,
            *const *const c_char,
        ) -> c_int
    );
    let compile = symbol!(
        "nvrtcCompileProgram",
        unsafe extern "C" fn(ProgramHandle, c_int, *const *const c_char) -> c_int
    );
    let get_size = symbol!(
        "nvrtcGetPTXSize",
        unsafe extern "C" fn(ProgramHandle, *mut usize) -> c_int
    );
    let get_ptx = symbol!(
        "nvrtcGetPTX",
        unsafe extern "C" fn(ProgramHandle, *mut c_char) -> c_int
    );
    let log_size = symbol!(
        "nvrtcGetProgramLogSize",
        unsafe extern "C" fn(ProgramHandle, *mut usize) -> c_int
    );
    let get_log = symbol!(
        "nvrtcGetProgramLog",
        unsafe extern "C" fn(ProgramHandle, *mut c_char) -> c_int
    );
    let destroy = symbol!("nvrtcDestroyProgram", Destroy);
    let (mut major, mut minor) = (0, 0);
    check("version", unsafe { version(&mut major, &mut minor) })?;
    if (major, minor) != (13, 0) {
        return Err(format!("unexpected compiler version {major}.{minor}"));
    }
    let mut handle = ptr::null_mut();
    check("create", unsafe {
        create(
            &mut handle,
            source.as_ptr(),
            ptr::null(),
            0,
            ptr::null(),
            ptr::null(),
        )
    })?;
    if handle.is_null() {
        return Err("compiler returned a null program".into());
    }
    let mut program = Program { handle, destroy };
    let result = unsafe { compile(program.handle, options.len() as c_int, options.as_ptr()) };
    if result != 0 {
        let mut size = 0;
        check("log-size", unsafe { log_size(program.handle, &mut size) })?;
        if size == 0 || size > 1024 * 1024 {
            return Err(format!("compile returned {result}; invalid log size"));
        }
        let mut log = vec![0u8; size];
        check("log", unsafe {
            get_log(program.handle, log.as_mut_ptr().cast())
        })?;
        let log = CStr::from_bytes_with_nul(&log)
            .map_err(|e| e.to_string())?
            .to_string_lossy();
        return Err(format!("compile returned {result}: {log}"));
    }
    let mut size = 0;
    check("PTX-size", unsafe { get_size(program.handle, &mut size) })?;
    if size == 0 || size > 64 * 1024 * 1024 {
        return Err("invalid PTX size".into());
    }
    let mut image = vec![0u8; size];
    check("PTX", unsafe {
        get_ptx(program.handle, image.as_mut_ptr().cast())
    })?;
    let ptx = CStr::from_bytes_with_nul(&image)
        .map_err(|e| e.to_string())?
        .to_str()
        .map_err(|e| e.to_string())?
        .to_owned();
    program.finish()?;
    drop(program);
    library
        .close()
        .map_err(|e| format!("close compiler: {e}"))?;
    builtins
        .close()
        .map_err(|e| format!("close builtins: {e}"))?;
    Ok(Ptx::from_src(ptx))
}
