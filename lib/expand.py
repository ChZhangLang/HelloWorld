import json
import copy
import random
import sys
from graphviz import Digraph

# 导入图
def get_path(path):
    with open(path, 'r') as f:
        topo = json.loads(f.read())

    hosts = {}
    edges = {}
    for host in topo["hosts"]:
        hosts[host["host_name"]] = host
    for edge in topo["edges"]:
        key = (edge["source"], edge["target"])
        edges[key] = edge
    # print(edges)
    return hosts, edges


def expand(topo, layer, addnum, linknum, multi):
    copyhosts = []
    for host in topo[0]:
        hostname = topo[0][host]['host_name']
        hostval = topo[0][host]['System_level']
        if hostname != 'V0' and hostname != 'T':
            copyhosts.append([hostname, hostval, 0])
    # print("\ncopyhosts: ", copyhosts)
    # copyhosts:  [('V1', 'Enterprise'), ('V2', 'Management'), ('V3', 'Management'), ('V4', 'Supervision'), ('V5', 'Supervision'), ('V6', 'Supervision'), ('V7', 'Supervision'), ('V8', 'Supervision'), ('V9', 'Control')]

    copyedges = []
    vals = []
    for edge in topo[1]:
        edgename = topo[1][edge]['edge_name']
        road = (topo[1][edge]['source'], topo[1][edge]['target'])
        val = topo[1][edge]['val']
        copyedges.append([edgename, road, val, 0])
        vals.append(val)
    # print("\ncopyedges: ", copyedges)
    # copyedges:  [['E1', ('V0', 'V1'), 3.9, 0], ['E2', ('V1', 'V2'), 0.8, 0], ['E3', ('V1', 'V3'), 2.8, 0], ['E4', ('V1', 'V4'), 3.9, 0], ['E5', ('V4', 'V3'), 2.8, 0], ['E6', ('V4', 'V2'), 0.8, 0], ['E7', ('V2', 'V3'), 2.8, 0], ['E8', ('V2', 'V5'), 2.8, 0], ['E9', ('V2', 'V6'), 3.9, 0], ['E10', ('V3', 'V5'), 2.8, 0], ['E11', ('V3', 'V6'), 3.9, 0], ['E12', ('V4', 'V7'), 2.8, 0], ['E13', ('V4', 'V8'), 2.3, 0], ['E14', ('V4', 'V9'), 3.9, 0], ['E15', ('V4', 'T'), 3.9, 0], ['E16', ('V5', 'V9'), 3.9, 0], ['E17', ('V6', 'T'), 3.9, 0], ['E18', ('V7', 'V9'), 3.9, 0], ['E19', ('V8', 'T'), 3.9, 0], ['E20', ('V9', 'T'), 3.9, 0]]
    # print("\nvals: ", vals)
    # vals:  [3.9, 0.8, 2.8, 3.9, 2.8, 0.8, 2.8, 2.8, 3.9, 2.8, 3.9, 2.8, 2.3, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9]

    expandedhosts = copy.deepcopy(topo[0])
    expandededges = copy.deepcopy(topo[1])
    for i in range(multi):
        addrandompoint = addrandompoints(copyhosts, copyedges, addnum)
        expandedhosts.update(addrandompoint[0])
        expandededges.update(addrandompoint[1])
    # print("\n addedhosts", expandedhosts)
    # print("\n addededges", expandededges)

    linkhosts = []
    for host in expandedhosts:
        hostname = expandedhosts[host]['host_name']
        order = layer.index(expandedhosts[host]['System_level'])
        linkhosts.append([hostname, order])

    for i in range(multi):
        expandededges.update(linkrandomedges(linkhosts, expandededges, vals, linknum))
    return expandedhosts, expandededges

def addrandompoints(copyhosts, copyedges, num):
    global hostsnum, edgesnum
    expandedhost = {}
    expandededge = {}

    while num:
        num -= 1
        newhost = random.choice(copyhosts)
        index = copyhosts.index(newhost)
        copyhosts[index][2] += 1
        times = copyhosts[index][2]
        hostsnum += 1
        newhostname = 'V' + str(hostsnum-2)
        # print(times, type(times))
        expandedhost.update({newhostname: {"host_name": newhostname, "System_level": newhost[1]}})

        for edge in copyedges:
            if edge[1][0] == newhost[0]:
                edge[3] += 1
                times = edge[3]
                edgesnum += 1
                newedgename = 'E' + str(edgesnum)
                expandededge.update({(newhostname, edge[1][1]): {"edge_name": newedgename, "source": newhostname, "target": edge[1][1], "val": edge[2]}})
            elif edge[1][1] == newhost[0]:
                edge[3] += 1
                times = edge[3]
                edgesnum += 1
                newedgename = 'E' + str(edgesnum)
                expandededge.update({(edge[1][0], newhostname): {"edge_name": newedgename, "source": edge[1][0], "target": newhostname, "val": edge[2]}})
            else: continue
    # print(expandedhost)
    return expandedhost, expandededge


