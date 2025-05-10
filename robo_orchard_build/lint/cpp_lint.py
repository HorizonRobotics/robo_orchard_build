# Project RoboOrchard
#
# Copyright (c) 2025 Horizon Robotics. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import argparse
import os
import subprocess

from robo_orchard_build.utils.file import scan_folder


def process(fname: str, clang_format_args: list[str]):
    """Process a file."""
    subprocess.check_call(["clang-format", *clang_format_args, fname])


def main():
    """Main entry function."""
    parser = argparse.ArgumentParser(
        description="Lint cpp source codes with clang-format."
        "The script will traverse the path and lint all the files "
        "with the suffix of .cc, .c, .cpp, .h, .cu, .hpp, "
        "and format code if --auto_format is set. "
        "The configuration of clang-format is Google style."
    )
    parser.add_argument(
        "--path",
        nargs="+",
        default=[],
        help="path to traverse",
        required=False,
    )
    parser.add_argument(
        "--exclude_path",
        nargs="+",
        default=[],
        help="exclude this path, and all subfolders " + "if path is a folder",
    )
    # add arguments for whether to auto format
    parser.add_argument(
        "--auto_format",
        action="store_true",
        help="whether to auto format code",
    )

    # check if clang-format is installed and disable the output
    try:
        subprocess.check_output(
            ["clang-format", "--version"], stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "clang-format is not installed! "
            "You can install it with pip install clang-format"
        )

    args = parser.parse_args()
    CXX_SUFFIX = set(["cc", "c", "cpp", "h", "cu", "hpp"])
    allow_type: list[str] = []
    allow_type += [x for x in CXX_SUFFIX]
    allow_type = ["." + x for x in allow_type]

    clang_foramt_args = [
        "--style=Google",
        "--Werror",
    ]
    if not args.auto_format:
        clang_foramt_args.append("--dry-run")
    else:
        clang_foramt_args.append("-i")

    for path in args.path:
        if os.path.isfile(path):
            process(path, clang_foramt_args)
        else:
            for file in scan_folder(
                path,
                ending=allow_type,
                recursive=True,
                list_folders=False,
                list_files=True,
                exclude_dir=args.exclude_path,
            ):
                process(file, clang_foramt_args)


if __name__ == "__main__":
    main()
