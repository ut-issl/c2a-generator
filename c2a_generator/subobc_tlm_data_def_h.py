import csv
import sys
from pathlib import Path
from typing import Union

from .util import get_git_file_blob_url

INVALID_START_CHARS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def set_struct_tree(struct_tree: dict, path: str, value: str, sep: str = "/") -> int:
    keys = path.split(sep)

    def recurse(tree: dict, keys: list, value: str, sep: str) -> int:
        if len(keys) == 0:
            return 1
        if len(keys) == 1:
            key = keys[0]
            key = key if key[0] not in INVALID_START_CHARS else "_" + key
            if key in tree:
                return 1
            tree[key] = value
            return 0
        else:
            key = keys[0]
            key = key if key[0] not in INVALID_START_CHARS else "_" + key
            if key not in tree:
                tree[key] = {}
            return recurse(tree[key], keys[1:], value, sep)

    return recurse(struct_tree, keys, value, sep)


def generate_struct_definition(struct_tree: dict, struct_name: str, indent: int = 2) -> str:
    def recurse(tree: dict, name: str, indent: int) -> str:
        output = " " * indent + "struct\n" + " " * indent + "{\n"
        for key, value in tree.items():
            if isinstance(value, dict):
                output += recurse(value, key, indent + 2)
            else:
                output += " " * (indent + 2) + value + " " + key + ";\n"
        output += " " * indent + "} " + name + ";\n"
        return output

    return recurse(struct_tree, struct_name, indent)


def generate(src_path: Path, dest_path: Path, obc_name: str) -> None:
    file_blob_url = get_git_file_blob_url(src_path)
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(dest_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            f"""
/**
 * @file
 * @brief  バッファリングされているテレメをパースしてMOBC内でかんたんに利用できるようにするためのテレメデータ構造体定義
 * @note   このコードは自動生成されています！
 * @src    {file_blob_url}
 */
#ifndef {obc_name}_TELEMETRY_DATA_DEFINITIONS_H_
#define {obc_name}_TELEMETRY_DATA_DEFINITIONS_H_

typedef struct
{{
"""[
                1:
            ]
        )
        csv_files = [csv_file for csv_file in src_path.glob("*.csv")]

        def sort_key(csv_file: Path) -> Union[int, float]:
            with csv_file.open() as file:
                reader = csv.reader(file)
                first_row = next(reader, ["", ""])
                try:
                    packet_id = int(first_row[1])
                except ValueError:
                    raise ValueError(f"Invalid packet_id: {first_row[1]}")
                return packet_id

        tlm_path_list = sorted(csv_files, key=sort_key)
        src = ""
        for tlm_path in tlm_path_list:
            tlm_name = tlm_path.stem
            tlm_struct_tree = {}
            last_var_type = ""
            with open(tlm_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)
                headers = next(reader)
                dict_reader = csv.DictReader(file, fieldnames=headers)
                for row in dict_reader:
                    if not any(row.values()):
                        continue
                    if row["type"] == "":
                        row["type"] = last_var_type
                    elif row["type"][0] == "_":
                        row["type"] = row["type"].lstrip("_")
                        last_var_type = row["type"]
                    row["name"] = "/".join(row["name"].lower().replace("/", "_").split("."))
                    if set_struct_tree(tlm_struct_tree, row["name"], row["type"]):
                        print(f"Error: Tlm DB Struct Parse Err at {row['name']}", file=sys.stderr)
                        sys.exit(1)
            src += generate_struct_definition(tlm_struct_tree, tlm_name.lower())
        src += f"}} {obc_name}_TlmData;\n"
        dest_file.write(src)
        dest_file.write(
            """
#endif
"""
        )
