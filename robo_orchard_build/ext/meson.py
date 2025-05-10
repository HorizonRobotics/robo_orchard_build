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

import importlib
import os
import subprocess
import sys
import types
from dataclasses import dataclass
from typing import Optional

from robo_orchard_build.ext.build_ext import (
    RoboOrcahrdExtension,
    RoboOrchardBuildExt,
    get_file_content,
)

__all__ = ["CppModuleInfo", "MesonExtension", "load"]


@dataclass
class CppModuleInfo:
    """CppModuleInfo is a dataclass to store information of a C++ module."""

    name: str
    include_dir: str
    src_dir: Optional[str]
    license_file: Optional[str] = None

    def copy_files_to(self, dst: "CppModuleInfo", link: bool = False):
        """Copy files from this module to another module.

        Args:
            dst (CppModuleInfo): the destination module.
            link (bool): whether to create symlink instead of copying files.
        """
        if not os.path.exists(dst.include_dir):
            os.makedirs(dst.include_dir)
        if not link:
            subprocess.check_call(
                f"cp -rf {self.include_dir}/* {dst.include_dir}", shell=True
            )
        else:
            for f in os.listdir(self.include_dir):
                src_file = os.path.join(self.include_dir, f)
                dst_file = os.path.join(dst.include_dir, f)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                os.symlink(src_file, dst_file)

        if self.src_dir is not None:
            assert dst.src_dir is not None
            if not os.path.exists(dst.src_dir):
                os.makedirs(dst.src_dir)
            if not link:
                subprocess.check_call(
                    f"cp -rf {self.src_dir}/* {dst.src_dir}", shell=True
                )
            else:
                for f in os.listdir(self.src_dir):
                    src_file = os.path.join(self.src_dir, f)
                    dst_file = os.path.join(dst.src_dir, f)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    os.symlink(src_file, dst_file)

        if self.license_file is not None:
            assert dst.license_file is not None
            subprocess.check_call(
                f"cp -rf {self.license_file} {dst.license_file}", shell=True
            )