def linkrandomedges(hosts, edges, vals, num):
    global edgesnum
    expandededges = {}

    for i in range(num):
        while True:
            source = random.choice(hosts)
            target = random.choice(hosts)
            if source[1] > target[1]:
                if isexisted(source, target, edges) == False:
                    break

        # print(source, target)
        newedge = (source[0], target[0])
        edgesnum += 1
        newedgename = 'E' + str(edgesnum)
        newedgeval = random.choice(vals)
        # print( newedge)
        edge = {newedge: {"edge_name": newedgename, "source": source[0], "target": target[0], "val": newedgeval}}
        expandededges.update(edge)
        edges.update(edge)
    return expandededges

def isexisted(source, target, edges):
    flag = False
    for edge in edges:
        if edge[0] == source[0] and edge[1] == target[0]:
            # print(edge)
            flag = True
    return flag

def drawtopo(topo, path):
    edges = topo[1]
    """保存dot文件和pdf视图"""
    graph = {
        "nodes": [],
        "edges": []
    }
    dot = Digraph(comment="Attack Graph", strict=True)
    dot.graph_attr['dpi'] = '300'
    dot.graph_attr['fontsize'] = '12pt'
    dot.node_attr['shape'] = 'box'
    dot.graph_attr['size'] = '7.75, 10.25'

    for edge in edges:
        # print(edge)
        source = edge[0]
        target = edge[1]
        if source not in graph["nodes"]:
            graph["nodes"].append(source)
            dot.node(name=source, label=source)
        if target not in graph["nodes"]:
            graph["nodes"].append(target)
            dot.node(name=target, label=target)

        item = {"source": source, "target": target}
        if item not in graph["edges"]:
            graph["edges"].append(item)
            dot.edge(source, target)
    dot.render(filename=path, view=False)

def savetopo(inputpath, expandedtopo, outputpath, nums):
    with open(inputpath, 'r') as f:
        topo = json.loads(f.read())
    out = {}
    start = topo['v0']
    end = topo['goal']
    hosts = expandedtopo[0]
    edges = expandedtopo[1]

    out.update({'v0': start})
    outhosts = []
    for host in hosts.values():
        outhosts.append({"host_name": host['host_name'], "System_level": host['System_level']})
    out.update({"hosts": outhosts})
    outedges = []
    for edge in edges.values():
        outedges.append({"edge_name": edge['edge_name'], "source": edge['source'], "target": edge['target'], "val": edge['val']})
    out.update({"edges": outedges})
    # print(out)
    out.update({'goal': end})
    out.update({'nums': nums})
    with open(outputpath+'.json', 'w') as f:
        json.dump(out, f)

def savestat(statpath,hostsnum, edgesnum, pathsnum):
    stat = {}
    stat.update({'hostsnum': hostsnum})
    stat.update({'edgesnum': edgesnum})
    stat.update({'pathsnum': pathsnum})
    with open(statpath+'.json', 'w') as f:
        json.dump(stat, f)


def caculatepathsnum(topo, start = 'V0', end = 'T'):
    graph = {}
    for source in topo:
        path = []
        for target in topo:
            if target[0] == source[0]:
                path.append(target[1])
        graph.update({source[0]: path})

    # print(graph)
    # 创建一个字典来保存每个节点的路径数量
    path_counts = {}

    # 对终点进行初始化，路径数量为1
    path_counts[end] = 1

    # 遍历图中的节点，计算每个节点到终点的路径数量
    for node in graph:
        if node != end:
            path_counts[node] = 0

    # 遍历节点，从终点向起点计算路径数量
    for node in reversed(graph):
        if node != end:
            for neighbor in graph[node]:
                path_counts[node] += path_counts[neighbor]

    # 返回起点的路径数量
    return path_counts[start]



# def Expand(addnum, linknum, multi, inputpath, outputpath, statpath):
if __name__ == '__main__':
    addnum = int(sys.argv[1]); linknum = int(sys.argv[2]); multi = int(sys.argv[3]); inputpath = sys.argv[4]; outputpath = sys.argv[5]; statpath = sys.argv[6]

    topo = get_path(inputpath)
    global hostsnum, edgesnum
    hostsnum = len(topo[0]); edgesnum = len(topo[1])
    # print("\ntopo hostsnumber edgesnumber", hostsnum, edgesnum)

    layer = ['Control', 'Supervision', 'Management', 'Enterprise']
    expandedtopo = expand(topo, layer, addnum, linknum, multi)
    # print(expandedtopo)
    # print("\nexpandedtopo hostsnumber edgesnumber", hostsnum, edgesnum)

    pathsnum = caculatepathsnum(topo[1])
    expandedpathsnum = caculatepathsnum(expandedtopo[1])
    # print("\npathsnum expandedpathsnum", pathsnum, expandedpathsnum)

    drawtopo(expandedtopo, outputpath)
    savetopo(inputpath, expandedtopo, outputpath, [expandedpathsnum, hostsnum, edgesnum])
    savestat(statpath, hostsnum, edgesnum, expandedpathsnum)

