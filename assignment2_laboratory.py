"""Assignment 2: Algorithm Analysis - Laboratory Works (Python 3).

Both laboratory exercises from the uploaded assignment are included.
No third-party libraries are required; graphs are saved as SVG files and
measurements as CSV files in the assignment2_lab_outputs folder.

Timing values are MEDIANS of 5 independent trials (seconds per call).
Input generation and correctness checks happen OUTSIDE timed sections.
"""

import csv
import html
import math
import platform
import random
import statistics
import sys
import time
from pathlib import Path


TRIALS = 5
SEED = 2026
OUTPUT_DIR = Path(__file__).resolve().parent / "assignment2_lab_outputs"


# --------------------- SHARED BENCHMARK UTILITIES ---------------------

def benchmark(function, *args):
    """Return (median seconds per call, calls per trial).

    Multiple calls are grouped into each trial to reduce timer-resolution
    problems for very fast operations. Python call/loop overhead remains,
    especially for constant-time indexing and logarithmic search.
    """
    repeats = 1
    while True:
        start = time.perf_counter()
        for _ in range(repeats):
            function(*args)
        elapsed = time.perf_counter() - start
        if elapsed >= 0.015 or repeats >= 262144:
            break
        repeats *= 2

    timings = []
    for _ in range(TRIALS):
        start = time.perf_counter()
        for _ in range(repeats):
            function(*args)
        elapsed = time.perf_counter() - start
        timings.append(elapsed / repeats)

    return statistics.median(timings), repeats


def save_csv(filename, headers, rows):
    path = OUTPUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)
    print("Saved:", path)


def save_svg(filename, title, series, ylabel="Time (milliseconds)"):
    """Draw a line chart using only Python's standard library.

    series: list of (label, [(n, y), ...]) where y is measured chart units.
    The resulting SVG file opens in any modern browser.
    """
    width, height = 900, 540
    left, right, top, bottom = 95, 35, 78, 88
    chart_w = width - left - right
    chart_h = height - top - bottom
    all_points = [point for _, points in series for point in points]
    if not all_points:
        return

    x_min = min(n for n, _ in all_points)
    x_max = max(n for n, _ in all_points)
    y_max = max(value for _, value in all_points)
    if x_max == x_min:
        x_max += 1
    if y_max <= 0:
        y_max = 1
    y_max *= 1.12

    def px(x):
        return left + (x - x_min) * chart_w / (x_max - x_min)

    def py(y):
        return top + chart_h - y * chart_h / y_max

    colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="35" text-anchor="middle" '
        f'font-family="Arial" font-size="21" font-weight="bold">{html.escape(title)}</text>',
    ]
    for step in range(6):
        value = y_max * step / 5
        y = py(value)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" '
                     f'x2="{width-right}" y2="{y:.2f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{left - 12}" y="{y+4:.2f}" text-anchor="end" '
                     f'font-family="Arial" font-size="12">{value:.3g}</text>')
    x_values = sorted({n for n, _ in all_points})
    if len(x_values) > 8:
        x_values = [x_values[round(i * (len(x_values) - 1) / 7)] for i in range(8)]
    for x in x_values:
        parts.append(f'<text x="{px(x):.2f}" y="{height - bottom + 24}" '
                     f'text-anchor="middle" font-family="Arial" font-size="12">{x}</text>')
    parts.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{height-bottom}" stroke="#111827" stroke-width="2"/>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" '
        f'y2="{height-bottom}" stroke="#111827" stroke-width="2"/>',
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" '
        'font-family="Arial" font-size="15">Input size n</text>',
        f'<text x="22" y="{height/2}" text-anchor="middle" '
        f'transform="rotate(-90 22 {height/2})" font-family="Arial" '
        f'font-size="15">{html.escape(ylabel)}</text>',
    ])
    for index, (label, points) in enumerate(series):
        color = colors[index % len(colors)]
        coords = " ".join(f"{px(x):.2f},{py(y):.2f}" for x, y in points)
        parts.append(f'<polyline points="{coords}" fill="none" '
                     f'stroke="{color}" stroke-width="2.5"/>')
        for x, y in points:
            parts.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" '
                         f'r="4" fill="{color}"/>')
        lx, ly = left + 12 + (index % 2) * 340, top + 16 + (index // 2) * 25
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+24}" '
                     f'y2="{ly}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx+32}" y="{ly+4}" font-family="Arial" '
                     f'font-size="12">{html.escape(label)}</text>')
    parts.append("</svg>")
    path = OUTPUT_DIR / filename
    path.write_text("\n".join(parts), encoding="utf-8")
    print("Saved:", path)


