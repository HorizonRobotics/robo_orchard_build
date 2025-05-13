# Project RoboOrchard
#
# Copyright (c) 2024 Horizon Robotics. All Rights Reserved.
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

import os
from typing import Iterable, Optional


def scan_folder(
    folder: str,
    ending: Optional[str | list[str]] = None,
    recursive: bool = False,
    list_folders: bool = True,
    list_files: bool = True,
    max_depth: Optional[int] = None,
    exclude_dir: Iterable[str] = (),
    verbose: bool = False,
) -> Iterable[str]:
    """Find files in a folder.

    Args:
        folder (str): The folder to scan.
        ending (str|list[str], optional): The file ending. Defaults to None.
        recursive (bool, optional): Whether to scan recursively.
            Defaults to False.
        list_folders (bool, optional): Whether to list folders.
            Defaults to True.
        list_files (bool, optional): Whether to list files. Defaults to True.
        max_depth (Optional[int], optional): The maximum depth to scan.
            If None, scan all. Defaults to None.
        exclude_dir (Iterable[str], optional): The directories to exclude.
            Defaults to ().
        verbose (bool, optional): Whether to print the excluded directories.
            Defaults to False.

    Returns:
        Iterable[str]: The file paths.
    """

    if isinstance(ending, str):
        ending = [
            ending,
        ]

    def is_target(file: str) -> bool:
        if os.path.isdir(file) and not list_folders:
            return False
        if os.path.isfile(file) and not list_files:
            return False
        if ending is None:
            return True
        else:
            return any(file.endswith(e) for e in ending)

    for root, dirs, files in os.walk(folder):
        if root in exclude_dir:
            if verbose:
                print(f"Skipping excluded directory: {root}")
            dirs[:] = []  # Do not traverse this folder
            continue
        if max_depth is not None and max_depth > 0:
            depth = root[len(folder) + 1 :].count(os.sep)  # noqa
            if depth >= max_depth:
                if verbose:
                    print(f"Skipping directory {root} due to max depth")
                dirs[:] = []
                continue

        for file in dirs + files:
            full_path = os.path.join(root, file)
            if is_target(full_path):
                yield full_path

        if max_depth == 0 or recursive is None:
            break
