//! Available system memory, cross-platform. The solver arenas are sized
//! against this so a laptop refuses a workstation-sized spot instead of
//! thrashing into OOM.

/// Currently available RAM in MB (Linux MemAvailable / Windows
/// ullAvailPhys). None on platforms without a probe.
pub fn avail_mem_mb() -> Option<f64> {
    imp::avail_mem_mb()
}

#[cfg(target_os = "linux")]
mod imp {
    pub fn avail_mem_mb() -> Option<f64> {
        let s = std::fs::read_to_string("/proc/meminfo").ok()?;
        s.lines()
            .find(|l| l.starts_with("MemAvailable:"))
            .and_then(|l| l.split_whitespace().nth(1))
            .and_then(|kb| kb.parse::<f64>().ok())
            .map(|kb| kb / 1024.0)
    }
}

#[cfg(windows)]
mod imp {
    // GlobalMemoryStatusEx from kernel32 — declared here to avoid pulling in
    // the windows-sys crate for one call.
    #[repr(C)]
    struct MemoryStatusEx {
        length: u32,
        memory_load: u32,
        total_phys: u64,
        avail_phys: u64,
        total_page_file: u64,
        avail_page_file: u64,
        total_virtual: u64,
        avail_virtual: u64,
        avail_extended_virtual: u64,
    }

    #[link(name = "kernel32")]
    extern "system" {
        fn GlobalMemoryStatusEx(buf: *mut MemoryStatusEx) -> i32;
    }

    pub fn avail_mem_mb() -> Option<f64> {
        let mut st = MemoryStatusEx {
            length: std::mem::size_of::<MemoryStatusEx>() as u32,
            memory_load: 0,
            total_phys: 0,
            avail_phys: 0,
            total_page_file: 0,
            avail_page_file: 0,
            total_virtual: 0,
            avail_virtual: 0,
            avail_extended_virtual: 0,
        };
        // SAFETY: `st` is a correctly sized, initialised MEMORYSTATUSEX.
        let ok = unsafe { GlobalMemoryStatusEx(&mut st) };
        (ok != 0).then(|| st.avail_phys as f64 / (1024.0 * 1024.0))
    }
}

#[cfg(not(any(target_os = "linux", windows)))]
mod imp {
    pub fn avail_mem_mb() -> Option<f64> {
        None
    }
}
