"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems: list[str] = []
    for metric_id, value in (pr.get("metrics") or {}).items():
        try:
            if isinstance(value, (int, float)) and not math.isfinite(float(value)):
                problems.append(f"metric {metric_id} is NaN/inf")
        except (TypeError, ValueError):
            pass

    manifest = pr.get("manifest") or {}
    item_count = int(manifest.get("items", 0) or 0)
    seeds = manifest.get("seeds") or []
    expected_rows = item_count * len(seeds)
    rows = pr.get("rows") or []
    if len(rows) != expected_rows:
        problems.append(f"row count {len(rows)} != manifest {item_count} x {len(seeds)}")

    key_counts: dict[tuple[str | None, int | None], int] = {}
    for row in rows:
        key = (row.get("item_id"), row.get("seed"))
        key_counts[key] = key_counts.get(key, 0) + 1
    duplicates = sorted(k for k, c in key_counts.items() if c > 1)
    if duplicates:
        problems.append(f"duplicate item/seed rows: {duplicates}")

    base_rows = base.get("rows") or []
    base_keys = {(r.get("item_id"), r.get("seed")) for r in base_rows}
    pr_keys = {(r.get("item_id"), r.get("seed")) for r in rows}
    if base_keys and pr_keys != base_keys:
        problems.append("PR item/seed set differs from baseline")

    if pr.get("evaluator_failures"):
        problems.append("evaluator_failures non-empty")

    row_metric_ids = {
        m["id"] for m in spec.get("metrics", [])
        if m.get("grader") != "lab8.metrics.summarize"
    }
    for row in rows:
        for metric_id in sorted(row_metric_ids):
            if row.get(metric_id) is None:
                problems.append(f"row {row.get('item_id')}@{row.get('seed')} missing {metric_id}")

    if base_spec is not None:
        base_metrics = {m["id"]: m for m in base_spec.get("metrics", [])}
        for metric in spec.get("metrics", []):
            mid = metric["id"]
            base_metric = base_metrics.get(mid)
            if base_metric is None:
                problems.append(f"metric {mid} disappeared from the ratchet spec")
                continue
            bth = base_metric.get("threshold", {})
            mth = metric.get("threshold", {})
            if "max" in bth and "max" in mth and mth["max"] > bth["max"]:
                problems.append(f"threshold max for {mid} loosened: {mth['max']} > {bth['max']}")
            if "min" in bth and "min" in mth and mth["min"] < bth["min"]:
                problems.append(f"threshold min for {mid} loosened: {mth['min']} < {bth['min']}")
            if base_metric.get("blocking") and not metric.get("blocking"):
                problems.append(f"metric {mid} stopped blocking")
            if base_metric.get("no_significant_drop") and not metric.get("no_significant_drop"):
                problems.append(f"metric {mid} dropped no_significant_drop")

        base_slices = {s["name"]: s for s in base_spec.get("slices", [])}
        for slice_def in spec.get("slices", []):
            name = slice_def["name"]
            base_slice = base_slices.get(name)
            if base_slice is None:
                problems.append(f"slice {name} disappeared from the ratchet spec")
                continue
            if base_slice.get("blocking") and not slice_def.get("blocking"):
                problems.append(f"slice {name} stopped blocking")
            if "min" in base_slice and "min" in slice_def and slice_def["min"] < base_slice["min"]:
                problems.append(f"slice {name} floor loosened: {slice_def['min']} < {base_slice['min']}")
            if base_slice.get("no_significant_drop") and not slice_def.get("no_significant_drop"):
                problems.append(f"slice {name} dropped no_significant_drop")

    base_slices_by_item = {}
    for row in base_rows:
        base_slices_by_item[row.get("item_id")] = sorted(row.get("slices") or [])
    pr_slices_by_item = {}
    for row in rows:
        pr_slices_by_item[row.get("item_id")] = sorted(row.get("slices") or [])
    for item_id in sorted(set(base_slices_by_item) | set(pr_slices_by_item)):
        if base_slices_by_item.get(item_id) != pr_slices_by_item.get(item_id):
            problems.append(f"slice tags changed for item {item_id}")

    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked: set[str] = set()
    lines: list[str] = []
    for s in spec.get("slices", []):
        name = s["name"]
        metric = s["metric"]
        pr_vals = per_item(pr, metric, name)
        if not pr_vals:
            continue
        avg = sum(pr_vals.values()) / len(pr_vals)
        line = f"  slice:{name}/{metric} {avg:.3f}"
        if s.get("min") is not None and avg < s["min"]:
            blocked.add(f"slice:{name}/{metric}")
            line += f" < {s['min']}"
        base_vals = per_item(base, metric, name)
        if s.get("no_significant_drop"):
            keys = sorted(set(pr_vals) & set(base_vals))
            if keys:
                d, lo, hi = stats.paired_bootstrap([pr_vals[k] for k in keys], [base_vals[k] for k in keys])
                line += f" Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
                if hi < 0:
                    blocked.add(f"slice:{name}/{metric}")
        lines.append(line)
    return sorted(blocked), lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
