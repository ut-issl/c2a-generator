import csv

def generate_bit_operation(variables, result_type="uint8_t"):
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

def generate_bct_def(src_path, dest_path):
    with open(src_path, 'r', encoding='utf-8') as csv_file, \
         open(dest_path, 'w', encoding='utf-8') as header_file:
        header_file.write("""
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef BLOCK_COMMAND_DEFINITIONS_H_
#define BLOCK_COMMAND_DEFINITIONS_H_

// 登録されるBlockCommandTableのblock番号を規定
typedef enum
{
"""[1:])
        reader = csv.reader(csv_file)
        next(reader)
        previous_line_was_comment = False
        for row in reader:
            if not any(row):
                continue
            if row[0]:
                previous_line_was_comment = False
                comment = f"    // {row[2]}" if len(row) > 2 and row[2] else ""
                header_file.write(f"  {row[1]} = {row[0]},{comment}\n")
            else:
                if not previous_line_was_comment:
                    header_file.write("\n")
                header_file.write(f"  // {row[1]}\n")
                previous_line_was_comment = True
        header_file.write("""
  BC_ID_MAX    // BCT 自体のサイズは BCT_MAX_BLOCKS で規定
} BC_DEFAULT_ID;

void BC_load_defaults(void);

#endif
""")

def generate_cmd_def_h(src_path, dest_path):
    with open(src_path, 'r', encoding='utf-8') as csv_file, \
         open(dest_path, 'w', encoding='utf-8') as header_file:
        header_file.write("""
/**
 * @file
 * @brief  コマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef COMMAND_DEFINITIONS_H_
#define COMMAND_DEFINITIONS_H_

typedef enum
{
"""[1:])
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            if not any(row):
                continue
            if row[0]:
                try:
                    row[0] = f'0x{int(row[0]):04X}'
                except ValueError:
                    continue
                # comment = f"    // {row[16]}" if len(row) > 2 and row[16] else ""
                comment = ""
                header_file.write(f"  Cmd_CODE_{row[2]} = {row[0]},{comment}\n")
        header_file.write("""
  Cmd_CODE_MAX
} CMD_CODE;

#endif
""")

def generate_cmd_def_c(src_path, dest_path):
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
    with open(src_path, 'r', encoding='utf-8') as csv_file, \
         open(dest_path, 'w', encoding='utf-8') as header_file:
        header_file.write("""
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
"""[1:])
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
                        param_info += (f"  cmd_table[Cmd_CODE_{row[2]}].param_size_infos[{index}].packed_info.bit.{subindex} = {conv_type_to_size[param]};\n")
        header_file.write(f"\n{param_info}")
        header_file.write("""
}

#pragma section
""")

def generate_tlm_def_h(src_path, dest_path):
    with open(dest_path, 'w', encoding='utf-8') as header_file:
        header_file.write("""
/**
 * @file
 * @brief  テレメトリ定義
 * @note   このコードは自動生成されています！
 */
#ifndef TELEMETRY_DEFINITIONS_H_
#define TELEMETRY_DEFINITIONS_H_

typedef enum
{
"""[1:])
        tlm_codes = []
        for csv_file in src_path.glob('*.csv'):
            with csv_file.open('r', encoding='utf-8') as file:
                reader = csv.reader(file)
                try:
                    packet_id = next(reader)[1]
                except StopIteration:
                    continue
                packet_id_hex = f'0x{int(packet_id):02X}'
                tlm_codes.append((packet_id_hex, csv_file.stem))
        tlm_codes.sort(key=lambda x: x[0])
        for packet_id, file_name in tlm_codes:
            header_file.write(f"  Tlm_CODE_{file_name} = {packet_id},\n")
        header_file.write("""
  TLM_CODE_MAX
} TLM_CODE;

#endif
""")

def generate_tlm_def_c(src_path, dest_path):
    with open(dest_path, 'w', encoding='utf-8') as header_file:
        header_file.write("""
#pragma section REPRO
/**
 * @file
 * @brief  テレメトリ定義
 * @note   このコードは自動生成されています！
 */
#include <src_core/TlmCmd/telemetry_frame.h>
#include "telemetry_definitions.h"
#include "telemetry_source.h"

"""[1:])
        # packet_id 小さい順
        tlm_path_list = sorted(
            (csv_file for csv_file in src_path.glob('*.csv') if (line := next(csv.reader(csv_file.open()), [None, None]))[1].isdigit()),
            key=lambda x: int(next(csv.reader(x.open()), [None, None])[1])
        )
        src_list = ["", "\nvoid TF_load_tlm_table(TF_TlmInfo tlm_table[TF_MAX_TLMS])\n{\n", ""]
        type_to_func_and_pos = {
            "int8_t": ("TF_copy_i8", 1),
            "int16_t": ("TF_copy_i16", 2),
            "int32_t": ("TF_copy_i32", 4),
            "uint8_t": ("TF_copy_u8", 1),
            "uint16_t": ("TF_copy_u16", 2),
            "uint32_t": ("TF_copy_u32", 4),
            "float": ("TF_copy_float", 4),
            "double": ("TF_copy_double", 8)
        }
        for tlm_path in tlm_path_list:
            tlm_name = tlm_path.stem
            src_list[0] += f"static TF_TLM_FUNC_ACK Tlm_{tlm_name}_(uint8_t* packet, uint16_t* len, uint16_t max_len);\n"
            src_list[1] += f"  tlm_table[Tlm_CODE_{tlm_name}].tlm_func = Tlm_{tlm_name}_;\n"
            src_list[2] += f"\nstatic TF_TLM_FUNC_ACK Tlm_{tlm_name}_(uint8_t* packet, uint16_t* len, uint16_t max_len)\n{{\n"
            with open(tlm_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                first_line = next(reader)
                local_var = first_line[3].replace("\n", "\n  ") if len(first_line) > 3 else ""
                headers = next(reader)
                dict_reader = csv.DictReader(file, fieldnames=headers)
                src_func = ""
                pos_sum = 0
                is_bit_shift, bit_shift_func_list, bit_shift_type = False, [], ""
                for row in dict_reader:
                    if not any(row.values()):
                        continue
                    if is_bit_shift and row["type"]:
                        var = generate_bit_operation(bit_shift_func_list, bit_shift_type)
                        func, pos = type_to_func_and_pos[bit_shift_type]
                        src_func += f"  {func}(&packet[{pos_sum}], {var});\n"
                        pos_sum += pos
                        is_bit_shift, bit_shift_func_list, bit_shift_type = False, [], ""
                    if len(row["type"]) > 0 and row["type"][0] == "_" and "PH." not in row["name"]:
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
                        var = generate_bit_operation(bit_shift_func_list, bit_shift_type)
                        func, pos = type_to_func_and_pos[bit_shift_type]
                        src_func += f"  {func}(&packet[{pos_sum}], {var});\n"
                        pos_sum += pos

                if local_var:
                    src_list[2] += f"  {local_var.strip()}\n\n"
                src_list[2] += f"  if ({str(pos_sum)} > max_len) return TF_TLM_FUNC_ACK_TOO_SHORT_LEN;\n\n#ifndef BUILD_SETTINGS_FAST_BUILD\n{src_func}"
            src_list[2] += f"#endif\n\n  *len = {pos_sum};\n  return TF_TLM_FUNC_ACK_SUCCESS;\n}}\n"
        else:
            src_list[1] += "}\n"
        for src in src_list:
            header_file.write(src)
        header_file.write("""
#pragma section
""")
    pass

def generate_other_obc_cmd_def():
    pass

def generate_other_obc_tlm_def():
    pass

def generate_tlm_buffer():
    pass


