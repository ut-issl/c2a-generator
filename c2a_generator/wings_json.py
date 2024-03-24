import csv
import json
from pathlib import Path

def generate(bct_src: list, dest_path: Path) -> None:
    data = [
        {
            "obc_name": "MOBC",
            "bc": []
        }
    ]
    bcid = 0
    for src_path, bcid_base in bct_src:
        if bcid_base is not None:
            bcid = bcid_base

        with open(src_path, "r", encoding="utf-8") as src_file:
            reader = csv.reader(src_file)
            headers = next(reader)
            dict_reader = csv.DictReader(src_file, fieldnames=headers)

            for row in dict_reader:
                if not any(row):
                    continue
                if not row["name"].strip():
                    continue
                data[0]["bc"].append({"name": row["name"], "id": bcid})
                bcid += 1

    with open(dest_path, "w", encoding="utf-8") as dest_file:
        json.dump(data, dest_file, ensure_ascii=False, indent=2)
