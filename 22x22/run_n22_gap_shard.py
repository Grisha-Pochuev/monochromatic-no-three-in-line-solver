#!/usr/bin/env python3
"""One 5h50 shard of the n=22 gap run (727 children, complementary orientation).

Phase A: every child of the shard gets a short budget.
Phase B: the remaining wall time is split among phase-A survivors (repeated rounds
with fresh seeds while time remains). Each attempt runs in its own subprocess with
an RSS guard. Only INFEASIBLE or a validated solution is a final result.
"""
import argparse, json, os, signal, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ENGINE = HERE / "prove_upper_22x22_profile_child_gap.py"
SCHEDULE = HERE / "webchat/2026-10-10-farkas-gap/gap_schedule.json"

def rss_mb(pid):
    total = 0.0
    try:
        out = subprocess.run(["ps", "-o", "rss=", "--ppid", str(pid), "-p", str(pid)], capture_output=True, text=True).stdout
        total = sum(int(x) for x in out.split()) / 1024.0
    except Exception:
        pass
    return total

def attempt(child, seconds, workers, seed, guard, outdir, tag):
    out = outdir / f"child-{child:04d}-{tag}.json"; log = outdir / f"child-{child:04d}-{tag}.log"
    cmd = [sys.executable, str(ENGINE), "--child-id", str(child), "--seconds", str(seconds),
           "--workers", str(workers), "--seed", str(seed), "--output", str(out)]
    t0 = time.monotonic(); peak = 0.0; guard_hit = False
    with log.open("w") as fh:
        p = subprocess.Popen(cmd, cwd=HERE, stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
        while p.poll() is None:
            r = rss_mb(p.pid); peak = max(peak, r)
            if r > guard or time.monotonic() - t0 > seconds + 120:
                guard_hit = r > guard
                try: os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                break
            time.sleep(1.0)
        p.wait()
    # keep only the tail of the solver log
    if log.stat().st_size > 32768:
        tail = log.read_bytes()[-32768:]; log.write_bytes(b"[truncated]\n" + tail)
    rec = {"child_id": child, "status": "TECHNICAL", "memory_guard": guard_hit}
    if out.exists():
        try: rec = json.loads(out.read_text())
        except Exception: pass
    rec.update({"tag": tag, "peak_rss_mb": peak, "wall_seconds": time.monotonic() - t0})
    out.write_text(json.dumps(rec, indent=1))
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--total-seconds", type=float, default=20700)
    ap.add_argument("--phase-a-seconds", type=float, default=120)
    ap.add_argument("--max-seconds", type=float, default=3600)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--memory-guard-mb", type=int, default=13000)
    ap.add_argument("--max-children", type=int, default=0)
    ap.add_argument("--seed-base", type=int, default=2026101000)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    sched = json.loads(SCHEDULE.read_text())
    ids = sched["assignments"][a.shard]["ids"]
    if a.max_children: ids = ids[:a.max_children]
    a.output_dir.mkdir(parents=True, exist_ok=True)
    start = time.monotonic(); deadline = start + a.total_seconds
    final = {}; best = {}
    def remaining(): return deadline - time.monotonic()
    # phase A
    for c in ids:
        if remaining() < 60: break
        r = attempt(c, min(a.phase_a_seconds, remaining() - 30), a.workers, a.seed_base + c, a.memory_guard_mb, a.output_dir, "A")
        best[c] = r
        if r.get("status") in ("INFEASIBLE", "FEASIBLE", "OPTIMAL"): final[c] = r
    # phase B rounds
    rnd = 0
    while True:
        open_ids = [c for c in ids if c not in final]
        if not open_ids or remaining() < 120: break
        rnd += 1
        per = min(a.max_seconds * rnd, max(60.0, (remaining() - 60) / len(open_ids)))
        for i, c in enumerate(open_ids):
            left = remaining() - 60
            if left < 60: break
            budget = min(per, left / max(1, len(open_ids) - i)) if rnd > 1 else min(per, left)
            r = attempt(c, budget, a.workers, a.seed_base + 100000 * rnd + c, a.memory_guard_mb, a.output_dir, f"B{rnd}")
            best[c] = r
            if r.get("status") in ("INFEASIBLE", "FEASIBLE", "OPTIMAL"): final[c] = r
    summary = {"shard": a.shard, "children": ids,
               "results": {str(c): {"status": (final.get(c) or best.get(c) or {"status": "NOT_STARTED"})["status"],
                                    "tag": (final.get(c) or best.get(c) or {}).get("tag"),
                                    "elapsed_seconds": (final.get(c) or best.get(c) or {}).get("elapsed_seconds"),
                                    "solution": (final.get(c) or {}).get("solution")} for c in ids},
               "wall_seconds": time.monotonic() - start}
    (a.output_dir / f"shard-{a.shard:02d}-summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))

if __name__ == "__main__":
    main()
