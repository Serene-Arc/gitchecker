#!/usr/bin/env python3
# coding=utf-8

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from queue import Queue

from colorama import Style

parser = argparse.ArgumentParser()
logger = logging.getLogger()


def _setup_logging(verbosity: int):
    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] - %(message)s")
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    if verbosity > 0:
        stream.setLevel(logging.DEBUG)
    else:
        stream.setLevel(logging.INFO)


def _add_arguments():
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    parser.add_argument("directories", nargs="+")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")


def main(args: argparse.Namespace):
    _setup_logging(args.verbosity)
    args.directories = [Path(d).expanduser().resolve() for d in args.directories]
    git_directories = []
    if args.recursive:
        master_queue = Queue()
        for place in args.directories:
            master_queue.put(place)
        while not master_queue.empty():
            if rs := recurse_directory(master_queue.get()):
                for subdir in rs:
                    if Path(subdir, ".git/").exists():
                        git_directories.append(subdir)
                    else:
                        master_queue.put(subdir)
    else:
        git_directories = args.directories

    git_directories = [g.expanduser().resolve() for g in git_directories if g.is_dir()]
    for git_dir in git_directories:
        output = subprocess.run(
            "git -c color.status=always status", shell=True, capture_output=True, text=True, cwd=git_dir
        )
        if git_not_finalised(output):
            if args.quiet:
                print(git_dir)
            else:
                print(Style.BRIGHT + str(git_dir) + Style.RESET_ALL)
                print(output.stdout)


def recurse_directory(root_directory: Path) -> list[Path]:
    check_dir = Path(root_directory, ".git/")
    if check_dir.exists():
        return [check_dir]
    else:
        subdirectories = filter(lambda d: d.is_dir(), root_directory.iterdir())
        return list(subdirectories)


def git_not_finalised(output: subprocess.CompletedProcess[str]) -> bool:
    if output.returncode != 0:
        return False
    if "nothing to commit, working tree clean" not in output.stdout or any(
        [s in output.stdout for s in ("branch is ahead", "branch is behind")]
    ):
        return True


def entry():
    _add_arguments()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    entry()
