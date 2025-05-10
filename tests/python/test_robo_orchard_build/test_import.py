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

import pytest


class TestImportExt:
    def test_import_build_ext(self):
        from robo_orchard_build.ext.build_ext import (
            RoboOrcahrdExtension,  # noqa: F401
        )

    def test_import_lint(self):
        from robo_orchard_build.ext.lint import BlackExtension  # noqa: F401

    def test_import_meson(self):
        from robo_orchard_build.ext.meson import MesonExtension  # noqa: F401

    def test_import_protobuf(self):
        from robo_orchard_build.ext.protobuf import (
            ProtocolExtension,  # noqa: F401
        )

    def test_import_stubgen(self):
        from robo_orchard_build.ext.stubgen import (
            Pybind11StubgenExtension,  # noqa: F401
        )


if __name__ == "__main__":
    pytest.main(["-s", __file__])
