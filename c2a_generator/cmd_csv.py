import csv
from pathlib import Path


def generate(src_file_path: Path, dest_file_path: Path) -> None:
    compo_list = ["CORE", "CDH", "POWER", "COMM", "MISSION", "Thermal", "Other", "Nonorder"]
    compo_comut = 0
    dest_line_len = 21
    line_index = 4
    dest_line_max = 1000
    prev_is_none = False

    with open(src_file_path, "r", encoding="utf-8") as src_file, open(dest_file_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            """
Component,Name,Target,Code,Params,,,,,,,,,,,,,Danger Flag,Is Restricted,Description,Note
MOBC,,,,Num Params,Param1,,Param2,,Param3,,Param4,,Param5,,Param6,,,,,
Comment,,,,,Type,Description,Type,Description,Type,Description,Type,Description,Type,Description,Type,Description,,,,
*,EXAMPLE,OBC,,2,uint32_t,address,int32_t,time [ms],,,,,,,,,,,例,引数の説明と単位を書くこと！（例：time [ms]）
"""[
                1:
            ]
        )
        reader = csv.reader(src_file)
        next(reader)
        code = 0

        for row in reader:
            row = row[:1] + row[2:]
            row = [row[i].replace("\n", "##") for i in range(len(row))]
            row = [row[i].replace(",", "@@") for i in range(len(row))]
            if not any(row):
                prev_is_none = True
                dest_file.write("**")
                dest_file.write("," * (dest_line_len - 2) + "\n")
                line_index += 1
                continue

            if row[1]:
                num_params = sum(1 for i in [4, 6, 8, 10, 12, 14] if row[i] != "")
                if row[3]:
                    row[3] = "danger"
                if row[0] == "TRUE":
                    dest_file.write(
                        f",{row[2]},{row[1]},0x{int(code):04X},{int(num_params)},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},\
{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]},{row[3]},restricted,{row[16]},{row[17]}\n"
                    )
                    code += 1
                else:
                    dest_file.write(
                        f"*,{row[2]},{row[1]},,{int(num_params)},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},{row[9]},{row[10]},\
{row[11]},{row[12]},{row[13]},{row[14]},{row[15]},{row[3]},restricted,{row[16]},{row[17]}\n"
                    )
            else:
                if prev_is_none or compo_comut == 0:
                    dest_file.write(f"*{compo_list[compo_comut]},")
                    compo_comut += 1
                else:
                    dest_file.write("**,")
                dest_file.write(f"{row[2]}")
                dest_file.write("," * (dest_line_len - 2) + "\n")

            prev_is_none = False
            line_index += 1

        dest_file.write(("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index))
