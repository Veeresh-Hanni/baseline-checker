import json

with open("src/baseline_checker/config/baseline_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(type(data))  # dict or list?
print(list(data.keys())[:5] if isinstance(data, dict) else data[:5])
