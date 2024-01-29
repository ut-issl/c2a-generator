import argparse
from pathlib import Path

import c2a
import toml

# generate_bct_def, generate_cmd_def_c, generate_cmd_def_h, generate_tlm_def_c, generate_tlm_def_h

root_path = Path(__file__).parent.parent
toml_path = root_path / "config.toml"
config = toml.load(toml_path)
assert config.get("obc") is not None, "obc is not defined in config.toml"


def main() -> None:
    parser = argparse.ArgumentParser(description="Python Script with --subobc option")
    parser.add_argument("--subobc", type=bool, default=False, help="Specify True or False for --subobc option")
    args = parser.parse_args()

    for obc in config["obc"]:
        if obc.get("is_main_obc"):
            c2a.bct_def.generate(root_path / obc["bct_src"], root_path / obc["bct_dest"])
            c2a.cmd_def_h.generate(root_path / obc["cmd_src"], root_path / obc["cmd_dest_h"])
            c2a.cmd_def_c.generate(root_path / obc["cmd_src"], root_path / obc["cmd_dest_c"])
            c2a.tlm_def_h.generate(root_path / obc["tlm_src"], root_path / obc["tlm_dest_h"])
            c2a.tlm_def_c.generate(root_path / obc["tlm_src"], root_path / obc["tlm_dest_c"])

        if (not obc.get("is_main_obc")) and args.subobc:
            print("Hogehoge")


if __name__ == "__main__":
    main()
