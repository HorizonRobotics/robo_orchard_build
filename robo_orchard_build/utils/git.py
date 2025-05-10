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

import datetime
import os
import subprocess
from typing import Optional


def get_commit_datetime(
    fmt: str = "%Y%m%d%H%M%S", cwd: str | None = None
) -> Optional[str]:
    """Get the commit datetime in the format of fmt.

    Args:
        fmt (str, optional): The datetime format. Defaults to "%Y%m%d%H%M%S".
        cwd (str | None, optional): The working directory. If None, use the
            current directory. Defaults to None.
    """
    if cwd is None:
        cwd = os.path.curdir
    try:
        commit_datetime = (
            subprocess.check_output(
                ["git", "show", "-s", "--format=%ci"], cwd=cwd
            )
            .decode("ascii")
            .strip()
        )
    except Exception:
        print("Failed to get commit datetime")
        return None
    ret = datetime.datetime.strptime(commit_datetime, "%Y-%m-%d %H:%M:%S %z")
    # convert to string format
    return ret.strftime("%Y%m%d%H%M%S")


def get_commit_id(short: bool = True, cwd: str | None = None) -> Optional[str]:
    """Get the commit id.

    Args:
        short (bool, optional): Whether to use the short commit id.
            Defaults to True.
        cwd (str | None, optional): The working directory. If None, use the
            current directory. Defaults

    """
    if cwd is None:
        cwd = os.path.curdir
    try:
        cmd = (
            ["git", "rev-parse", "--short", "HEAD"]
            if short
            else ["git", "rev-parse", "HEAD"]
        )
        commit_id = (
            subprocess.check_output(cmd, cwd=cwd).decode("ascii").strip()
        )
    except Exception:
        print("Failed to get commit id")
        return None
    return commit_id


def get_show_commit_files(
    commit_id: str, cwd: str | None = None
) -> list[str] | None:
    """Get the files of a commit.

    Args:
        commit_id (str): The commit id.
        cwd (str | None, optional): The working directory. If None, use the
            current directory. Defaults to None.
    """
    if cwd is None:
        cwd = os.path.curdir
    try:
        commit_files = (
            subprocess.check_output(
                ["git", "show", "--name-only", "--pretty=", commit_id],
                cwd=cwd,
            )
            .decode("ascii")
            .strip()
        )
    except Exception:
        print("Failed to get commit files")
        return None

    return commit_files.split("\n")
