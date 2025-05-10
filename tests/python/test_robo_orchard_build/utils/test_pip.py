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

import pytest

from robo_orchard_build.utils.pip import get_package_version


class TestPip:
    def test_get_package_version(self):
        package_name = "pytest"
        version = get_package_version(package_name)
        print(version)
        assert version is not None

    def test_get_package_version_not_exist(self):
        package_name = "pytest_not_exist"
        version = get_package_version(package_name)
        print(version)
        assert version is None


if __name__ == "__main__":
    pytest.main(["-s", __file__])
