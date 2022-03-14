const CODE: &[u8] = include_bytes!("../source.bin");

unsafe fn map_memory() -> *mut std::ffi::c_void {
    let mapsz = 4096;
    libc::mmap(
        std::ptr::null_mut(),
        mapsz,
        libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC,
        libc::MAP_ANONYMOUS | libc::MAP_PRIVATE,
        -1,
        0,
    )
}

fn compile_instruction(instruction: u8, dest: &mut [u8], i: usize) -> usize {
    match instruction {
        0x0 => {
            dest[i] = 0x40; // inc eax
            i + 1
        }
        0x1 => {
            dest[i] = 0x40; // dec eax
            i + 1
        }
        0x2 => {
            // inc [eax]
            dest[i] = 0xff;
            dest[i + 1] = 0x00;
            i + 2
        }
        0x3 => {
            // dec [eax]
            dest[i] = 0xff;
            dest[i + 1] = 0x08;
            i + 2
        }
        0x4 => {
            // mov rax, 0
            dest[i] = 0xff;
            // b800000000
            dest[i + 1] = 0x08;
            i + 2
        }
        _ => unimplemented!(),
    }
}

fn main() {
    let ptr = unsafe { map_memory() };
    let ptr = unsafe { std::mem::transmute::<_, *mut u8>(ptr) };
    let dest = unsafe { std::slice::from_raw_parts_mut(ptr, 4096) };
    println!("{:?}", dest);
}
