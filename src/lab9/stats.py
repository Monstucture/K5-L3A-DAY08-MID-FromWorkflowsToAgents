"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError("human and judge must be the same length")
    tp = fp = fn = tn = 0
    for h, j in zip(human, judge):
        if h == POS and j == POS:
            tp += 1
        elif h != POS and j == POS:
            fp += 1
        elif h == POS and j != POS:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    m = confusion(human, judge)
    tp, fp, fn = m["tp"], m["fp"], m["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    if len(human) != len(judge):
        raise ValueError("human and judge must be the same length")
    m = confusion(human, judge)
    n = len(human)
    if n == 0:
        raise ValueError("empty sequences are undefined")
    tp, fp, fn, tn = m["tp"], m["fp"], m["fn"], m["tn"]
    p_o = (tp + tn) / n
    p_yes = ((tp + fp) / n) * ((tp + fn) / n)
    p_no = ((fn + tn) / n) * ((fp + tn) / n)
    p_e = p_yes + p_no
    if math.isclose(p_e, 1.0):
        raise ValueError("cohen_kappa undefined: judge is constant")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denom = sensitivity + specificity - 1
    if math.isclose(denom, 0.0):
        return 0.0
    corrected = (observed_rate + specificity - 1) / denom
    return min(1.0, max(0.0, corrected))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("a and b must have the same shape")
    if a.size == 0:
        raise ValueError("cannot bootstrap empty sequences")
    diff = float(a.mean() - b.mean())
    if np.allclose(a, b):
        return 0.0, 0.0, 0.0
    rng_obj = np.random.default_rng(rng)
    pairs = np.column_stack([a, b])
    samples = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng_obj.integers(0, a.size, size=a.size)
        samples[i] = pairs[idx, 0].mean() - pairs[idx, 1].mean()
    lo, hi = np.quantile(samples, [(1.0 - confidence) / 2.0, 1.0 - (1.0 - confidence) / 2.0])
    return diff, float(lo), float(hi)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    if not (isinstance(n, int) and isinstance(c, int) and isinstance(k, int)):
        raise ValueError("n, c, and k must be ints")
    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("invalid n, c, k")
    if k > n - c:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    if not (isinstance(n, int) and isinstance(c, int) and isinstance(k, int)):
        raise ValueError("n, c, and k must be ints")
    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("invalid n, c, k")
    if k > c:
        return 0.0
    return math.comb(c, k) / math.comb(n, k)
