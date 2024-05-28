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
            if row[headers[0]].startswith('#'):
                continue
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
    cmd_src: Optional[Path] = None,
    el_src: Optional[Path] = None,
    eh_src: Optional[Path] = None,
    eh_base_id: int = 0,
) -> None:
    data = []
    el_list = []
    eh_list = []
    eh_id = eh_base_id
    if aobc_csv_path:
        aobc_bc_dict = csv_to_json(aobc_csv_path)
        data.append({"obc_name": "AOBC", "bc": aobc_bc_dict, "el": [], "eh": []})
    if tobc_csv_path:
        tobc_bc_dict = csv_to_json(tobc_csv_path)
        data.append({"obc_name": "TOBC", "bc": tobc_bc_dict, "el": [], "eh": []})
    if mif_csv_path:
        mif_bc_dict = csv_to_json(mif_csv_path)
        data.append({"obc_name": "MIF", "bc": mif_bc_dict, "el": [], "eh": []})
    if eh_src:
        with open(eh_src, "r", encoding="utf-8") as src_file:
            reader = csv.reader(src_file)
            headers = next(reader)
            dict_reader = csv.DictReader(src_file, fieldnames=headers)

            for row in dict_reader:
                if row[headers[0]].startswith('#'):
                    continue
                if not any(row):
                    continue
                if not row["name"].strip():
                    continue
                eh_list.append({"name": row["name"], "id": eh_id})
                eh_id += 1
    if el_src:
        with open(el_src, "r", encoding="utf-8") as src_file:
            reader = csv.reader(src_file)
            headers = next(reader)
            dict_reader = csv.DictReader(src_file, fieldnames=headers)

            # CMD_CODEの取得
            CMD_LIST = []
            if cmd_src:
                with open(cmd_src, "r", encoding="utf-8") as cmd_src_file:
                    cmd_reader = csv.reader(cmd_src_file)
                    cmd_header = next(cmd_reader)
                    cmd_dict_reader = csv.DictReader(
                        cmd_src_file, fieldnames=cmd_header
                    )
                    code = 0
                    for cmd_row in cmd_dict_reader:
                        if row[headers[0]].startswith('#'):
                            continue
                        if not any(cmd_row):
                            continue
                        if cmd_row["enabled"] == "TRUE":
                            try:
                                cmd_row["code"] = f"0x{int(code):04X}"
                                code += 1
                                if code == 496:  # 0x1F0, 0x1F1 を回避する
                                    code += 2
                            except ValueError:
                                continue
                            CMD_LIST.append({"name": cmd_row["name"], "local_id": code})

            # EH の取得
            EH_LIST = []
            if eh_src:
                eh_id = eh_base_id
                with open(eh_src, "r", encoding="utf-8") as eh_src_file:
                    eh_reader = csv.reader(eh_src_file)
                    eh_header = next(eh_reader)
                    eh_dict_reader = csv.DictReader(eh_src_file, fieldnames=eh_header)
                    for eh_row in eh_dict_reader:
                        if row[headers[0]].startswith('#'):
                            continue
                        if not any(eh_row):
                            continue
                        EH_LIST.append({"name": eh_row["name"], "local_id": int(eh_id)})
                        eh_id += 1

            # EL の取得
            EL_LIST = []
            with open(el_src, "r", encoding="utf-8") as el_src_file:
                el_reader = csv.reader(el_src_file)
                el_header = next(el_reader)
                el_dict_reader = csv.DictReader(el_src_file, fieldnames=el_header)
                for el_row in el_dict_reader:
                    if row[headers[0]].startswith('#'):
                        continue
                    if not el_row["group_id"].strip():
                        continue
                    EL_LIST.append(
                        {
                            "name": el_row["group_name"],
                            "local_id": int(el_row["group_id"]),
                        }
                    )

            last_el_dict = {}
            for row in dict_reader:
                if not any(row):
                    continue
                if row["group_name"].strip():
                    if last_el_dict:
                        el_list.append(last_el_dict)
                    last_el_dict = {
                        "name": row["group_name"],
                        "group_id": int(row["group_id"]),
                        "type": [],
                    }
                if row["local_name"].strip():
                    assert last_el_dict, "local_name must be under group_name"
                    if row["local_id"] == "uint32_t":
                        continue
                    if row["local_id"] in ["EL_GROUP"]:
                        for EL in EL_LIST:
                            last_el_dict["type"].append(EL)
                    elif row["local_id"] == "EH_RULE_ID":
                        for EH in EH_LIST:
                            last_el_dict["type"].append(EH)
                    elif row["local_id"] == "CMD_CODE":
                        for CMD in CMD_LIST:
                            last_el_dict["type"].append(CMD)
                    else:
                        last_el_dict["type"].append(
                            {
                                "name": row["local_name"],
                                "local_id": int(row["local_id"]),
                            }
                        )
            else:
                if last_el_dict:
                    el_list.append(last_el_dict)
    data.append({"obc_name": "MOBC", "bc": [], "el": el_list, "eh": eh_list})
    bcid = 0
    for src_path, bcid_base in bct_src:
        if bcid_base is not None:
            bcid = bcid_base

        with open(src_path, "r", encoding="utf-8") as src_file:
            reader = csv.reader(src_file)
            headers = next(reader)
            dict_reader = csv.DictReader(src_file, fieldnames=headers)

            for row in dict_reader:
                if row[headers[0]].startswith('#'):
                    continue
                if not any(row):
                    continue
                if not row["name"].strip():
                    continue
                data[-1]["bc"].append({"name": row["name"], "id": bcid})
                bcid += 1

    with open(dest_path, "w", encoding="utf-8") as dest_file:
        json.dump(data, dest_file, ensure_ascii=False, indent=2)
