import csv
import json
from pathlib import Path
from typing import Optional


def csv_to_json(csv_file: Path):
    bc_dict = {}
    bc_dict = []
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Comment"]:
                continue
            elif row["Name"].startswith("BC_"):
                bc_name = row["Name"]
                bc_id = int(row["BCID"])
                bc_dict.append({"name": bc_name, "id": bc_id})

    return bc_dict


def generate(
    bct_src: list,
    dest_path: Path,
    aobc_csv_path: Optional[Path] = None,
    tobc_csv_path: Optional[Path] = None,
    mif_csv_path: Optional[Path] = None,
) -> None:
    data = []
    if aobc_csv_path:
        aobc_bc_dict = csv_to_json(aobc_csv_path)
        data.append({"obc_name": "AOBC", "bc": aobc_bc_dict, "el": [], "eh": []})
    if tobc_csv_path:
        tobc_bc_dict = csv_to_json(tobc_csv_path)
        data.append({"obc_name": "TOBC", "bc": tobc_bc_dict, "el": [], "eh": []})
    if mif_csv_path:
        mif_bc_dict = csv_to_json(mif_csv_path)
        data.append({"obc_name": "MIF", "bc": mif_bc_dict, "el": [], "eh": []})
    data.append({"obc_name": "MOBC", "bc": [], "el": [], "eh": []})
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
                data[-1]["bc"].append({"name": row["name"], "id": bcid})
                bcid += 1

    with open(dest_path, "w", encoding="utf-8") as dest_file:
        json.dump(data, dest_file, ensure_ascii=False, indent=2)
