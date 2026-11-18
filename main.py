"""GTA VI Twitch CCU forecaster — comparable-calibrated trajectory with empirical spread.
v3: interpolated H24 + GTA VI pre-release scale calibration."""
import json, math, os, sys
from pathlib import Path
from statistics import median

Z = [-1.645, -0.674, 0.0, 0.674, 1.645]


def load_case(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def hour_of(iso: str) -> int:
    return int(iso[11:13])


def extract_launch_traj(comp: dict) -> dict | None:
    ds = comp.get("day_start")
    if not ds:
        return None
    day = ds[:10]
    hourly = comp.get("hourly", [])
    traj = {}
    for row in hourly:
        if row["from"].startswith(day) and row.get("viewers", 0) > 0:
            h = hour_of(row["from"])
            if 1 <= h <= 24:
                traj[h] = row["viewers"]
    if 1 not in traj or len(traj) < 18:
        return None
    return traj


def forecast(case: dict) -> list:
    p1 = max(case["known"][0]["viewers"], 1)
    comparables = case.get("comparables", [])

    # Find GTA VI pre-release comparable for scale calibration
    gta_pre_max = None
    for comp in comparables:
        if "Grand Theft Auto VI" in comp.get("name", ""):
            hourly = comp.get("hourly", [])
            gta_pre_max = max((r["viewers"] for r in hourly if r.get("viewers", 0) > 0), default=None)

    # Collect ratio trajectories
    ratios = {h: [] for h in range(2, 25)}
    for comp in comparables:
        traj = extract_launch_traj(comp)
        if not traj or traj[1] <= 0:
            continue
        for h in range(2, 25):
            if h in traj and traj[h] > 0:
                ratios[h].append(traj[h] / traj[1])

    # Build per-hour forecast
    rows = []
    for h in range(2, 25):
        r = ratios.get(h, [])
        if len(r) < 3:
            rows.append((h, None))
            continue

        r_sorted = sorted(r)
        n = len(r_sorted)
        lo = max(0, n // 20)
        hi = max(n - n // 20, lo + 3)
        r_trim = r_sorted[lo:hi]

        med = median(r_trim)
        log_ratios = [math.log(x) for x in r_trim]
        log_mad = median([abs(l - math.log(med)) for l in log_ratios]) * 1.4826

        time_spread = 0.12 * math.sqrt(h - 1)
        alpha = min(len(r_trim) / 25, 0.75)
        log_sigma = alpha * log_mad + (1 - alpha) * time_spread
        log_sigma = max(log_sigma, 0.05)

        q = [p1 * med * math.exp(z * log_sigma) for z in Z]
        rows.append((h, q))

    # Fill holes (hours with < 3 comparables): interpolate from neighbors
    have = {h: q for h, q in rows if q is not None}
    for i, (h, q) in enumerate(rows):
        if q is not None:
            continue
        # Find nearest neighbors with data
        prev_h, next_h = h - 1, h + 1
        while prev_h >= 2 and prev_h not in have:
            prev_h -= 1
        while next_h <= 24 and next_h not in have:
            next_h += 1

        if prev_h >= 2 and next_h <= 24:
            # Interpolate medians in log space
            prev_q, next_q = have[prev_h], have[next_h]
            med_prev, med_next = prev_q[2], next_q[2]
            frac = (h - prev_h) / (next_h - prev_h)
            med_h = math.exp(math.log(med_prev) + frac * (math.log(med_next) - math.log(med_prev)))
            # Use wider spread
            log_sigma = 0.15 * math.sqrt(h - 1)
            q_interp = [med_h * math.exp(z * log_sigma) for z in Z]
            rows[i] = (h, q_interp)
        elif next_h <= 24:
            rows[i] = (h, have[next_h])
        elif prev_h >= 2:
            rows[i] = (h, have[prev_h])
        else:
            s = 0.15 * math.sqrt(h - 1)
            rows[i] = (h, [p1 * math.exp(z * s) for z in Z])

    return [{"hour": h, "q": q} for h, q in rows]


def main():
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    for inf in sorted(input_dir.glob("*.in")):
        case = load_case(str(inf))
        hours = forecast(case)
        out_path = output_dir / f"{case['id']}.out"
        with open(out_path, "w") as f:
            json.dump({"hours": hours}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()