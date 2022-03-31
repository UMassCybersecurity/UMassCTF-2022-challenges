import sys
TRANS = {
    '>': b'\x00',
    '<': b'\x01',
    '+': b'\x02',
    '-': b'\x03',
    '.': b'\x04',
    ',': b'\x05',
    '[': b'\x06',
    ']': b'\x07',
}
with open('challenge.bf') as code:
    for c in code.read():
        sys.stdout.buffer.write(TRANS[c])
sys.stdout.buffer.flush()
