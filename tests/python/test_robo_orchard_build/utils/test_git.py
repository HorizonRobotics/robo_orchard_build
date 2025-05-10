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

import pytest

from robo_orchard_build.utils.git import (
    get_commit_datetime,
    get_commit_id,
    get_show_commit_files,
)


class TestGit:
    def test_get_git_commit_datetime(self):
        commit_date = get_commit_datetime()
        print(commit_date)
        assert commit_date is not None

    def test_get_commit_id(self):
        commit_id = get_commit_id()
        print(commit_id)
        assert commit_id is not None

    def test_show_commit_files(self):
        commit_id = get_commit_id()
        assert commit_id is not None
        commit_files = get_show_commit_files(commit_id)
        print(commit_files)
        assert commit_files is not None

    def test_show_commit_files_with_cwd(self):
        cwd = os.path.dirname(__file__)
        commit_id = get_commit_id(short=True)
        assert commit_id is not None
        commit_files = get_show_commit_files(commit_id, cwd=cwd)
        print(commit_files)
        assert commit_files is not None


if __name__ == "__main__":
    pytest.main(["-s", __file__])
