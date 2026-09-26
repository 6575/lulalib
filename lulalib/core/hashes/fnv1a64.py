from typing import Iterable

def hash_fnv1a_64(data: Iterable[int]):
    FNV_OFFSET_BASIS = 0xcbf29ce484222325
    FNV_PRIME = 0x100000001b3
    MASK_64 = 0xFFFFFFFFFFFFFFFF
    
    hash_value = FNV_OFFSET_BASIS
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * FNV_PRIME) & MASK_64
    
    return hash_value

