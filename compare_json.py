import json
import re

def is_date_string(s):
    # Simple ISO 8601 and common date format check
    # if not isinstance(s, str):
    #     return False
    date_patterns = [
        r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
    ]
    return any(re.match(p, s) for p in date_patterns)

def get_type(val):
    if isinstance(val, str) and is_date_string(val):
        return "date"
    elif isinstance(val, bool):
        return "bool"
    elif isinstance(val, int):
        return "int"
    elif isinstance(val, float):
        return "float"
    elif isinstance(val, str):
        return "string"
    elif isinstance(val, list):
        return "list"
    elif isinstance(val, dict):
        return "dict"
    elif val is None:
        return "null"
    else:
        return type(val).__name__

class JSONDiff:
    def __init__(self):
        self.differences = []

    def add(self, kind, path, base_type, target_type, base_val=None, target_val=None):
        self.differences.append({
            "kind": kind,
            "path": path,
            "base_type": base_type,
            "target_type": target_type,
            "base_val": base_val,
            "target_val": target_val
        })

    def report(self):
        print("\n=== 1-by-1 JSON Format Compliance Report (Base vs Second JSON) ===\n")
        if not self.differences:
            print("✅ No format differences found. Second JSON fully complies with base JSON.")
        for diff in self.differences:
            kind = diff["kind"]
            path = diff["path"]
            base_type = diff["base_type"]
            target_type = diff["target_type"]
            base_val = diff["base_val"]
            target_val = diff["target_val"]
            if kind == "missing_in_target":
                print(f"❌ MISSING in second JSON at {path}: expected '{base_type}'")
            elif kind == "extra_in_target":
                print(f"⚠️ EXTRA in second JSON at {path}: found '{target_type}' (not in base)")
            elif kind == "type_mismatch":
                print(f"❌ TYPE MISMATCH at {path}: base '{base_type}' vs target '{target_type}'")
            elif kind == "list_length":
                print(f"⚠️ LIST LENGTH at {path}: base {base_val} vs target {target_val}")
        print("\n=== End of Report ===\n")

def compare_json_format(base, target, path="", diff=None):
    if diff is None:
        diff = JSONDiff()
    base_type = get_type(base)
    target_type = get_type(target)
    if base_type != target_type:
        diff.add("type_mismatch", path or "root", base_type, target_type)
        return diff

    if base_type == "dict":
        for key in base:
            new_path = f"{path}.{key}" if path else key
            if key not in target:
                diff.add("missing_in_target", new_path, get_type(base[key]), None)
            else:
                compare_json_format(base[key], target[key], new_path, diff)
        for key in target:
            if key not in base:
                new_path = f"{path}.{key}" if path else key
                diff.add("extra_in_target", new_path, None, get_type(target[key]))
    elif base_type == "list":
        if len(base) != len(target):
            diff.add("list_length", path, "list", "list", len(base), len(target))
        min_len = min(len(base), len(target))
        for i in range(min_len):
            compare_json_format(base[i], target[i], f"{path}[{i}]", diff)
    # No need to check value, only type/format
    return diff

def max_depth(obj, level=1):
    if isinstance(obj, dict):
        if not obj:
            return level
        return max(max_depth(v, level+1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return level
        return max(max_depth(i, level+1) for i in obj)
    else:
        return level

if __name__ == "__main__":
    # Load base and target from files
    with open("visit-sample.json") as f1, open("Petyerng-submission-jsonformatter.json") as f2:
        base = json.load(f1)
        target = json.load(f2)

    diff = compare_json_format(base, target)
    diff.report()

    print(f"Max depth (level) of base: {max_depth(base)}")
    print(f"Max depth (level) of target: {max_depth(target)}")