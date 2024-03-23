import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def get_git_file_blob_url(src_path: Path) -> str:
    """Get the GitHub repository URL, current commit hash, and repository root path."""
    try:
        # Fetching the GitHub repository URL
        os.chdir(src_path.parent)
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip().decode()
        if len(remote_url) > 3 and remote_url[:4] == "git@":
            remote_url = remote_url.replace(":", "/").replace("git@", "https://")
        parsed_url = urlparse(remote_url)
        repo_url = f"https://github.com{parsed_url.path}"[:-4]

        # Fetching the current commit hash
        commit_hash = subprocess.check_output(["git", "log", "-n", "1", "--pretty=format:%H", str(src_path)]).strip().decode()


        # Fetching the Git repository root path
        repo_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode())
    except subprocess.CalledProcessError:
        # Handle errors if Git commands fail
        raise EnvironmentError("Unable to fetch Git repository info")

    if repo_url is None or commit_hash is None or repo_root is None:
        raise EnvironmentError("Unable to fetch Git repository info")
    # Resolve the absolute path of src_path and compute its relative path from the repo root
    absolute_src_path = Path(src_path).resolve()
    relative_src_path = absolute_src_path.relative_to(repo_root)
    # Construct the file's blob permalink
    file_blob_url = f"{repo_url}/blob/{commit_hash}/{relative_src_path}"
    return file_blob_url
