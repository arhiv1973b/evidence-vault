import json
import sys
from collections import Counter

def load_triggers(trigger_file):
    with open(trigger_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("cascade_triggers", [])

def analyze_logs(log_file, trigger_file, report_file):
    triggers = load_triggers(trigger_file)
    counters = Counter({"x_plus":0, "y_minus":0, "x_minus":0, "y_plus":0})

    with open(log_file, "r", encoding="utf-8-sig") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                msg = entry.get("message","")
                status = entry.get("status","")

                if any(trigger in msg for trigger in triggers):
                    counters["y_plus"] += 1
                elif status == "INSTITUTIONAL_DENIAL_EVENT":
                    counters["x_minus"] += 1
                else:
                    counters["x_plus"] += 1

                if "error" in msg.lower() or status.endswith("_EVENT"):
                    counters["y_minus"] += 1

            except json.JSONDecodeError:
                continue

    scenario_detection = counters["x_plus"] + counters["y_plus"]
    scenario_non_detection = counters["x_minus"] + counters["y_minus"]

    with open(report_file, "w", encoding="utf-8-sig") as out:
        out.write("=== Cascade Simulation Report ===\n")
        out.write(f"x+ (успехи): {counters['x_plus']}\n")
        out.write(f"y- (ошибки): {counters['y_minus']}\n")
        out.write(f"x- (ложные успехи): {counters['x_minus']}\n")
        out.write(f"y+ (компенсированные ошибки): {counters['y_plus']}\n\n")
        out.write(f"Сценарий обнаружения (x+ + y+): {scenario_detection}\n")
        out.write(f"Сценарий необнаружения (x- + y-): {scenario_non_detection}\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python analyze_logs.py <log_file> <trigger_file> <report_file>")
    else:
        analyze_logs(sys.argv[1], sys.argv[2], sys.argv[3])

