from pathlib import Path

import c2a_generator

root_path = Path(__file__).parent.parent / "sils-docker/sils/FlightSW/c2a-mobc-onglaisat"

# cmd
c2a_generator.cmd_def_c.generate(root_path / "design/cmd.csv", root_path / "src/src_user/TlmCmd/command_definitions.c")
c2a_generator.cmd_def_h.generate(root_path / "design/cmd.csv", root_path / "src/src_user/TlmCmd/command_definitions.h")
c2a_generator.cmd_csv.generate(root_path / "design/cmd.csv", root_path / "database/CMD_DB/ISSL6U_MOBC_CMD_DB_CMD_DB.csv")

# bct
# MRAM 一重領域: 1142 - 1269
# MRAM 三重領域: 1270 - 1279
# BCT MAX : 1280
bct_src = [
    [root_path / "design/bct/bc_sequence_list.csv", 0], # Block Cmds for Mode Transition (シーケンスリスト), ./src_user/Settings/Modes/Transitions/ で定義
    [root_path / "design/bct/bc_task_list.csv", None], # Block Cmds for TaskList (タスクリスト), ./src_user/Settings/Modes/TaskLists/ で定義
    [root_path / "design/bct/bc_app_router.csv", None],
    [root_path / "design/bct/bc_app_combinator.csv", None],
    [root_path / "design/bct/bc_cdh.csv", None],
    [root_path / "design/bct/bc_comm.csv", None],
    [root_path / "design/bct/bc_power.csv", None],
    [root_path / "design/bct/bc_mif.csv", None],
    [root_path / "design/bct/bc_thermal.csv", None],
    [root_path / "design/bct/bc_mram.csv", 1142],
    [root_path / "design/bct/bc_mram_triple.csv", 1270],
]
bc_header_header = """
#include <src_core/TlmCmd/block_command_table.h>
#include <src_core/TlmCmd/block_command_loader.h>
#include <src_core/TlmCmd/common_tlm_packet.h>
#include <src_core/TlmCmd/common_cmd_packet.h>
#include <src_core/System/TimeManager/obc_time.h>
#include <src_core/System/EventManager/event_logger.h>
#include <src_core/Applications/timeline_command_dispatcher_id_define.h>

#include "../block_command_definitions.h"
#include "../telemetry_definitions.h"
#include "../command_definitions.h"
#include "../../Settings/Modes/mode_definitions.h"
#include "../../Settings/System/EventHandlerRules/event_handler_rules.h"
#include "../../Settings/port_config.h"
#include "../../Drivers/Aocs/aobc_command_definitions.h"
#include "../../Drivers/Thermal/tobc_command_definitions.h"
#include "../../Drivers/Mission/mif_command_definitions.h"
#include "../../Drivers/Mission/mif_telemetry_definitions.h"
#include "../../Applications/app_registry.h"
#include "../../Applications/UserDefined/Com/comm_fdir.h"

#define EL_LOG_DR_PARTITION (7)
#define TL_TLM_DR_PARTITION (8)
"""[1:]

c2a_generator.bct_def_c.generate(bct_src, root_path / "src/src_user/TlmCmd/block_command_definitions.c", bc_header_header)
c2a_generator.bct_def_h.generate(bct_src, root_path / "src/src_user/TlmCmd/block_command_definitions.h")
c2a_generator.bct_csv.generate(bct_src, root_path / "database/CMD_DB/ISSL6U_MOBC_CMD_DB_BCT.csv")

# tlm
tlm_path = root_path / "design/tlm"
c2a_generator.tlm_def_h.generate(tlm_path, root_path / "src/src_user/TlmCmd/telemetry_definitions.h")
c2a_generator.tlm_def_c.generate(tlm_path, root_path / "src/src_user/TlmCmd/telemetry_definitions.c")
c2a_generator.tlm_csv.generate(tlm_path, root_path / "database/TLM_DB", prefix="ISSL6U_MOBC_TLM_DB_")

# wings
c2a_generator.wings_json.generate(bct_src, root_path / "../../../wings/aspnetapp/WINGS/ClientApp/src/assets/alias/c2a_onglai.json")
