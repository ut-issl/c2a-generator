import csv
from pathlib import Path
from typing import Union

conv_type = {
    "int8_t": ("temp_i8", 1),
    "int16_t": ("temp_i16", 2),
    "int32_t": ("temp_i32", 4),
    "uint8_t": ("temp_u8", 1),
    "uint16_t": ("temp_u16", 2),
    "uint32_t": ("temp_u32", 4),
    "float": ("temp_f", 4),
    "double": ("temp_d", 8),
}


def generate(src_path: Path, dest_path: Path, obc_name: str, driver_type: str, driver_name: str, code_when_tlm_not_found: str) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(dest_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            f"""
#pragma section REPRO
/**
 * @file
 * @brief  テレメトリバッファー（テレメ中継）
 * @note   このコードは自動生成されています！
 */
#include <src_core/Drivers/Protocol/common_tlm_cmd_packet_for_driver_super.h>
#include "./{obc_name.lower()}_telemetry_definitions.h"
#include "./{obc_name.lower()}_telemetry_buffer.h"
#include "./{obc_name.lower()}.h"
#include <string.h>

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
        src_list = [
            "",
            f"""
static CommonTlmPacket {obc_name}_ctp_;

void {obc_name}_init_tlm_buffer({driver_type}* {driver_name})
{{
  // packet などは，上位の driver の初期化で driver もろとも memset 0x00 されていると期待して，ここではしない
  int i = 0;
  for (i = 0; i < {obc_name}_MAX_TLM_NUM; ++i)
  {{
    {driver_name}->tlm_buffer.tlm[i].is_null_packet = 1;
  }}
}}

DS_ERR_CODE {obc_name}_buffer_tlm_packet(DS_StreamConfig* p_stream_config, {driver_type}* {driver_name})
{{
  {obc_name}_TLM_CODE tlm_id;
  DS_ERR_CODE ret;

  ret = CTP_get_ctp_from_dssc(p_stream_config, &{obc_name}_ctp_);
  if (ret != DS_ERR_CODE_OK) return ret;

  tlm_id  = ({obc_name}_TLM_CODE)CTP_get_id(&{obc_name}_ctp_);

  switch (tlm_id)
  {{
""",
            "",
        ]
        for tlm_path in tlm_path_list:
            tlm_name = tlm_path.stem
            src_list[
                0
            ] += f"static DS_ERR_CODE {obc_name}_analyze_tlm_{tlm_name.lower()}_(const CommonTlmPacket* packet, {obc_name}_TLM_CODE tlm_id, {driver_type}* {driver_name});\n"
            src_list[
                1
            ] += f"  case {obc_name}_Tlm_CODE_{tlm_name.upper()}:\n    return {obc_name}_analyze_tlm_{tlm_name.lower()}_(&{obc_name}_ctp_, tlm_id, {driver_name});\n"
            src_list[
                2
            ] += f"""
static DS_ERR_CODE {obc_name}_analyze_tlm_{tlm_name.lower()}_(const CommonTlmPacket* packet, {obc_name}_TLM_CODE tlm_id, {driver_type}* {driver_name})
{{
  const uint8_t* f = packet->packet;
  int8_t temp_i8 = 0;
  int16_t temp_i16 = 0;
  int32_t temp_i32 = 0;
  uint8_t temp_u8 = 0;
  uint16_t temp_u16 = 0;
  uint32_t temp_u32 = 0;
  float temp_f = 0.0f;
  double temp_d = 0.0;

  // GS へのテレメ中継のためのバッファーへのコピー
  CTP_copy_packet(&({driver_name}->tlm_buffer.tlm[tlm_id].packet), packet);
  {driver_name}->tlm_buffer.tlm[tlm_id].is_null_packet = 0;
  // TODO: CRC チェック

  // MOBC 内部でテレメデータへアクセスしやすいようにするための構造体へのパース"""
            with open(tlm_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)
                headers = next(reader)
                dict_reader = csv.DictReader(file, fieldnames=headers)
                pos_sum = 0
                last_var_type = ""
                for row in dict_reader:
                    is_compression = False
                    octet_pos = pos_sum // 8
                    bit_pos = pos_sum % 8
                    if not any(row.values()):
                        continue
                    if row["type"] == "":
                        is_compression = True
                        pos_sum += int(row["bit"])
                        row["type"] = last_var_type
                    elif row["type"][0] == "_":
                        is_compression = True
                        pos_sum += int(row["bit"])
                        row["type"] = row["type"].lstrip("_")
                        last_var_type = row["type"]
                    else:
                        pos_sum += conv_type[row["type"]][1] * 8
                    name_tree = row["name"].lower().split(".")
                    for idx, name in enumerate(name_tree):
                        if name[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            name_tree[idx] = f"_{name}"
                    row["name"] = f'{driver_name}->tlm_data.{tlm_name.lower()}.{".".join(name_tree).replace("/", "_")}'
                    if is_compression:
                        src_list[
                            2
                        ] += f"""
  ENDIAN_memcpy(&{conv_type[row['type']][0]}, &(f[{octet_pos}]), {conv_type[row['type']][1]});
  {conv_type[row['type']][0]} >>= {conv_type[row['type']][1] * 8 - bit_pos - int(row['bit'])};
  {conv_type[row['type']][0]} &= {hex(int('0b' + '1' * int(row['bit']), 2))};
  {row["name"]} = {conv_type[row['type']][0]};"""
                    else:
                        src_list[
                            2
                        ] += f"""
  ENDIAN_memcpy(&({row["name"]}), &(f[{octet_pos}]), {conv_type[row['type']][1]});"""
            src_list[
                2
            ] += """
  // TODO: ビットフィールドをつかっている系は，様々なパターンがあり得るので，今後，バグが出ないか注視する

  // ワーニング回避
  (void)temp_i8;
  (void)temp_i16;
  (void)temp_i32;
  (void)temp_u8;
  (void)temp_u16;
  (void)temp_u32;
  (void)temp_f;
  (void)temp_d;

  return DS_ERR_CODE_OK;
}
"""
        else:
            src_list[
                1
            ] += f"""
  default:
    {code_when_tlm_not_found}
    return DS_ERR_CODE_ERR;
  }}
}}
"""[
                1:
            ]
        src_list[
            2
        ] += f"""
TF_TLM_FUNC_ACK {obc_name}_pick_up_tlm_buffer(const {driver_type}* {driver_name}, {obc_name}_TLM_CODE tlm_id, uint8_t* packet, uint16_t* len, uint16_t max_len)
{{
  const CommonTlmPacket* buffered_packet;

  if (tlm_id >= {obc_name}_MAX_TLM_NUM) return TF_TLM_FUNC_ACK_NOT_DEFINED;
  if ({driver_name}->tlm_buffer.tlm[tlm_id].is_null_packet) return TF_TLM_FUNC_ACK_NULL_PACKET;

  buffered_packet = &({driver_name}->tlm_buffer.tlm[tlm_id].packet);
  *len = CTP_get_packet_len(buffered_packet);

  if (*len > max_len) return TF_TLM_FUNC_ACK_TOO_SHORT_LEN;

  memcpy(packet, &buffered_packet->packet, (size_t)(*len));
  return TF_TLM_FUNC_ACK_SUCCESS;
}}

#pragma section
"""
        for src in src_list:
            dest_file.write(src)
