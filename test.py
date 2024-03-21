from pathlib import Path

import c2a_generator

root_path = Path(__file__).parent.parent / "sils-docker/sils/FlightSW/c2a-mobc-onglaisat"

# cmd
c2a_generator.cmd_def_h.generate(root_path / "design/cmd.csv", root_path / "src/src_user/TlmCmd/command_definitions.h")
c2a_generator.cmd_csv.generate(root_path / "design/cmd.csv", root_path / "database/CMD_DB/ISSL6U_MOBC_CMD_DB_CMD_DB.csv")

# bct
bct_path = root_path / "design/bct.csv"
bct_src = [
    [root_path / "design/bct/sram/sl.csv", 0],
    [root_path / "design/bct/sram/tl.csv", None],[root_path / "design/bct/sram/bc.csv", None],[root_path / "design/bct/mram.csv", 1142],
    [root_path / "design/bct/mram_triple.csv", 1270],
]

c2a_generator.bct_def_h.generate(bct_src, root_path / "src/src_user/TlmCmd/block_command_definitions.h")
c2a_generator.bct_csv.generate(bct_src, root_path / "database/CMD_DB/ISSL6U_MOBC_CMD_DB_BCT.csv")

# tlm
tlm_path = root_path / "design/tlm"
c2a_generator.tlm_def_h.generate(tlm_path, root_path / "src/src_user/TlmCmd/telemetry_definitions.h")
c2a_generator.tlm_def_c.generate(tlm_path, root_path / "src/src_user/TlmCmd/telemetry_definitions.c")
c2a_generator.tlm_csv.generate(tlm_path, root_path / "database/TLM_DB/calced_data", prefix="ISSL6U_MOBC_TLM_DB_")

