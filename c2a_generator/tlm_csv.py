import csv
import os
from pathlib import Path


def generate(src_dir_path: Path, dest_dir_path: Path, prefix: str) -> None:
    # packet_id 小さい順
    src_path_list = sorted(
        (
            csv_file
            for csv_file in src_dir_path.glob("*.csv")
            if (_ := next(csv.reader(csv_file.open()), [None, None]))[1].isdigit()
        ),
        key=lambda x: int(next(csv.reader(x.open()), [None, None])[1]),
    )

    for src_path in src_path_list:
        dest_name = prefix + os.path.basename(src_path)
        dest_path = dest_dir_path / dest_name
        dest_calced_data_path = dest_dir_path / "calced_data" / dest_name
        generate_(src_path, dest_path, dest_calced_data_path)


def generate_(
    src_file_path: Path, dest_file_path: Path, dest_calced_data_path: Path
) -> None:
    dest_line_len = 18
    dest_line_max = 500
    line_index = 8

    pos = 0
    bit_len = 0

    with open(src_file_path, "r", encoding="utf-8") as src_file, open(
        dest_calced_data_path, "w", encoding="utf-8"
    ) as dest_calced_data, open(dest_file_path, "w", encoding="utf-8") as dest_file:
        reader = csv.reader(src_file)

        meta = next(reader)
        headers = next(reader)
        dict_reader = csv.DictReader(src_file, fieldnames=headers)

        for i in range(len(meta)):
            meta[i] = meta[i].replace("\n", "##").replace(",", "@@")

        dest_calced_data.write(
            f"""
,Target,{meta[2]},Local Var{"," * (dest_line_len - 4)}
,PacketID,0x{int(meta[1]):02x},{meta[3]}{"," * (dest_line_len - 4)}
,Enable/Disable,ENABLE{"," * (dest_line_len - 3)}
,IsRestricted,{meta[0]}{"," * (dest_line_len - 3)}
{"," * (dest_line_len - 1)}
Comment,TLM Entry,Onboard Software Info.,,Extraction Info.,,,,Conversion Info.,,,,,,,,Description,Note
,Name,Var.%%##Type,Variable or Function Name,Ext.%%##Type,Pos. Desiginator,,,Conv.%%##Type,Poly (Σa_i * x^i),,,,,,Status,,
,,,,,Octet%%##Pos.,bit%%##Pos.,bit%%##Len.,,a0,a1,a2,a3,a4,a5,,,
"""[1:]
        )
        dest_file.write(
            f"""
,Target,{meta[2]},Local Var{"," * (dest_line_len - 4)}
,PacketID,0x{int(meta[1]):02x},{meta[3]}{"," * (dest_line_len - 4)}
,Enable/Disable,ENABLE{"," * (dest_line_len - 3)}
,IsRestricted,{meta[0]}{"," * (dest_line_len - 3)}
{"," * (dest_line_len - 1)}
Comment,TLM Entry,Onboard Software Info.,,Extraction Info.,,,,Conversion Info.,,,,,,,,Description,Note
,Name,Var.%%##Type,Variable or Function Name,Ext.%%##Type,Pos. Desiginator,,,Conv.%%##Type,Poly (Σa_i * x^i),,,,,,Status,,
,,,,,Octet%%##Pos.,bit%%##Pos.,bit%%##Len.,,a0,a1,a2,a3,a4,a5,,,
"""[1:]
        )

        for row in dict_reader:
            for key in ["var", "status", "description", "note"]:
                row[key] = row[key].replace("\n", "##").replace(",", "@@")
            if not any(row):
                line_index += 1
                continue

            type_original = row["type"]
            if row["type"]:
                if row["type"][0] == "_":
                    type_original = row["type"][1:]
                    row["type"] = row["type"][1:]
                    bit_len = int(row["bit"])
                else:
                    bit_len = type2bit(row["type"])
            else:
                bit_len = int(row["bit"])
                type_original = "||"

            bit_pos = pos % 8
            octet_pos = int(pos / 8)
            pos += bit_len

            if row["name"][-5:] == "DUMMY" or row["name"][0:5] == "DUMMY":
                dest_calced_data.write("*")
                dest_file.write("*")

            dest_calced_data.write(
                f",{row['name']},{row['type']},{row['var']},PACKET,{octet_pos},{bit_pos},{bit_len},{row['conv']},{row['a0']},{row['a1']},{row['a2']},{row['a3']},\
{row['a4']},{row['a5']},{row['status']},{row['description']},{row['note']}\n"
            )

            octet_pos_original = (
                "=R[-1]C+INT((R[-1]C[1]+R[-1]C[2])/8)"
                if row["name"] != "PH.VER"
                else "0"
            )
            bit_pos_original = (
                "=MOD((R[-1]C+R[-1]C[1])@@8)" if row["name"] != "PH.VER" else "0"
            )
            bit_len_original = (
                '=IF(OR(EXACT(RC[-5]@@"uint8_t")@@EXACT(RC[-5]@@"int8_t"))@@8@@IF(OR(EXACT(RC[-5]@@"uint16_t")@@EXACT(RC[-5]@@"int16_t"))@@16@@IF(OR(EXACT(RC[-5]@@"uint32_t")@@EXACT(RC[-5]@@"int32_t")@@EXACT(RC[-5]@@"float"))@@32@@IF(EXACT(RC[-5]@@"double")@@64))))'
                if not row["bit"]
                else row["bit"]
            )
            var_original = row["var"]
            if not row["var"] and (
                len(row["name"]) > 3 and row["name"][0:3] not in ["PH.", "SH."]
            ):
                var_original = "||"
            dest_file.write(
                f',{row["name"]},{type_original},{var_original},PACKET,{octet_pos_original},{bit_pos_original},{bit_len_original},{row["conv"]},{row["a0"]},{row["a1"]},{row["a2"]},{row["a3"]},{row["a4"]},{row["a5"]},{row["status"]},{row["description"]},{row["note"]}\n'
            )

            line_index += 1
        dest_calced_data.write(
            ("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index)
        )
        dest_file.write(
            ("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index)
        )


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