def setup_text():
    return (f"Python version: {sys.version.split()[0]}\n"
            f"Platform: {platform.platform()}\n"
            f"Processor: {platform.processor() or 'not reported'}\n"
            f"Timing clock: time.perf_counter()\n"
            f"Reported statistic: MEDIAN of {TRIALS} timed trials\n"
            f"Units: seconds per algorithm call (tables also show milliseconds)\n"
            f"Random seed: {SEED}\n"
            f"Input generation/validation: outside timed sections\n"
            f"Repeated calls per trial: calibrated to about 15 ms or more, "
            f"except the largest cases\n")


# ---------------- LAB WORK 1: ALGORITHMIC GROWTH RATES ----------------

def list_indexing(values, index):
    return values[index]                            # O(1)


def binary_search(values, target):
    lo, hi = 0, len(values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                                       # O(log n)


def linear_search(values, target):
    for i, value in enumerate(values):
        if value == target:
            return i
    return -1                                       # O(n)


def merge_sort(values):
    if len(values) <= 1:
        return values[:]
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result                                  # O(n log n)


def pair_counter(n):
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    return count                                   # O(n^2)


def subset_enumeration(n):
    count = 0
    for mask in range(1 << n):
        count += 1     # each mask represents one subset
    return count                                   # O(2^n)


def growth_value(kind, n):
    return {
        "constant": lambda: 1,
        "logarithmic": lambda: math.log2(n),
        "linear": lambda: n,
        "nlogn": lambda: n * math.log2(n),
        "quadratic": lambda: n * n,
        "exponential": lambda: 2 ** n,
    }[kind]()


def lab1_cases():
    """Create reproducible input once per (algorithm, n), outside timing."""
    configurations = [
        ("List indexing", "constant", [1000, 10000, 100000, 300000]),
        ("Binary search", "logarithmic", [256, 1024, 4096, 16384, 65536]),
        ("Linear search", "linear", [200, 500, 1000, 2000, 4000, 8000]),
        ("Merge sort", "nlogn", [200, 500, 1000, 2000, 4000, 8000]),
        ("Pair counter", "quadratic", [100, 200, 400, 800, 1200]),
        ("Subset enumeration", "exponential", [8, 10, 12, 14, 16]),
    ]
    for name, kind, sizes in configurations:
        for n in sizes:
            rng = random.Random(SEED + n)
            if name == "List indexing":
                values = list(range(n))
                function, args = list_indexing, (values, n // 2)
                assert function(*args) == n // 2
            elif name == "Binary search":
                values = list(range(0, 2 * n, 2))
                function, args = binary_search, (values, 2 * n + 1)
                assert function(*args) == -1
            elif name == "Linear search":
                values = list(range(n))
                function, args = linear_search, (values, -1)
                assert function(*args) == -1
            elif name == "Merge sort":
                values = [rng.randint(-100000, 100000) for _ in range(n)]
                function, args = merge_sort, (values,)
                assert function(*args) == sorted(values)
            elif name == "Pair counter":
                function, args = pair_counter, (n,)
                assert function(*args) == n * (n - 1) // 2
            else:
                function, args = subset_enumeration, (n,)
                assert function(*args) == 2 ** n
            yield name, kind, n, function, args


def run_lab1():
    print("\n=== LAB WORK 1: BENCHMARKING ALGORITHMIC GROWTH RATES ===")
    print(setup_text())
    data = {}
    csv_rows = []
    for name, kind, n, function, args in lab1_cases():
        seconds, repeats = benchmark(function, *args)
        data.setdefault(name, {"kind": kind, "points": []})["points"].append((n, seconds))
        csv_rows.append([name, kind, n, repeats, round(seconds * 1000, 8),
                         f"{seconds/n:.12g}",
                         f"{seconds/(n*math.log2(n)):.12g}",
                         f"{seconds/(n*n):.12g}",
                         f"{seconds/growth_value(kind, n):.12g}"])
        print(f"{name:21s} n={n:7d}  median={seconds * 1000:11.6f} ms")

    save_csv("lab1_timing_data.csv",
             ["algorithm", "growth_class", "n", "calls_per_trial", "median_ms",
              "T_over_n_seconds", "T_over_nlog2n_seconds", "T_over_n2_seconds",
              "T_over_expected_growth_seconds"], csv_rows)

    for name, record in data.items():
        save_svg("lab1_" + name.lower().replace(" ", "_") + ".svg",
                 name + " - Execution time vs n",
                 [(name, [(n, t * 1000) for n, t in record["points"]])])

    theory = {"constant": "O(1)", "logarithmic": "O(log n)",
              "linear": "O(n)", "nlogn": "O(n log n)",
              "quadratic": "O(n^2)", "exponential": "O(2^n)"}
    notes = {
        "List indexing": "Call and loop overhead hide the extremely small O(1) work.",
        "Binary search": "Only a few comparisons; overhead/cache effects can mask log n growth.",
        "Linear search": "Full unsuccessful scan; Python iteration overhead matters.",
        "Merge sort": "Recursion, slicing and allocation add costs beyond comparisons.",
        "Pair counter": "Python nested-loop overhead affects constants; n kept moderate.",
        "Subset enumeration": "Inputs kept <=16; exponential work becomes impractical quickly.",
    }
    lines = ["LAB 1 - ALGORITHMIC GROWTH BENCHMARK", setup_text(),
             "Input characteristics:",
             "Indexing: sequential list, middle position. Binary search: sorted even integers,",
             "  target larger than maximum (unsuccessful search).",
             "Linear search: sequential list, absent target (-1; worst case).",
             "Merge sort: seeded uniformly random integers, including duplicates/negatives.",
             "Pair counter: count each i<j pair (n(n-1)/2).",
             "Subset enumeration: visit all 2^n subset bitmasks; only small n.", "",
             "Algorithm             Expected    Measured growth (end/start)   Model ratio",
             "-" * 78]
    comparison_rows = []
    for name, record in data.items():
        points = record["points"]
        kind = record["kind"]
        n0, t0 = points[0]
        n1, t1 = points[-1]
        observed_ratio = t1 / t0 if t0 else float("nan")
        model_ratio = growth_value(kind, n1) / growth_value(kind, n0)
        lines.append(f"{name:21s} {theory[kind]:10s} {observed_ratio:12.2f}x"
                     f" {model_ratio:20.2f}x")
        comparison_rows.append([name, theory[kind], f"{observed_ratio:.2f}x "
                                f"(n={n0} to {n1})", notes[name]])
    lines.extend(["", "EXPERIMENTAL LIMITATIONS / DISCUSSION:",
                  "1. Interpreter overhead, function calls and timer noise dominate tiny n.",
                  "2. Constant factors and lower-order terms delay asymptotic behaviour.",
                  "3. Cache, memory allocation, background tasks and processor load vary.",
                  "4. Different algorithms have different SAFE input-size ranges.",
                  "5. Median of 5 repeated trials reduces, but cannot remove, variability.",
                  "6. Theoretical bounds are asymptotic; observed ratios need not equal model ratios.",
                  "7. Each CSV includes T/n, T/(n log2 n), T/n^2 and T/model columns.",
                  "   A stable T/model at sufficiently large n supports a growth hypothesis."])
    (OUTPUT_DIR / "lab1_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_csv("lab1_comparison_table.csv",
             ["algorithm", "theoretical_bound", "measured_trend", "experimental_limitations"],
             comparison_rows)
    print("Saved:", OUTPUT_DIR / "lab1_report.txt")


# -------- LAB WORK 2: PREFIX AVERAGES (QUADRATIC VS LINEAR) ---------

def prefix_average1(values):
    """O(n^2): sum each prefix from scratch; empty list -> []."""
    averages = []
    for i in range(len(values)):
        total = 0
        for j in range(i + 1):
            total += values[j]
        averages.append(total / (i + 1))
    return averages


def prefix_average2(values):
    """O(n): update one running sum; empty list -> []."""
    averages = []
    running_sum = 0
    for i, value in enumerate(values):
        running_sum += value
        averages.append(running_sum / (i + 1))
    return averages


def validate_prefix_averages():
    test_cases = {
        "empty": [], "singleton": [7],
        "positive": [1, 2, 3, 4, 5],
        "negative": [-9, -4, -2, -1],
        "mixed": [-3, 0, 10, -5, 2, 4],
        "floating-point": [0.1, -0.2, 0.3, -0.4, 0.5],
    }
    for label, values in test_cases.items():
        result1 = prefix_average1(values)
        result2 = prefix_average2(values)
        assert len(result1) == len(result2) == len(values)
        assert all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                   for a, b in zip(result1, result2)), label
        print(f"PASS: {label:14s} -> {result2}")
    return len(test_cases)


def run_lab2():
    print("\n=== LAB WORK 2: PREFIX AVERAGES ===")
    print(setup_text())
    tests_count = validate_prefix_averages()
    sizes = [100, 250, 500, 1000, 2000, 3000]
    results = []
    print("\n  n     quadratic (ms)    linear (ms)    speedup")
    for n in sizes:
        rng = random.Random(SEED + n)
        values = [rng.randint(-1000, 1000) for _ in range(n)]
        # Verify before measuring, never inside the timed block.
        a = prefix_average1(values)
        b = prefix_average2(values)
        assert a == b, f"Mismatch at n={n}"
        t1, reps1 = benchmark(prefix_average1, values)
        t2, reps2 = benchmark(prefix_average2, values)
        speedup = t1 / t2 if t2 else float("inf")
        results.append((n, t1, t2, reps1, reps2))
        print(f"{n:5d}    {t1*1000:14.6f}    {t2*1000:11.6f}    {speedup:7.2f}x")

    save_csv("lab2_prefix_averages_timing.csv",
             ["n", "prefix_average1_median_ms", "prefix_average2_median_ms",
              "quadratic_calls_per_trial", "linear_calls_per_trial", "speedup",
              "T1_over_n2_seconds", "T2_over_n_seconds"],
             [[n, f"{t1*1000:.9f}", f"{t2*1000:.9f}", reps1, reps2,
               f"{t1/t2:.4f}", f"{t1/(n*n):.12g}", f"{t2/n:.12g}"]
              for n, t1, t2, reps1, reps2 in results])
    save_svg("lab2_prefix_averages.svg", "Prefix averages - Execution time vs n", [
        ("prefix_average1 - O(n^2)", [(n, t1 * 1000) for n, t1, _, _, _ in results]),
        ("prefix_average2 - O(n)", [(n, t2 * 1000) for n, _, t2, _, _ in results]),
    ])
    save_svg("lab2_normalized.svg", "Normalized prefix-average timings", [
        ("T1 / n^2", [(n, t1 / (n*n)) for n, t1, _, _, _ in results]),
        ("T2 / n", [(n, t2 / n) for n, _, t2, _, _ in results]),
    ], ylabel="Seconds per growth unit")

    threshold_n = next((n for n, t1, t2, _, _ in results if t1 >= 1.5*t2), None)
    threshold_desc = (f"n={threshold_n} (first tested n with >=1.5x speedup)"
                      if threshold_n is not None else "not reached in tested range")
    report = f"""LAB 2 - PREFIX AVERAGES
{setup_text()}
Validation: {tests_count} cases passed (empty, singleton, positive, negative, mixed, floating-point).
Empty-input handling: both functions return [].
Input characteristics: deterministic mixed signed integers [-1000, 1000], seed SEED+n.
Input creation, correctness checking and validation are outside timed regions.

OPERATION COUNTS AND DERIVATION:
prefix_average1: For prefix i (1-based), i additions are performed.
  Total additions = sum(i, i=1..n) = n(n+1)/2 = (n^2+n)/2.
  Therefore the running time is Theta(n^2).
prefix_average2: Exactly one addition per input element, total n additions.
  Therefore the running time is Theta(n).
Both methods return n averages and use O(n) output memory.
The improved method also uses O(1) extra working memory besides its output.

NUMERICAL PRECISION:
Both implementations add values left-to-right, so the same inputs normally
produce equal results; floating-point addition may still have rounding error
relative to exact mathematical arithmetic. Tests compare floats with math.isclose.
For precision-sensitive numeric applications, consider math.fsum for each prefix
(but that changes the implementation and its cost).

MEASURED SPEED COMPARISON:
First tested input size with a clearly measurable speed advantage: {threshold_desc}.
Ratios depend on interpreter overhead, list allocation, CPU load, cache,
and n. The expected growth rates are Theta(n^2) and Theta(n), not exact times.
CSV and SVG plots provide the empirical comparison and normalized timings.
"""
    path = OUTPUT_DIR / "lab2_report.txt"
    path.write_text(report, encoding="utf-8")
    print("Saved:", path)


# ------------------------------ MAIN MENU -----------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        print("\n========== ASSIGNMENT 2 - LABORATORY WORKS ==========")
        print("1. Lab Work 1 - Benchmark algorithmic growth rates")
        print("2. Lab Work 2 - Prefix averages (O(n^2) vs O(n))")
        print("3. Run both labs")
        print("0. Exit")
        choice = input("Enter your choice (0-3): ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            run_lab1()
        elif choice == "2":
            run_lab2()
        elif choice == "3":
            run_lab1()
            run_lab2()
        else:
            print("Invalid choice. Please enter 0, 1, 2 or 3.")
        if choice in ("1", "2", "3"):
            print("\nAll files are saved in:", OUTPUT_DIR)
            print("Open any .svg graph in your browser.")


if __name__ == "__main__":
    main()
