import csv
from pathlib import Path


def generate(bct_src: list, dest_file_path: Path) -> None:
    prev_row0_is_none = False
    dest_line_len = 12
    dest_line_max = 300
    line_index = 2

    with open(dest_file_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            """
Comment,Name,ShortName,BCID,エイリアス,,,,,Danger Flag,Description,Note
,,,,Deploy,SetBlockPosition,Clear,Activate,Inactivate,,,
"""[
                1:
            ]
        )
        bcid = 0
        for src_path, bcid_base in bct_src:
            if bcid_base is not None:
                bcid = bcid_base
            with open(src_path, "r", encoding="utf-8") as src_file:
                reader = csv.reader(src_file)
                headers = next(reader)
                dict_reader = csv.DictReader(src_file, fieldnames=headers)

                for row in dict_reader:
                    row["description"] = row["description"].replace(",", "@@").replace("\n", "##")
                    row["note"] = row["note"].replace(",", "@@").replace("\n", "##")
                    if not any(row):
                        continue
                    if not row["name"].strip():
                        continue
                    dest_file.write(f",{row['name']},,{bcid},,,,,,,{row['description']},")
                    if row["note"]:
                        dest_file.write(f"{row['note']}")
                    dest_file.write("\n")
                    bcid += 1
                    line_index += 1

        dest_file.write(("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index))