class MesonExtension(RoboOrcahrdExtension):
    """A custom extension class for Meson build system.

    This extension will generate a meson.build file from a Jinja2
    template and build the extension using Meson build system.

    The compiled library will be installed to a specified directory,
    or the same directory as the extension file if not specified.

    The target path of the compiled library usually will be:

    - If `with_python` is True, the recommended target name and path is
    `{install_dir}/{name}.cython-3.10.so`. The target name and path varies
    depending on the implementation of meson build file.
    - If `with_python` is False, we recommend the target name and path to be
    `{install_dir}/lib{name}.so`. The target name and path varies depending on
    the implementation of meson build file.

    Args:
        name (str): The name of the extension.
        jinja2_args (dict): The arguments to pass to the Jinja2 template.
        jinja2_template_path (str): The path to the Jinja2 template.
        with_python (bool): Whether the extension is a python extension. This
            will affect the target path of the compiled library.
        install_dir (Optional[str], optional): The directory to install the
            compiled library. If not specified, the library will be installed
            to the directory of `dirname(get_ext_fullpath(self.name))`.
        verbose (bool, optional): Whether to run meson in verbose mode.
            Defaults to False.
        quiet (bool, optional): Whether to run meson in quiet mode. If
            True, the output of meson command will be redirected to a log
            file. Defaults to False.
        *args: Additional arguments to pass to the parent class.
        **kwargs: Additional keyword arguments to pass to the parent class.
    """

    SKIP_RUN: bool = False

    def __init__(
        self,
        name: str,
        jinja2_args: dict,
        jinja2_template_path: str,
        with_python: bool,
        install_dir: Optional[str] = None,
        verbose: bool = False,
        quiet: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, name=name, sources=[], **kwargs)

        if not os.path.exists(jinja2_template_path):
            raise FileNotFoundError(
                f"Jinja2 template {jinja2_template_path} does not exist."
            )
        self.with_python = with_python
        self._jinj2_args = jinja2_args
        self._jinja2_template_path = jinja2_template_path
        self.install_dir: Optional[str] = install_dir
        self.quiet = quiet
        self.verbose = verbose
        self.meson_build_path = ""

    def generate_meson_build_from_jinja2(self):
        """Generate meson.build file from Jinja2 template."""
        jinja2_template_path = self._jinja2_template_path
        import jinja2

        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                searchpath=os.path.dirname(jinja2_template_path)
            )
        )

        template = self.template_env.get_template(
            os.path.basename(jinja2_template_path)
        )
        return template.render(**self._jinj2_args)

    def _strip_ext_midfix(self, ext_path: str) -> str:
        """Strip the middle part of the extension path.

        The middle part is usually the python version info. If the
        target is not a python extension, this function will remove
        the middle part to be a standard library name.
        """
        folder, file = os.path.split(ext_path)
        file = file.split(".")
        return os.path.join(folder, ".".join([file[0], file[-1]]))

    def _get_meson_build_file_path(self, ext_fullpath: str) -> str:
        # get_ext_fullpath usually returns something like
        # 'lib.linux-x86_64-cpython-310/{self.get_ext_filename()}'
        ext_path = ext_fullpath
        build_folder = os.path.dirname(ext_path) + "-meson"
        return os.path.join(build_folder, self.name, "meson.build")

    def _is_meson_configured(self, ext_fullpath: str) -> bool:
        build_file = self._get_meson_build_file_path(ext_fullpath)
        core_file = os.path.join(
            os.path.split(build_file)[0],
            "build",
            "meson-private",
            "coredata.dat",
        )
        return os.path.exists(core_file)

    def get_meson_install_dir(self, ext_fullpath: str) -> str:
        if self.install_dir is not None:
            return self.install_dir
        return os.path.abspath(os.path.dirname(ext_fullpath))

    def _meson_build_extension(
        self,
        build_ext: RoboOrchardBuildExt,
        ext_meson_file_path: str,
        log_file: str,
    ) -> None:
        need_reconfigure = False
        ext_fullpath = build_ext.get_ext_fullpath(self.name)
        ext_filename = build_ext.get_ext_filename(self.name)
        # update install_dir
        install_dir = self.get_meson_install_dir(ext_fullpath=ext_fullpath)
        self.install_dir = install_dir
        if not os.path.exists(install_dir):
            os.mkdir(install_dir)
            assert os.path.exists(install_dir)

        meson_folder = os.path.dirname(ext_meson_file_path)
        meson_content = self.generate_meson_build_from_jinja2()
        old_meson_content = get_file_content(ext_meson_file_path)
        if (
            isinstance(old_meson_content, str)
            and old_meson_content == meson_content
        ):
            pass
        else:
            with open(ext_meson_file_path, "w") as f:
                f.write(meson_content)
                need_reconfigure = True

        if need_reconfigure or (
            not self._is_meson_configured(ext_fullpath=ext_fullpath)
        ):
            meson_cmd = [
                "meson",
                "setup",
                f"{meson_folder}/build",
                f"{meson_folder}",
            ]
            if need_reconfigure:
                meson_cmd.append("--reconfigure")
            if self.quiet:
                meson_cmd.append(f" >> {log_file} ")

            subprocess.check_call(" ".join(meson_cmd), shell=True)

        # run meson build command everytime to make sure the
        # library is up-to-date
        meson_cmd = ["meson", "compile", "-C", f"{meson_folder}/build"]
        if self.verbose:
            meson_cmd.append("--verbose")
        if self.quiet:
            meson_cmd.append(f">> {log_file}")

        subprocess.check_call(" ".join(meson_cmd), shell=True)

        target_lib = ext_filename
        ext_fullpath = ext_fullpath
        if not self.with_python:
            target_lib = self._strip_ext_midfix(target_lib)
            ext_fullpath = self._strip_ext_midfix(ext_fullpath)

        # skip copy operation if the library is up-to-date
        # install if target does not exist or target is older
        # than the compiled library
        if (
            (not os.path.exists(install_dir))
            or (not os.path.exists(ext_fullpath))
            or (
                os.stat(
                    os.path.join(meson_folder, "build", target_lib)
                ).st_mtime
                > os.stat(ext_fullpath).st_mtime
            )
        ):
            # run meson install command
            meson_cmd = [
                "meson",
                "install",
                "-C",
                f"{meson_folder}/build",
                "--destdir",
                f"{install_dir}",
            ]

            if self.quiet:
                meson_cmd.append(f">> {log_file}")
            subprocess.check_call(" ".join(meson_cmd), shell=True)

    def build(self, build_ext: RoboOrchardBuildExt):
        ext_fullpath = build_ext.get_ext_fullpath(self.name)
        # configure meson_build_path
        ext_meson_file_path = self._get_meson_build_file_path(
            ext_fullpath=ext_fullpath
        )
        meson_folder = os.path.dirname(ext_meson_file_path)
        self.meson_build_path = meson_folder

        if not os.path.exists(meson_folder):
            os.makedirs(meson_folder)
            assert os.path.exists(meson_folder)

        file_lock_path = ext_meson_file_path + ".lock"
        log_file = f"{meson_folder}/build_log.txt"
        # create empty log file:
        with open(log_file, "w") as f:
            f.write("")

        import filelock

        with filelock.FileLock(file_lock_path):
            try:
                self._meson_build_extension(
                    build_ext=build_ext,
                    ext_meson_file_path=ext_meson_file_path,
                    log_file=log_file,
                )
            except Exception as e:
                print(f"Failed to build extension {self.name}: {e}. ")
                if self.quiet:
                    print(f"Check log file {log_file} for more information.")
                raise e


def load(ext: MesonExtension) -> types.ModuleType:
    """Load a meson extension as a python module by JIT compiling it.

    This function will build the extension and install it to a
    temporary directory. Then it will import the module from the
    temporary directory.

    Args:
        ext (MesonExtension): The extension to load.

    Returns:
        types.ModuleType: The loaded module.
    """
    assert isinstance(ext, MesonExtension)
    assert ext.with_python, "with_python must be True"
    assert ext.SKIP_RUN is False, "SKIP_RUN must be False"

    from setuptools import setup

    _ = setup(
        ext_modules=[
            ext,
        ],
        cmdclass={"build_ext": RoboOrchardBuildExt},
        zip_safe=False,
        script_args=["build", "-q"],
    )
    assert ext.install_dir is not None, "install_dir must be set"
    if ext.install_dir not in sys.path:
        sys.path.append(ext.install_dir)
    module = importlib.import_module(ext.name)
    if sys.path[-1] == ext.install_dir:
        sys.path.pop()
    return module
