import math
import numpy as np
from scipy.signal import resample_poly


def resample_block(block: np.ndarray, source_rate: int, target_rate: int, dtype=None) -> np.ndarray:
    if source_rate == target_rate:
        return block
    if block.size == 0:
        return block

    gcd = math.gcd(int(source_rate), int(target_rate))
    up = int(target_rate) // gcd
    down = int(source_rate) // gcd

    out = resample_poly(block.astype(np.float32, copy=False), up=up, down=down)

    if dtype is None:
        return out

    out_dtype = np.dtype(dtype)
    if np.issubdtype(out_dtype, np.integer):
        limits = np.iinfo(out_dtype)
        out = np.clip(np.rint(out), limits.min, limits.max)

    return out.astype(out_dtype, copy=False)
