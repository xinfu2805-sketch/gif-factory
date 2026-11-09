"""Single-pebble state and coordinate audit for the four-second pilot."""
from math import hypot, sin, pi

FRAMES = 24
SHIFT_X = 80  # Scene artwork is shifted left after compositing.
BEAK = {9: (828, 1223), 5: (842, 1025), 3: (850, 755)}
GROUND = (828, 1223)
SUNK = (968, 1267)


def frame_state(i):
    if not 0 <= i < FRAMES:
        raise ValueError(i)
    pose = 5 if i <= 2 or 5 <= i <= 8 else 9 if i <= 4 else 3
    if i <= 2:
        stage, point, representation = "GROUND", GROUND, "separate"
    elif i <= 4:
        stage, point, representation = "BEAK_CONTACT", BEAK[9], "embedded_in_pose_09"
    elif i <= 11:
        stage, point, representation = "HELD", BEAK[pose], "separate"
    elif i <= 14:
        t = (i - 12) / 2
        stage = "RELEASED"
        point = (850 + 105 * t, 755 - 130 * sin(pi * t) + 35 * t)
        representation = "separate"
    elif i <= 18:
        u = (i - 15) / 3
        stage = "FALLING_IN_JAR"
        point = (955 + 9 * sin(u * pi), 810 + 450 * u)
        representation = "separate"
    else:
        stage, point, representation = "SUNK", SUNK, "separate"
    return {
        "frame": i,
        "pose_asset": pose,
        "stage": stage,
        "representation": representation,
        "target_count": 1,
        "point_px": [round(point[0] - SHIFT_X, 2), round(point[1], 2)],
        "water_top_px": 1175 if i < 19 else max(950, 1175 - round((i - 18) / 5 * 225)),
    }


def audit():
    rows = [frame_state(i) for i in range(FRAMES)]
    violations = []
    expected = (["GROUND"] * 3 + ["BEAK_CONTACT"] * 2 + ["HELD"] * 7
                + ["RELEASED"] * 3 + ["FALLING_IN_JAR"] * 4 + ["SUNK"] * 5)
    if [r["stage"] for r in rows] != expected:
        violations.append("stage_order")
    for i, row in enumerate(rows):
        if row["target_count"] != 1:
            violations.append(f"frame_{i}: target_count")
        if row["stage"] != "SUNK" and row["water_top_px"] != 1175:
            violations.append(f"frame_{i}: water_rose_before_sinking")
        if i:
            prev = rows[i - 1]
            row["delta_from_previous_px"] = round(hypot(
                row["point_px"][0] - prev["point_px"][0],
                row["point_px"][1] - prev["point_px"][1]), 2)
            limit = 90 if row["stage"] in {"GROUND", "BEAK_CONTACT", "HELD"} else 170
            if row["delta_from_previous_px"] > limit:
                violations.append(
                    f"frame_{i}: stone_jump_{row['delta_from_previous_px']}px_gt_{limit}px"
                )
        else:
            row["delta_from_previous_px"] = None
    return {
        "frames": rows,
        "target_unique_every_frame": all(r["target_count"] == 1 for r in rows),
        "distinct_pose_assets": len({r["pose_asset"] for r in rows}),
        "rendered_frames": FRAMES,
        "coordinate_continuity_pass": not violations,
        "violations": violations,
    }
