// Author: Jakob L. Kreuze <https://jakob.space>

use std::fs;

const CODE: &[u8] = include_bytes!("../source.bin");
const MAPSZ: usize = 4096 * 64;

unsafe fn map_chunk() -> *mut std::ffi::c_void {
    libc::mmap(
        std::ptr::null_mut(),
        MAPSZ,
        libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC,
        libc::MAP_ANONYMOUS | libc::MAP_PRIVATE,
        -1,
        0,
    )
}

fn main() {
    let ptr = unsafe { std::mem::transmute::<_, *mut u8>(map_chunk()) };
    let dest = unsafe { std::slice::from_raw_parts_mut(ptr, MAPSZ) };
    dest.fill(0xc3d);

    let mut off = 0;
    let mut stk = Vec::new();

    // sub rsp, 0x1000
    dest[off] = 0x48;
    dest[off + 1] = 0x81;
    dest[off + 2] = 0xec;
    dest[off + 3] = 0x00;
    dest[off + 4] = 0x30;
    dest[off + 5] = 0x00;
    dest[off + 6] = 0x00;
    off += 7;

    // mov rax, rsp
    dest[off] = 0x48;
    dest[off + 1] = 0x89;
    dest[off + 2] = 0xe0;
    off += 3;

    // mov rbx, 1000
    dest[off] = 0x48;
    dest[off + 1] = 0xc7;
    dest[off + 2] = 0xc3;
    dest[off + 3] = 0xe8;
    dest[off + 4] = 0x03;
    dest[off + 5] = 0x00;
    dest[off + 6] = 0x00;
    off += 7;

    // xor rcx, rcx
    dest[off] = 0x48;
    dest[off + 1] = 0x31;
    dest[off + 2] = 0xc9;
    off += 3;

    // mov [rax + rbx], rcx
    dest[off] = 0x48;
    dest[off + 1] = 0x89;
    dest[off + 2] = 0x0c;
    dest[off + 3] = 0x18;
    off += 4;

    // dec rbx
    dest[off] = 0x48;
    dest[off + 1] = 0xff;
    dest[off + 2] = 0xcb;
    off += 3;

    // jnz rel8
    dest[off] = 0x75;
    dest[off + 1] = 0xf9;
    off += 2;

    // mov rax, rsp
    dest[off] = 0x48;
    dest[off + 1] = 0x89;
    dest[off + 2] = 0xe0;
    off += 3;

    for byte in CODE.iter() {
        match byte {
            0x0 => {
                // inc rax
                dest[off] = 0x48;
                dest[off + 1] = 0xff;
                dest[off + 2] = 0xc0;
                off += 3;
            }
            0x1 => {
                // dec rax
                dest[off] = 0x48;
                dest[off + 1] = 0xff;
                dest[off + 2] = 0xc8;
                off += 3;
            }
            0x2 => {
                // inc byte ptr [rax]
                dest[off] = 0xfe;
                dest[off + 1] = 0x00;
                off += 2;
            }
            0x3 => {
                // dec byte ptr [rax]
                dest[off] = 0xfe;
                dest[off + 1] = 0x08;
                off += 2;
            }
            0x4 => {
                // mov rbx, rax
                dest[off] = 0x48;
                dest[off + 1] = 0x89;
                dest[off + 2] = 0xc3;
                // lea rsi, [rax]
                dest[off + 3] = 0x48;
                dest[off + 4] = 0x8d;
                dest[off + 5] = 0x30;
                // mov rax, 1
                dest[off + 6] = 0x48;
                dest[off + 7] = 0xc7;
                dest[off + 8] = 0xc0;
                dest[off + 9] = 0x01;
                dest[off + 10] = 0x00;
                dest[off + 11] = 0x00;
                dest[off + 12] = 0x00;
                // mov rdi, rax
                dest[off + 13] = 0x48;
                dest[off + 14] = 0x89;
                dest[off + 15] = 0xc7;
                // mov rdx, rax
                dest[off + 16] = 0x48;
                dest[off + 17] = 0x89;
                dest[off + 18] = 0xc2;
                // syscall
                dest[off + 19] = 0x0f;
                dest[off + 20] = 0x05;
                // mov rax, rbx
                dest[off + 21] = 0x48;
                dest[off + 22] = 0x89;
                dest[off + 23] = 0xd8;
                off += 24;
            }
            0x5 => {
                // mov rbx, rax
                dest[off] = 0x48;
                dest[off + 1] = 0x89;
                dest[off + 2] = 0xc3;
                // lea rsi, [rax]
                dest[off + 3] = 0x48;
                dest[off + 4] = 0x8d;
                dest[off + 5] = 0x30;
                // xor rax, rax
                dest[off + 6] = 0x48;
                dest[off + 7] = 0x31;
                dest[off + 8] = 0xc0;
                // xor rdi, rdi
                dest[off + 9] = 0x48;
                dest[off + 10] = 0x31;
                dest[off + 11] = 0xff;
                // mov rdx, 1
                dest[off + 12] = 0x48;
                dest[off + 13] = 0xc7;
                dest[off + 14] = 0xc2;
                dest[off + 15] = 0x01;
                dest[off + 16] = 0x00;
                dest[off + 17] = 0x00;
                dest[off + 18] = 0x00;
                // syscall
                dest[off + 19] = 0x0f;
                dest[off + 20] = 0x05;
                // mov rax, rbx
                dest[off + 21] = 0x48;
                dest[off + 22] = 0x89;
                dest[off + 23] = 0xd8;
                off += 24;
            }
            0x6 => {
                // Placeholder
                stk.push(off);
                off += 10;
            }
            0x7 => {
                let target = stk.pop().expect("unbalanced loop");
                // mov bl, [rax]
                dest[target] = 0x8a;
                dest[target + 1] = 0x18;
                // test bl, bl
                dest[target + 2] = 0x84;
                dest[target + 2 + 1] = 0xdb;
                // jz rel32
                let encoded = ((off + 10) as i32 - (target + 10) as i32).to_le_bytes();
                dest[target + 4] = 0x0f;
                dest[target + 4 + 1] = 0x84;
                dest[target + 4 + 2] = encoded[0];
                dest[target + 4 + 3] = encoded[1];
                dest[target + 4 + 4] = encoded[2];
                dest[target + 4 + 5] = encoded[3];
                // mov bl, [rax]
                dest[off] = 0x8a;
                dest[off + 1] = 0x18;
                off += 2;
                // test bl, bl
                dest[off] = 0x84;
                dest[off + 1] = 0xdb;
                off += 2;
                // jnz rel32
                let encoded = ((target + 10) as i32 - (off + 6) as i32).to_le_bytes();
                dest[off] = 0x0f;
                dest[off + 1] = 0x85;
                dest[off + 2] = encoded[0];
                dest[off + 3] = encoded[1];
                dest[off + 4] = encoded[2];
                dest[off + 5] = encoded[3];
                off += 6;
            }
            _ => panic!("Invalid bytecode"),
        }
    }

    // add rsp, 0x1000
    dest[off] = 0x48;
    dest[off + 1] = 0x81;
    dest[off + 2] = 0xc4;
    dest[off + 3] = 0x00;
    dest[off + 4] = 0x30;
    dest[off + 5] = 0x00;
    dest[off + 6] = 0x00;

    fs::write("/tmp/shellcode.bin", &dest).unwrap();

    let ptr = dest.as_mut_ptr();
    let func = unsafe { std::mem::transmute::<_, extern "C" fn()>(ptr) };
    func();
}
