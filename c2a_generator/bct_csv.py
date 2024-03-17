import csv
from pathlib import Path


def generate(src_file_path: Path, dest_file_path: Path) -> None:
    prev_row0_is_none = False
    dest_line_len = 12
    dest_line_max = 300
    line_index = 2

    with open(src_file_path, "r", encoding="utf-8") as src_file, open(dest_file_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            """
Comment,Name,ShortName,BCID,エイリアス,,,,,Danger Flag,Description,Note
,,,,Deploy,SetBlockPosition,Clear,Activate,Inactivate,,,
"""[
                1:
            ]
        )
        reader = csv.reader(src_file)
        next(reader)

        for row in reader:
            row = row[1:]
            row = [row[i].replace("\n", "##") for i in range(len(row))]
            row = [row[i].replace(",", "@@") for i in range(len(row))]
            if not any(row):
                continue

            if row[0]:
                # num_params = (len(list(filter(None, row[2:15]))) - 1) / 2
                dest_file.write(f",{row[1]},,{row[0]},,,,,,,{row[2]}\n")
                prev_row0_is_none = False
            else:
                if prev_row0_is_none:
                    dest_file.write(f"*,{row[1]}")
                    dest_file.write("," * (dest_line_len - 2) + "\n")
                else:
                    dest_file.write(f"**,{row[1]}")
                    dest_file.write("," * (dest_line_len - 2) + "\n")
                prev_row0_is_none = True
            line_index += 1

        dest_file.write(("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index))
