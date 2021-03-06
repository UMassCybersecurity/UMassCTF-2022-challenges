from io import SEEK_CUR, SEEK_SET, BufferedReader
from itertools import chain, repeat
from re import compile
from struct import unpack
from sys import argv
from typing import Optional


class FileEntry:
    name: str
    offset: int
    length: int

    def __init__(self, name: str, offset: int, length: int) -> None:
        self.name = name
        self.offset = offset
        self.length = length

    def __str__(self) -> str:
        return f"File(\
name: {self.name}, offset: {self.offset}, length: {self.length})"

    def __repr__(self) -> str:
        return self.__str__()


class ArchiveTable:
    signature: bytes
    version: int
    count: int
    offset: int
    files: list[FileEntry]

    def __str__(self) -> str:
        return f"Archive(\
offset: {self.offset}, \
signature: {self.signature}, \
version: {self.version}, \
count: {self.count}, \
files: {self.files})"

    def __repr__(self) -> str:
        return self.__str__()


def destruct(fd: BufferedReader) -> Optional[ArchiveTable]:
    ret = ArchiveTable()

    base = fd.tell()
    ret.offset = base

    # File signature
    if (sig := fd.read(4)) != b"MyrA":
        return None
    ret.signature = sig

    ret.version, ret.count = unpack("<BQ", fd.read(9))
    ret.files = []
    for _ in range(ret.count):
        name = b""
        while len(byte := fd.read(1)) != 0 and byte[0] != 0x0:
            name += byte
        _, length, offset = unpack("3N", fd.read(24))
        entry = FileEntry(name, base + offset, length)
        ret.files.append(entry)

    return ret


def read_archive(filename: str) -> Optional[ArchiveTable]:
    with open(filename, "rb") as fd:
        while True:
            # print("Searching")
            while len(buffer := fd.read(2)) != 0 and buffer != b"\xFF\xD9":
                pass
            if len(buffer) != 2:
                break
            offset = fd.tell()

            print("Found possible at", offset)
            if (ret := destruct(fd)) is not None:
                return ret

            fd.seek(offset, SEEK_SET)
    print("Not the challenge file!")
    return None


def extract(archive_name: str, entries: list[FileEntry]) -> dict[bytes, bytes]:
    store = {}
    with open(archive_name, "rb") as fd:
        for entry in entries:
            fd.seek(entry.offset)
            store[entry.name] = fd.read(entry.length)
    return store


def xor_two_bytes(f1: bytes, f2: bytes):
    return bytes(map(lambda x: x[0] ^ x[1], zip(f1, f2)))


if __name__ == "__main__":
    if len(argv) > 1:
        target = argv[-1]
        frame = read_archive(target)
        if frame is not None:
            print(frame)
            unpacked = extract(target, frame.files)

            # Find key
            pattern = compile(rb"(.+)\1")
            with open(target, "rb") as fd:
                out = xor_two_bytes(fd.read(frame.offset), unpacked[b"penguin.jpg"])
            key = pattern.findall(out)[0]
            # print("Keyfound:", key)

            # Write to files
            for name, entry in unpacked.items():
                print("Extracted:", name)
                with open(name, "wb") as fd:
                    key_bytes = chain.from_iterable(repeat(tuple(key)))
                    fd.write(xor_two_bytes(entry, key_bytes))
