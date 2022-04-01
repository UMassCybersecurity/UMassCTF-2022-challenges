use rustc_hash::FxHashMap;
use std::{mem, slice};

fn compress(data: &[u8]) -> Vec<u32> {
    // Initialize a codebook that maps a byte sequence to a short index that can be used to to 
    // replace the bytesequence and thus compress the code. This is initialized with single 
    // character strings at the beginning.
    let mut code_book: FxHashMap<Vec<u8>, u32> = FxHashMap::default();
    for i in 0..=255 {
        code_book.insert(vec![i], i as u32);
    }

    let mut tracker = vec![data[0]];
    let mut compressed = Vec::new();

    for &b in &data[1..] {
        let mut cur = tracker.clone();
        cur.push(b);

        // Check if the code book contains tracker + the current byte, if so, extend extend the 
        // tracker with the current byte and keep increasing the combination
        if code_book.contains_key(&cur) {
            tracker.push(b);
        } else {
            // In this case we found a new entry that we can now add to the compressed data
            compressed.push(code_book[&tracker]);

            // Since this is a new entry, we insert this entry into the code book before resetting
            // the tracker
            code_book.insert(cur, code_book.len() as u32);
            tracker.clear();
            tracker.push(b);
        }
    }

    // If the final entry in the file was in the dictionary, we still need to push it to the 
    // compressed data at this point
    if !tracker.is_empty() {
        compressed.push(code_book[&tracker]);
    }

    compressed
}

fn decompress(data: &[u32]) -> Option<Vec<u8>> {
    // Initialize a codebook that maps an index to its corresponding byte sequence. This is used to
    // gradually build up a decoder while parsing the message and obtaining additional information. 
    // It is initialized with single character strings at the beginning.
    let mut code_book: FxHashMap<u32, Vec<u8>> = FxHashMap::default();
    for i in 0..=255 {
        code_book.insert(i, vec![i as u8]);
    }

    let mut tracker = code_book.get_mut(&data[0])?.to_vec();
    let mut decompressed = tracker.clone();

    for &b in &data[1..] {
        let entry = if code_book.contains_key(&b) {
            code_book[&b].clone()
        } else if b == code_book.len() as u32 {
            let mut entry = tracker.clone();
            entry.push(tracker[0]);
            entry
        } else {
            return None;
        };

        decompressed.extend_from_slice(&entry);

        tracker.push(entry[0]);
        code_book.insert(code_book.len() as u32, tracker);

        tracker = entry;
    }
    Some(decompressed)
}

fn main() {
    // Read chall, compress it and write it to chall_compressed
    let target = std::fs::read("./bin/chall").unwrap();

    let compressed = compress(&target);
    let compressed_u8: &[u8] = unsafe {
        slice::from_raw_parts(
            compressed.as_ptr() as *const u8,
            compressed.len() * mem::size_of::<u32>(),
        )
    };
    std::fs::write("./bin/chall_compressed", compressed_u8).unwrap();

    let new_compressed = std::fs::read("./bin/chall_compressed").unwrap();
    let compressed_u32: &[u32] = unsafe {
        slice::from_raw_parts(
            new_compressed.as_ptr() as *const u32,
            new_compressed.len() / mem::size_of::<u32>(),
        )
    };

    let decompressed = match decompress(&compressed_u32) {
        Some(data) => data,
        None => panic!("Error occured while decompressing"),
    };
    std::fs::write("./bin/chall_decompressed", decompressed).unwrap();
}
