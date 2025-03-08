import csv
from pathlib import Path


def generate(bct_src: list, dest_path: Path, bc_header_header: str) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"

    bc_definition_folder_path = dest_path.parent / "normal_block_command_definition"
    bc_header_path = bc_definition_folder_path / "nbc_header.h"

    with open(dest_path, "w", encoding="utf-8") as header_file, open(
        bc_header_path, "w", encoding="utf-8"
    ) as bc_header_file:
        header_file.write(
            """
#pragma section REPRO
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 */
#include "block_command_definitions.h"
#include <src_core/tlm_cmd/block_command_loader.h>
#include <src_core/tlm_cmd/block_command_table.h>
#include <src_core/System/watchdog_timer/watchdog_timer.h>
#include <string.h>
#include "command_definitions.h"

#include "./normal_block_command_definition/nbc_header.h"

/**
 * @brief
 * 各ブロックコマンドIDに中身の初期値をロードしていく
 */
void BC_load_defaults(void)
{
"""[1:]
        )
        bc_header_file.write(
            f"""
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef BC_HEADER_H_
#define BC_HEADER_H_

{bc_header_header}
"""[1:]
        )
        bc_num = 1
        for src_path, _ in bct_src:
            dest_c_path = bc_definition_folder_path / Path(src_path).name.replace(
                ".csv", ".c"
            )
            if "mram" in src_path.name:
                continue
            with open(src_path, "r", encoding="utf-8") as csv_file, open(
                dest_c_path, "w", encoding="utf-8"
            ) as c_file:
                c_file.write(
                    """
#pragma section REPRO
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 */
#include "bc_header.h"

"""[1:]
                )

                reader = csv.reader(csv_file)
                headers = next(reader)
                dict_reader = csv.DictReader(csv_file, fieldnames=headers)
                is_init = True
                for row in dict_reader:
                    if row[headers[0]].startswith('#'):
                        continue
                    if not any(row):
                        continue
                    if not row["name"].strip():
                        if row["type"]:
                            comment = ""
                            if row["description"]:
                                comment = f"  // {row['description']}"
                                if row["note"]:
                                    comment += f", NOTE: {row['note']}"
                            if comment:
                                c_file.write(f"{comment}\n")

                            if row["type"] in ["app", "combine", "rotate"]:
                                assert row["ti"], f"ti is not defined: {row}"
                                assert row["cmd"], f"cmd is not defined: {row}"
                                c_file.write(
                                    f"  BCL_tool_register_{row['type']}({row['ti']}, {row['cmd']});\n"
                                )
                            elif row["type"] == "code":
                                c_file.write(f"{row['cmd']}\n")
                            elif row["type"] in ["cmd", "cmd_to_other_obc"]:
                                assert row["ti"], f"ti is not defined: {row}"
                                assert row["cmd"], f"cmd is not defined: {row}"
                                assert (
                                    row["type"] == "cmd" or row["option"]
                                ), f"option is not defined: {row}"
                                if row["args"]:
                                    args = row["args"].split(",")
                                    for arg in args:
                                        arg_type, arg_value = arg.split(":")
                                        c_file.write(
                                            f"  BCL_tool_prepare_param_{arg_type}({arg_value});\n"
                                        )
                                if row["type"] == "cmd":
                                    c_file.write(
                                        f"  BCL_tool_register_cmd({row['ti']}, {row['cmd']});\n"
                                    )
                                else:
                                    c_file.write(
                                        f"  BCL_tool_register_cmd_to_other_obc({row['ti']}, {row['option']}, (CMD_CODE){row['cmd']});\n"
                                    )
                            elif row["type"] in ["deploy", "limit_combine"]:
                                assert row["ti"], f"ti is not defined: {row}"
                                assert row["cmd"], f"cmd is not defined: {row}"
                                assert row["option"], f"option is not defined: {row}"
                                c_file.write(
                                    f"  BCL_tool_register_{row['type']}({row['ti']}, {row['cmd']}, {row['option']});\n"
                                )
                            else:
                                assert False, f"Unknown type: {row}"
                        continue
                    comment = (
                        f"    // {row['description']}"
                        if len(row) > 2 and row["description"]
                        else ""
                    )
                    header_file.write(
                        f"  BCL_load_bc({row['name']}, BCL_load_{row['name'][3:].lower()});{comment}\n"
                    )
                    bc_header_file.write(
                        f"void BCL_load_{row['name'][3:].lower()}(void);{comment}\n"
                    )
                    if not is_init:
                        c_file.write("}\n\n")
                    else:
                        is_init = False
                    c_file.write(
                        f"void BCL_load_{row['name'][3:].lower()}(void){comment}\n{{\n"
                    )
                    if bc_num % 6 == 0:
                        header_file.write("  WDT_clear_wdt();\n")
                    bc_num += 1

                if not is_init:
                    c_file.write("}\n")
                c_file.write("\n#pragma section\n")

        header_file.write(
            """}

#pragma section
"""
        )
        bc_header_file.write(
            """
#endif
"""
        )
