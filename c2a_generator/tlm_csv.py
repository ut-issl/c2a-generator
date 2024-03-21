import csv
import os
from pathlib import Path


def generate(src_dir_path: Path, dest_dir_path: Path, prefix: str) -> None:
    # packet_id 小さい順
    src_path_list = sorted(
        (csv_file for csv_file in src_dir_path.glob("*.csv") if (_ := next(csv.reader(csv_file.open()), [None, None]))[1].isdigit()),
        key=lambda x: int(next(csv.reader(x.open()), [None, None])[1]),
    )

    for src_path in src_path_list:
        dest_name = prefix + os.path.basename(src_path)
        dest_path = dest_dir_path / dest_name
        generate_(src_path, dest_path)


def generate_(src_file_path: Path, dest_file_path: Path) -> None:
    dest_line_len = 18
    dest_line_max = 500
    line_index = 8

    pos = 0
    bit_len = 0

    with open(src_file_path, "r", encoding="utf-8") as src_file, open(dest_file_path, "w", encoding="utf-8") as dest_file:
        reader = csv.reader(src_file)
        reader = list(reader)

        row0 = reader[0]
        row0 = [row0[i].replace("\n", "##") for i in range(len(row0))]
        row0 = [row0[i].replace(",", "@@") for i in range(len(row0))]

        dest_file.write(f",Target,{row0[2]},Local Var")
        dest_file.write("," * (dest_line_len - 4) + "\n")
        dest_file.write(f",PacketID,0x{int(row0[1]):02x},{row0[3]}")
        dest_file.write("," * (dest_line_len - 4) + "\n")
        dest_file.write(",Enable/Disable,ENABLE")
        dest_file.write("," * (dest_line_len - 3) + "\n")
        dest_file.write(f",IsRestricted,{row0[0]}")
        dest_file.write("," * (dest_line_len - 3) + "\n")
        dest_file.write("," * (dest_line_len - 1) + "\n")
        dest_file.write(
            """
Comment,TLM Entry,Onboard Software Info.,,Extraction Info.,,,,Conversion Info.,,,,,,,,Description,Note
,Name,Var.%%##Type,Variable or Function Name,Ext.%%##Type,Pos. Desiginator,,,Conv.%%##Type,Poly (Σa_i * x^i),,,,,,Status,,
,,,,,Octet%%##Pos.,bit%%##Pos.,bit%%##Len.,,a0,a1,a2,a3,a4,a5,,,
"""[
                1:
            ]
        )

        reader = reader[2:]

        for row in reader:
            row = row[1:]
            row = [row[i].replace("\n", "##") for i in range(len(row))]
            row = [row[i].replace(",", "@@") for i in range(len(row))]
            if not any(row):
                line_index += 1
                continue
            if row[1]:
                if row[1][0] == "_":
                    row[1] = row[1][1:]
                    bit_len = int(row[2])
                else:
                    bit_len = type2bit(row[1])
            else:
                bit_len = int(row[2])

            bit_pos = pos % 8
            octet_pos = int(pos / 8)
            pos += bit_len

            if (row[0][-5:] == 'DUMMY'):
                dest_file.write('*')

            dest_file.write(
                f",{row[0]},{row[1]},{row[3]},PACKET,{octet_pos},{bit_pos},{bit_len},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},\
{row[9]},{row[10]},{row[11]},{row[12]},{row[13]}\n"
            )
            line_index += 1
        dest_file.write(("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index))


def type2bit(val_type: str) -> int:
    if val_type == "uint8_t":
        return 8
    if val_type == "uint16_t":
        return 16
    if val_type == "uint32_t":
        return 32
    if val_type == "uint64_t":
        return 64
    if val_type == "int8_t":
        return 8
    if val_type == "int16_t":
        return 16
    if val_type == "int32_t":
        return 32
    if val_type == "int64_t":
        return 64
    if val_type == "float":
        return 32
    if val_type == "double":
        return 64
    print("type: ", val_type)
    raise Exception("Tlm valuable type is invalid")
