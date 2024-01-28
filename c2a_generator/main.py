import toml
import argparse
from pathlib import Path
from load import load_cmd
from generate import generate_cmd_def_h, generate_bct_def, generate_cmd_def_c, generate_tlm_def_h, generate_tlm_def_c

root_path = Path(__file__).parent.parent
toml_path = root_path / "config.toml"
config = toml.load(toml_path)
assert config.get("obc") is not None, "obc is not defined in config.toml"

def main():
    parser = argparse.ArgumentParser(description='Python Script with --subobc option')
    parser.add_argument('--subobc', type=bool, default=False, help='Specify True or False for --subobc option')
    args = parser.parse_args()

    for obc in config["obc"]:
        if obc.get("is_main_obc"):
            generate_bct_def(root_path / obc["bct_src"], root_path / obc["bct_dest"])
            generate_cmd_def_h(root_path / obc["cmd_src"], root_path / obc["cmd_dest_h"])
            generate_cmd_def_c(root_path / obc["cmd_src"], root_path / obc["cmd_dest_c"])
            generate_tlm_def_h(root_path / obc["tlm_src"], root_path / obc["tlm_dest_h"])
            generate_tlm_def_c(root_path / obc["tlm_src"], root_path / obc["tlm_dest_c"])

        if (not obc.get("is_main_obc")) and args.subobc:
            print("Hogehoge")

if __name__ == "__main__":
    main()
