from pathlib import Path


def generate(src_path: Path, dest_path: Path, obc_name: str, driver_type: str, driver_name: str, max_tlm_num: int) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            f"""
/**
 * @file
 * @brief  テレメトリバッファー（テレメ中継）
 * @note   このコードは自動生成されています！
 */
#ifndef {obc_name}_TELEMETRY_BUFFER_H_
#define {obc_name}_TELEMETRY_BUFFER_H_

#include "./{obc_name.lower()}_telemetry_definitions.h"
#include <src_core/Drivers/Super/driver_super.h>
#include <src_core/TlmCmd/common_tlm_packet.h>
#include <src_core/TlmCmd/telemetry_frame.h>

typedef struct {driver_type} {driver_type};

#define {obc_name}_MAX_TLM_NUM ({max_tlm_num})

typedef struct
{{
  CommonTlmPacket packet;   //!< 最新のテレメパケットを保持
  uint8_t is_null_packet;   //!< 一度でもテレメを受信しているか？（空配列が読み出されるのを防ぐため）
}} {obc_name}_TlmBufferElem;

typedef struct
{{
  {obc_name}_TlmBufferElem tlm[{obc_name}_MAX_TLM_NUM];   //!< TLM ID ごとに保持
}} {obc_name}_TlmBuffer;

void {obc_name}_init_tlm_buffer({driver_type}* {driver_name});

DS_ERR_CODE {obc_name}_buffer_tlm_packet(DS_StreamConfig* p_stream_config, {driver_type}* {driver_name});

TF_TLM_FUNC_ACK {obc_name}_pick_up_tlm_buffer(const {driver_type}* {driver_name}, {obc_name}_TLM_CODE tlm_id, uint8_t* packet, uint16_t* len, uint16_t max_len);

#endif
"""[
                1:
            ]
        )
