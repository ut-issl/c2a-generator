import csv
from pathlib import Path


def generate(src_path: Path, dest_path: Path) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    conv_type_to_size = {
        "int8_t": "CA_PARAM_SIZE_TYPE_1BYTE",
        "int16_t": "CA_PARAM_SIZE_TYPE_2BYTE",
        "int32_t": "CA_PARAM_SIZE_TYPE_4BYTE",
        "uint8_t": "CA_PARAM_SIZE_TYPE_1BYTE",
        "uint16_t": "CA_PARAM_SIZE_TYPE_2BYTE",
        "uint32_t": "CA_PARAM_SIZE_TYPE_4BYTE",
        "float": "CA_PARAM_SIZE_TYPE_4BYTE",
        "double": "CA_PARAM_SIZE_TYPE_8BYTE",
        "raw": "CA_PARAM_SIZE_TYPE_RAW",
    }
    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
#pragma section REPRO
/**
 * @file
 * @brief  コマンド定義
 * @note   このコードは自動生成されています！
 */
#include <src_core/TlmCmd/command_analyze.h>
#include "command_definitions.h"
#include "command_source.h"

void CA_load_cmd_table(CA_CmdInfo cmd_table[CA_MAX_CMDS])
{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        param_info = ""
        next(reader)
        for row in reader:
            if not any(row):
                continue
            if row[0]:
                header_file.write(f"  cmd_table[Cmd_CODE_{row[2]}].cmd_func = Cmd_{row[2]};\n")
                for i, param in enumerate(row[4:16:2]):
                    if param != "":
                        index = i // 2
                        subindex = "second" if i % 2 else "first"
                        param_info += (
                            f"  cmd_table[Cmd_CODE_{row[2]}].param_size_infos[{index}].packed_info.bit.{subindex} = {conv_type_to_size[param]};\n"
                        )
        header_file.write(f"\n{param_info}")
        header_file.write(
            """
}

#pragma section
"""
        )
