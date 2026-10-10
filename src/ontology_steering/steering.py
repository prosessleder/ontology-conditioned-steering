"""Residual-output hooks, train-only vector estimation, and safe JSON artifacts."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import random
from pathlib import Path


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_value(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_jsonl(path):
    with Path(path).open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def estimate_direction(compatible, incompatible):
    """Equal-weight paired difference-of-means; all computation uses Python float."""
    if not compatible or len(compatible) != len(incompatible):
        raise ValueError("Require nonempty, equal-size contrastive endpoints")
    width = len(compatible[0])
    endpoints = compatible + incompatible
    if not width or any(len(row) != width for row in endpoints):
        raise ValueError("All activation endpoints must have equal nonzero dimension")
    if any(not math.isfinite(x) for row in endpoints for x in row):
        raise ValueError("Nonfinite activation")
    n = len(compatible)
    delta = [sum(p[j] - q[j] for p, q in zip(compatible, incompatible)) / n
             for j in range(width)]
    norm = math.sqrt(sum(x * x for x in delta))
    if norm <= 1e-12:
        raise ValueError("Degenerate contrastive direction; record this as a null estimator")
    scale = sum(math.sqrt(sum(x * x for x in row)) for row in endpoints) / (2 * n)
    return {"direction": [x / norm for x in delta], "difference_norm": norm,
            "activation_scale": scale, "n_pairs": n}


def random_direction(width, seed):
    rng = random.Random(seed)
    values = [rng.gauss(0, 1) for _ in range(width)]
    norm = math.sqrt(sum(x * x for x in values))
    return [x / norm for x in values]


def decoder_layers(model):
    """The pinned Qwen implementation exposes model.model.layers."""
    if not hasattr(model, "model") or not hasattr(model.model, "layers"):
        raise TypeError("Expected a Qwen-compatible model.model.layers ModuleList")
    return model.model.layers


def residual_tensor(output):
    # 4.57.1 Qwen2DecoderLayer returns Tensor; support legacy tuple for tests.
    return output[0] if isinstance(output, tuple) else output


@contextmanager
def capture_last_token(model, layers):
    """Capture decoder outputs before final RMSNorm, without changing activations."""
    values, handles = {}, []
    modules = decoder_layers(model)
    try:
        for index in layers:
            if not 0 <= index < len(modules):
                raise ValueError(f"Invalid zero-based layer {index}")
            def hook(_module, _inputs, output, index=index):
                h = residual_tensor(output)
                if h.ndim != 3 or h.shape[0] != 1:
                    raise ValueError("Capture requires batch size one")
                values[index] = h[0, -1, :].detach().float().cpu().tolist()
            handles.append(modules[index].register_forward_hook(hook))
        yield values
    finally:
        for handle in handles:
            handle.remove()


@contextmanager
def add_direction(model, layer, direction, alpha, scale):
    """Add at the final position of each forward, including prefill and cached decode.

    Only batch size one is supported. Prompt positions before the last are untouched.
    This is vector addition, not projection, erasure, a logit bias, or output filtering.
    """
    import torch
    modules = decoder_layers(model)
    if not 0 <= layer < len(modules):
        raise ValueError(f"Invalid zero-based layer {layer}")
    if not math.isfinite(alpha) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Finite alpha and positive finite scale required")
    unit = torch.tensor(direction, dtype=torch.float32)
    if unit.ndim != 1 or not torch.isfinite(unit).all() or not torch.isclose(
            torch.linalg.vector_norm(unit), torch.tensor(1.0), atol=1e-5):
        raise ValueError("Steering direction must be finite and unit-normalized")
    trace = []
    deltas = {}
    def hook(_module, _inputs, output):
        h = residual_tensor(output)
        if h.ndim != 3 or h.shape[0] != 1 or h.shape[-1] != unit.numel():
            raise ValueError("Intervention requires matching hidden size and batch size one")
        trace.append({"sequence_length": int(h.shape[1]), "position": int(h.shape[1] - 1)})
        if alpha == 0:
            return output
        key = (h.device, h.dtype)
        if key not in deltas:
            deltas[key] = unit.to(h.device, h.dtype) * (alpha * scale)
        changed = h.clone()
        changed[:, -1, :] = changed[:, -1, :] + deltas[key]
        return (changed,) + output[1:] if isinstance(output, tuple) else changed
    handle = modules[layer].register_forward_hook(hook)
    try:
        yield trace
    finally:
        handle.remove()
