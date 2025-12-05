import json

with open("alert_rules.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

enabled_rules = [r for r in rules if r.get("enabled", True)]

print("Total rules:", len(rules))
print("Enabled rules:", len(enabled_rules))

with open("alert_rules_enabled.json", "w", encoding="utf-8") as f:
    json.dump(enabled_rules, f, indent=2)

print("Saved filtered rules to alert_rules_enabled.json")
