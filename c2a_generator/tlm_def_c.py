import csv
from pathlib import Path
from typing import List, Union


def generate_bit_operation(variables: list, result_type: str = "uint8_t") -> str:
    if len(variables) == 1:
        return variables[0][0]
    type_to_max_bits = {"uint8_t": 8, "uint16_t": 16, "uint32_t": 32}
    max_bits = type_to_max_bits.get(result_type, 8)
    current_bit = max_bits

    operation_parts = []
    for var_name, bit_size in variables:
        current_bit -= bit_size
        if var_name:
            mask = (1 << bit_size) - 1

            if current_bit != 0:
                part = f"({var_name} << {current_bit} & 0x{mask << current_bit:0{max_bits // 4}X})"
            else:
                part = f"({var_name} & 0x{mask:0{max_bits // 4}X})"
            operation_parts.append(part)

    operation = " | ".join(operation_parts)
    return f"({operation})" if result_type is None else f"({result_type})({operation})"


def generate(src_path: Path, dest_path: Path) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
#pragma section REPRO
/**
 * @file
 * @brief  テレメトリ定義
 * @note   このコードは自動生成されています！
 */
#include <src_core/tlm_cmd/telemetry_frame.h>
#include <src_core/library/git_revision.h>
#include "telemetry_definitions.h"
#include "telemetry_source.h"

"""[1:]
        )
        # packet_id 小さい順
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
        src_list = [
            "",
            "\nvoid TF_load_tlm_table(TF_TlmInfo tlm_table[TF_MAX_TLMS])\n{\n",
            "",
        ]
        type_to_func_and_pos = {
            "int8_t": ("TF_copy_i8", 1),
            "int16_t": ("TF_copy_i16", 2),
            "int32_t": ("TF_copy_i32", 4),
            "int64_t": {"TF_copy_i64", 8},
            "uint8_t": ("TF_copy_u8", 1),
            "uint16_t": ("TF_copy_u16", 2),
            "uint32_t": ("TF_copy_u32", 4),
            "uint64_t": ("TF_copy_u64", 8),
            "float": ("TF_copy_float", 4),
            "double": ("TF_copy_double", 8),
        }
        for tlm_path in tlm_path_list:
            tlm_name = tlm_path.stem
            src_list[0] += (
                f"static TF_TLM_FUNC_ACK Tlm_{tlm_name}_(uint8_t* packet, uint16_t* len, uint16_t max_len);\n"
            )
            src_list[1] += (
                f"  tlm_table[Tlm_CODE_{tlm_name}].tlm_func = Tlm_{tlm_name}_;\n"
            )
            src_list[2] += (
                f"\nstatic TF_TLM_FUNC_ACK Tlm_{tlm_name}_(uint8_t* packet, uint16_t* len, uint16_t max_len)\n{{\n"
            )
            with open(tlm_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                first_line = next(reader)
                local_var = (
                    first_line[3].replace("\n", "\n  ") if len(first_line) > 3 else ""
                )
                headers = next(reader)
                dict_reader = csv.DictReader(file, fieldnames=headers)
                src_func = ""
                pos_sum = 0
                is_bit_shift, bit_shift_type = False, ""
                bit_shift_func_list: List[tuple] = []
                for row in dict_reader:
                    if row[headers[0]].startswith('#'):
                        continue
                    if not any(row.values()):
                        continue
                    if is_bit_shift and row["type"]:
                        var = generate_bit_operation(
                            bit_shift_func_list, bit_shift_type
                        )
                        func, pos = type_to_func_and_pos[bit_shift_type]
                        if var:
                            src_func += f"  {func}(&packet[{pos_sum}], {var});\n"
                            pos_sum += pos
                        is_bit_shift, bit_shift_func_list, bit_shift_type = (
                            False,
                            [],
                            "",
                        )
                    if (
                        len(row["type"]) > 0
                        and row["type"][0] == "_"
                        and "PH." not in row["name"]
                    ):
                        is_bit_shift = True
                        bit_shift_type = row["type"][1:]
                        bit_shift_func_list.append((row["var"], int(row["bit"])))
                        continue
                    row["type"] = row["type"].lstrip("_")
                    if row["type"] in type_to_func_and_pos:
                        func, pos = type_to_func_and_pos[row["type"]]
                        if row["var"]:
                            src_func += f"  {func}(&packet[{pos_sum}], {row['var']});\n"
                            pos_sum += pos
                        elif "PH." in row["name"] or "SH." in row["name"]:
                            pos_sum += pos
                    elif is_bit_shift and row["var"]:
                        bit_shift_func_list.append((row["var"], int(row["bit"])))
                else:
                    if is_bit_shift:
                        var = generate_bit_operation(
                            bit_shift_func_list, bit_shift_type
                        )
                        func, pos = type_to_func_and_pos[bit_shift_type]
                        src_func += f"  {func}(&packet[{pos_sum}], {var});\n"
                        pos_sum += pos

                if local_var:
                    src_list[2] += f"  {local_var.strip()}\n\n"
                src_list[2] += (
                    f"  if ({str(pos_sum)} > max_len) return TF_TLM_FUNC_ACK_TOO_SHORT_LEN;\n\n#ifndef BUILD_SETTINGS_FAST_BUILD\n{src_func}"
                )
            src_list[2] += (
                f"#endif\n\n  *len = {pos_sum};\n  return TF_TLM_FUNC_ACK_SUCCESS;\n}}\n"
            )
        else:
            src_list[1] += "}\n"
        for src in src_list:
            header_file.write(src)
        header_file.write(
            """
#pragma section
"""
        )
