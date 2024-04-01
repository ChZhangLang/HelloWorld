import collections
import json
import copy
import csv
from collections import Counter

class GetPath():
    def __init__(self,nodes,edgesDict,start,end):
        self.nodes = [i for i in nodes]
        self.edges = copy.deepcopy(edgesDict)
        self.start = start
        self.end = end

    def getPath(self):
        Path = []
        pa = []
        visit = {}
        for node in self.nodes:
            visit[node] = 0
        self.dfs(self.start, visit, Path, pa)
        return Path

    def dfs(self, mynode, visit, Path, pa):
        if visit[mynode] == 1:
            return
        pa.append(mynode)
        visit[mynode] = 1
        temp = [i for i in pa]
        if mynode == self.end:
            Path.append(temp)
            visit[mynode] = 0
            pa.pop()
            return

        for node in self.edges[mynode]:
            self.dfs(node, visit, Path, pa)
        visit[mynode] = 0
        pa.pop()
        return

    def tran(self, Path):
        edgePath = []
        for path in Path:
            edgepath = []
            for i in range(len(path)-1):
                edgepath.append((path[i], path[i+1]))
            edgePath.append(edgepath)

        return edgePath

