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

import copy
import subprocess
import warnings
from typing import Callable, Literal

from robo_orchard_build.ext.build_ext import RoboOrcahrdExtension

__all__ = ["BlackExtension"]


class BlackExtension(RoboOrcahrdExtension):
    SKIP_RUN: bool = True

    def __init__(
        self,
        name: str,
        find_file_callback: Callable[[], list[str]],
        target_version: Literal[
            "py36", "py37", "py38", "py39", "py310", "py311", "py312", "py313"
        ] = "py310",
        pyi: bool = True,
        include: str = "",
        config_file: str = "",
        line_length: int = 79,
        quiet: bool = False,
        verbose: bool = False,
        *args,
        **kwargs,
    ):
        import black  # This line to check pybind11 stubgen is installed.  # noqa: F401, E501

        super().__init__(*args, name=name, sources=[], **kwargs)
        self._target_version = target_version
        self._pyi = pyi
        self._config_file = config_file
        self._line_length = line_length
        self._find_file_callback = find_file_callback
        self._include = include
        self._quiet = quiet
        self._verbose = verbose

    def after_run(self):
        # should implement the after_run method
        cmd = []

        cmd.append("black")
        cmd.extend(
            [
                "--line-length",
                str(self._line_length),
                "-t",
                self._target_version,
            ]
        )
        if self._pyi:
            cmd.append("--pyi")

        if self._include != "":
            cmd.extend(["--include", f'"{self._include}'])
        if self._config_file != "":
            cmd.extend(["--config", self._config_file])
        if self._verbose:
            cmd.append("--verbose")
        if self._quiet:
            cmd.append("--quiet")

        files = self._find_file_callback()
        if len(files) == 0:
            warnings.warn("No files found to sort imports.")
            return

        new_cmd = copy.deepcopy(cmd)
        new_cmd.extend(files)
        try:
            subprocess.check_call(" ".join(new_cmd), shell=True)
        except Exception as e:
            raise e


class ISortExtension(RoboOrcahrdExtension):
    SKIP_RUN: bool = True

    """ISortExtension is used to sort imports in python files. """

    def __init__(
        self,
        name: str,
        find_file_callback: Callable[[], list[str]],
        profile: str = "",
        settings_path: str = "",
        quiet: bool = False,
        verbose: bool = False,
        *args,
        **kwargs,
    ):
        import isort  # This line to check pybind11 stubgen is installed.  # noqa: F401, E501

        super().__init__(*args, name=name, sources=[], **kwargs)

        self._profile = profile
        self._find_file_callback = find_file_callback
        self._settings_path = settings_path
        self._quiet = quiet
        self._verbose = verbose

    def after_run(self):
        # should implement the after_run method
        cmd = []

        cmd.extend(
            [
                "isort",
            ]
        )
        if self._profile != "":
            cmd.extend(["--profile", self._profile])
        if self._settings_path != "":
            cmd.extend(["--settings-path", self._settings_path])
        if self._verbose:
            cmd.append("--verbose")
        if self._quiet:
            cmd.append("--quiet")
        files = self._find_file_callback()

        if len(files) == 0:
            warnings.warn("No files found to sort imports.")
            return

        cmd.extend(files)

        try:
            subprocess.check_call(" ".join(cmd), shell=True)
        except Exception as e:
            raise e
