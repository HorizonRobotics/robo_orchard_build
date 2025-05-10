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

import os
import subprocess

from robo_orchard_build.ext.build_ext import RoboOrcahrdExtension
from robo_orchard_build.utils.file import scan_folder

__all__ = ["Pybind11StubgenExtension"]


class Pybind11StubgenExtension(RoboOrcahrdExtension):
    SKIP_RUN: bool = True

    """This class is used to generate pyi files for pybind11 modules.

    Args:
        name (str): The name of the extension.
        module_name (str): The name of the module to generate pyi files for.
        pwd (str, optional): The working directory to run the command.
            Defaults to "".
        output_dir (str, optional): The output directory for the generated
            pyi files. Defaults to "".
        root_suffix (str, optional): The root suffix for the generated pyi files.
            Defaults to "".
        dry_run (bool, optional): If True, the command will not be executed.
            Defaults to False.
        ignore_unresolved_names (str, optional): A comma-separated list of
            unresolved names to ignore. Defaults to "".
        enum_class_locations (str | list[str], optional): A comma-separated list
            of locations to search for enum classes. Defaults to "".
        ignore_all_errors (bool, optional): If True, ignore all errors.
            Defaults to False.
        quiet (bool, optional): If True, do not print output to stdout.
            Defaults to False.
        log_file (str, optional): The log file to write output to.
            Defaults to "".
        target_package_import_from (str, optional): The package to import the
            module from. If provided, the package import will be modified in the
            generated pyi files to import the module from this package.
            Defaults to "".
    """  # noqa: E501

    def __init__(
        self,
        name: str,
        module_name: str,
        pwd: str = "",
        output_dir: str = "",
        root_suffix: str = "",
        dry_run: bool = False,
        ignore_unresolved_names: str = "",
        enum_class_locations: str | list[str] = "",
        ignore_all_errors: bool = False,
        quiet: bool = False,
        log_file: str = "",
        target_package_import_from: str = "",
        *args,
        **kwargs,
    ):
        import pybind11_stubgen  # This line to check pybind11 stubgen is installed.  # noqa: F401, E501

        super().__init__(*args, name=name, sources=[], **kwargs)
        self._output_dir = output_dir
        self._root_suffix = root_suffix
        self._dry_run = dry_run
        self._module_name = module_name
        self._quiet = quiet
        self._ignore_unresolved_names = ignore_unresolved_names
        self._ignore_all_errors = ignore_all_errors
        self._enum_class_locations = (
            enum_class_locations
            if isinstance(enum_class_locations, list)
            else [
                enum_class_locations,
            ]
        )
        # remove empty string
        self._enum_class_locations = list(
            filter(lambda x: x != "", self._enum_class_locations)
        )

        self._pwd = pwd
        if self._quiet and log_file == "":
            raise ValueError("log_file is required when quiet is True")
        self._log_file = log_file

        self._target_package_import_from = target_package_import_from

    def after_run(self):
        # should implement the after_run method
        cmd = []

        if self._pwd != "":
            cmd.append(f"PYTHONPATH={self._pwd}:$PYTHONPATH  ")

        cmd.append("pybind11-stubgen")
        if self._output_dir != "":
            cmd.extend(["-o", self._output_dir])
        if self._root_suffix != "":
            cmd.extend(["--root-suffix", self._root_suffix])
        if self._dry_run:
            cmd.append("--dry-run")

        if self._ignore_unresolved_names != "":
            cmd.extend(
                ["--ignore-unresolved-names", self._ignore_unresolved_names]
            )
        for loc in self._enum_class_locations:
            cmd.extend(["--enum-class-locations", loc])

        if self._ignore_all_errors:
            cmd.append("--ignore-all-errors")

        if self._quiet:
            cmd.append(f" >> {self._log_file} ")

        cmd.extend(["--exit-code", self._module_name])

        try:
            subprocess.check_call(" ".join(cmd), shell=True)
        except Exception as e:
            if self._quiet:
                print(f"Failed to run pybind11-stubgen: {e}")
                print(f"Check log file {self._log_file} for more information.")
            raise e

        if self._target_package_import_from != "":
            self.modify_package_import()

    def modify_package_import(self):
        output_dir = os.path.join(self._output_dir, self._module_name)
        # find all pyi files
        pyi_files = scan_folder(
            output_dir,
            ending=[".pyi"],
            recursive=True,
            list_files=True,
            list_folders=False,
        )
        # modify package import for any pyi file:
        # Find any line that start with `import {self._module_name}`
        # Delete this line
        # Add `from {self._target_package_import_from} import {self._module_name}`  # noqa: E501
        # to the file if any line is deleted

        for pyi_file in pyi_files:
            with open(pyi_file, "r") as f:
                lines = f.readlines()
            new_lines = []
            to_insert_line = -1
            for i, line in enumerate(lines):
                if line.startswith(f"import {self._module_name}"):
                    if to_insert_line < 0:
                        to_insert_line = i
                    continue
                new_lines.append(line)
            if len(new_lines) != len(lines):
                new_lines.insert(
                    to_insert_line,
                    f"from {self._target_package_import_from} "
                    f"import {self._module_name}\n",
                )
                with open(pyi_file, "w") as f:
                    f.writelines(new_lines)
