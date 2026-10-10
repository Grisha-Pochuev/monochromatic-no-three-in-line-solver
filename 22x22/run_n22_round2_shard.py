#!/usr/bin/env python3
"""One 5h40 shard of n=22 round 2: 225 gap survivors + 63 subcases of child 652.

Schedule: webchat/2026-10-10-round2/round2_schedule.json. Items:
  {"kind": "gap",  "child": c, "weight": w}        -> prove_upper_22x22_profile_child_gap.py
  {"kind": "c652", "r": r, "c": c, "a": a, "weight": w} -> prove_upper_22x22_child652_subcase.py
Round 1: one long attempt per item, budget = (time left) * w / (weight of items not yet tried),
so time freed by early closures flows to later items. Later rounds: survivors share the rest
with fresh seeds. Each attempt runs in its own subprocess with an RSS guard.
Only INFEASIBLE or an independently validated solution is final. UNKNOWN is not a proof.
"""
import argparse, json, os, signal, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
GAP = HERE / "prove_upper_22x22_profile_child_gap.py"
C652 = HERE / "prove_upper_22x22_child652_subcase.py"
SCHEDULE = HERE / "webchat/2026-10-10-round2/round2_schedule.json"
FINAL = ("INFEASIBLE", "FEASIBLE", "OPTIMAL")


def key(it):
    return f"gap-{it['child']:04d}" if it["kind"] == "gap" else f"c652-r{it['r']}-c{it['c']}-a{it['a']}"


def rss_mb(pid):
    try:
        out = subprocess.run(["ps", "-o", "rss=", "--ppid", str(pid), "-p", str(pid)], capture_output=True, text=True).stdout
        return sum(int(x) for x in out.split()) / 1024.0
    except Exception:
        return 0.0


def attempt(it, seconds, workers, seed, guard, outdir, tag):
    k = key(it); out = outdir / f"{k}-{tag}.json"; log = outdir / f"{k}-{tag}.log"
    if it["kind"] == "gap":
        cmd = [sys.executable, str(GAP), "--child-id", str(it["child"])]
    else:
        cmd = [sys.executable, str(C652), "--r", str(it["r"]), "--c", str(it["c"]), "--a", str(it["a"])]
    cmd += ["--seconds", str(seconds), "--workers", str(workers), "--seed", str(seed), "--output", str(out)]
    t0 = time.monotonic(); peak = 0.0; guard_hit = False
    with log.open("w") as fh:
        p = subprocess.Popen(cmd, cwd=HERE, stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
        while p.poll() is None:
            r = rss_mb(p.pid); peak = max(peak, r)
            if r > guard or time.monotonic() - t0 > seconds + 180:
                guard_hit = r > guard
                try: os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                break
            time.sleep(1.0)
        p.wait()
    if log.stat().st_size > 32768:
        tail = log.read_bytes()[-32768:]; log.write_bytes(b"[truncated]\n" + tail)
    rec = {"status": "TECHNICAL", "memory_guard": guard_hit}
    if out.exists():
        try: rec = json.loads(out.read_text())
        except Exception: pass
    rec.update({"item": it, "key": k, "tag": tag, "peak_rss_mb": peak, "wall_seconds": time.monotonic() - t0})
    out.write_text(json.dumps(rec, indent=1))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--total-seconds", type=float, default=20400)
    ap.add_argument("--min-seconds", type=float, default=60)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--memory-guard-mb", type=int, default=13000)
    ap.add_argument("--max-items", type=int, default=0)
    ap.add_argument("--seed-base", type=int, default=2026101100)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    items = json.loads(SCHEDULE.read_text())["assignments"][a.shard]["items"]
    if a.max_items: items = items[:a.max_items]
    a.output_dir.mkdir(parents=True, exist_ok=True)
    start = time.monotonic(); deadline = start + a.total_seconds
    final, best = {}, {}
    def left(): return deadline - time.monotonic() - 60
    def seed(it, rnd):
        h = it["child"] if it["kind"] == "gap" else 5000 + 100 * it["r"] + 10 * it["c"] + it["a"]
        return a.seed_base + 1000003 * rnd + 7 * h
    # round 1: weighted single long attempt
    untried = list(items)
    while untried:
        it = untried[0]
        if left() < a.min_seconds: break
        wsum = sum(x["weight"] for x in untried)
        budget = max(a.min_seconds, left() * it["weight"] / wsum)
        r = attempt(it, budget, a.workers, seed(it, 1), a.memory_guard_mb, a.output_dir, "R1")
        best[key(it)] = r; untried.pop(0)
        if r.get("status") in FINAL: final[key(it)] = r
    # later rounds: survivors share the remaining time, fresh seeds
    rnd = 1
    while True:
        open_items = [it for it in items if key(it) not in final and key(it) in best]
        if not open_items or left() < 2 * a.min_seconds: break
        rnd += 1
        for i, it in enumerate(open_items):
            if left() < a.min_seconds: break
            budget = left() / (len(open_items) - i)
            r = attempt(it, budget, a.workers, seed(it, rnd), a.memory_guard_mb, a.output_dir, f"R{rnd}")
            best[key(it)] = r
            if r.get("status") in FINAL: final[key(it)] = r
    res = {}
    for it in items:
        r = final.get(key(it)) or best.get(key(it)) or {"status": "NOT_STARTED"}
        res[key(it)] = {"item": it, "status": r["status"], "tag": r.get("tag"),
                        "elapsed_seconds": r.get("elapsed_seconds"), "solution": r.get("solution")}
    summary = {"shard": a.shard, "keys": [key(it) for it in items], "results": res,
               "wall_seconds": time.monotonic() - start}
    (a.output_dir / f"shard-{a.shard:02d}-summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))


if __name__ == "__main__":
    main()
