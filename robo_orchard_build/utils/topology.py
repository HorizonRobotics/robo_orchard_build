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

from collections import defaultdict
from typing import Dict, Generic, Optional, Set, TypeVar

T = TypeVar("T")


class Graph(Generic[T]):
    def __init__(self, directed=False):
        # use defaultdict to avoid key error
        self.graph: Dict[T, Set[T]] = defaultdict(set)
        self.directed = directed

    def add_node(self, node: T):
        """Add a node to the graph."""
        if node not in self.graph:
            self.graph[node] = set()

    def add_edge(self, start: T, end: T):
        """Add an edge to the graph."""
        self.graph[start].add(end)
        if not self.directed:
            self.graph[end].add(start)
        else:
            # make sure that end is in the graph
            # we call a visit to the end node to add it to the graph
            self.graph[end] = self.graph[end]

    def topo_sort(self) -> Optional[list[T]]:
        """Topologically sort the graph.

        Returns:
            Optional[Sequence[T]]: The topologically sorted nodes. If the graph
                has a cycle, return None.
        """
        # calculate in degree

        if not self.directed:
            raise ValueError("Topological sort is only for directed graph.")

        inDeg = {node: 0 for node in self.graph}
        for node in self.graph:
            for adj in self.graph[node]:
                inDeg[adj] += 1

        # initialize the queue with nodes that have 0 in-degree
        # these nodes are the starting nodes of the graph
        que = []
        for node, d in inDeg.items():
            if d == 0:
                que.append(node)

        idx = 0
        while idx < len(que):
            u = que[idx]
            # for every child, update in-degree. If in-degree becomes
            # 0, add it to the queue.
            for v in self.graph[u]:
                inDeg[v] -= 1
                if inDeg[v] == 0:
                    que.append(v)
            idx += 1

        if len(que) < len(self.graph):
            return None
        return que
