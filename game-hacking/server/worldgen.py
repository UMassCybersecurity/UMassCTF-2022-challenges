from base64 import b64encode, b64decode
from enum import Enum
import binascii
import hashlib
import json
import uuid

class Tile(Enum):
    NOTHING = 0
    GRASS   = 1

SECRET_KEY = b"1f_y0u'r3_r34d1ng_7h15,_1_h0p3_17'5_b3c4u53_y0u_unr0113d_MD5,_n07_b3c4u53_y0u_g07_RCE_0n_7h3_53rv3r"

def generate_grasslands():
    return [[Tile.GRASS.value] * 128] * 128


def generate_signature(blob):
    m = hashlib.md5()
    m.update(SECRET_KEY)
    m.update(blob)
    return binascii.hexlify(m.digest()).decode()


def validate_signature(signature, blob):
    m = hashlib.md5()
    m.update(SECRET_KEY)
    m.update(blob)
    return signature == binascii.hexlify(m.digest()).decode()

def generate_world():
    world = {
        "portals": [
            # { id: UUID(...), destination_world: "desert", destination_position: (x, y) }
        ],
        "tilemaps": {
            "grasslands": generate_grasslands(),
            # "desert"
            # "snowland"
        }
    }
    encoded = b64encode(json.dumps(world).encode())
    signature = generate_signature(encoded)
    return {
        "signature": signature,
        "blob": encoded.decode()
    }
