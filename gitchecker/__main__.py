#!/usr/bin/env python3
# coding=utf-8

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from queue import Queue
from typing import Optional

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


def main(args: argparse.Namespace):
    _setup_logging(args.verbosity)
    args.directories = [Path(d).expanduser().resolve() for d in args.directories]
    for place in args.directories:
        if args.recursive:
            master_queue = Queue()
            master_queue.put(place)
            while not master_queue.empty():
                if rs := recurse_directory(master_queue.get()):
                    [master_queue.put(r) for r in rs]
        else:
            check_git_status_directory(place)


def recurse_directory(root_directory: Path) -> Optional[list[Path]]:
    check_dir = Path(root_directory, ".git/")
    if check_dir.exists():
        check_git_status_directory(root_directory)
    else:
        subdirectories = filter(lambda d: d.is_dir(), root_directory.iterdir())
        return list(subdirectories)


def check_git_status_directory(place: Path):
    if place.is_dir():
        output = subprocess.run(
            "git -c color.status=always status", shell=True, capture_output=True, text=True, cwd=place
        )
        if output.returncode != 0:
            return
        if "nothing to commit, working tree clean" not in output.stdout or any(
            [s in output.stdout for s in ("branch is ahead", "branch is behind")]
        ):
            print(Style.BRIGHT + str(place) + Style.RESET_ALL)
            print(output.stdout)


def entry():
    _add_arguments()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    entry()
