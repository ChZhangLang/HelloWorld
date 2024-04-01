import json
import copy
import sys
import csv
# sys.path.append('....')
from lib import get_allpath as method_get_all_path
# from lib import cal_metrics as method_get_metrics
# import MABAC as method_MABAC
from lib.Rank.MABAC import method_MABAC


def get_path(topo_path):
    with open(topo_path, 'r') as f:
        Topo = json.load(f)
    f.close()
    start = Topo['v0']
    end = Topo['goal'][0]['host']
    nodes = Topo['hosts']
    edges = Topo['edges']
    pathsnum = Topo['nums']

    newnodes = []
    newedges = []
    for node in nodes:
        newnodes.append(node['host_name'])
    for edge in edges:
        path = [edge['source'], edge['target']]
        newedges.append(path)

    return start, end, newnodes, newedges, pathsnum


# [[('S0', 'S1'), ('S1', 'S2'), ('S2', 'S3'), ('S3', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S2'), ('S2', 'S3'), ('S3', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S2'), ('S2', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S2'), ('S2', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S3'), ('S3', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S3'), ('S3', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S2'), ('S2', 'S3'), ('S3', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S2'), ('S2', 'S3'), ('S3', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S2'), ('S2', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S2'), ('S2', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S3'), ('S3', 'S5'), ('S5', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S3'), ('S3', 'S6'), ('S6', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S7'), ('S7', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S8'), ('S8', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'S9'), ('S9', 'T')], [('S0', 'S1'), ('S1', 'S4'), ('S4', 'T')]]
def get_path1(start, end, nodes, edges):
    edgesDict = {}
    Numedges = {}
    edgesNum = {}
    for edge in edges:
        if edgesDict.get(edge[0]) == None:
            edgesDict[edge[0]] = [edge[1]]
        else:
            edgesDict[edge[0]].append(edge[1])
        edgesDict[end] = []
    myPath = method_get_all_path.GetPath(nodes, edgesDict, start, end)
    Path = myPath.getPath()  # 存放全部攻击路径
    edgePath = myPath.tran(Path)
    return edgePath


def all_paths_conversion(all_paths, topo_path, start):
    path_id = []  # 每条边用编号代替
    path_node = []  # 记录攻击路径上的点

    with open(topo_path, 'r') as f:
        Topo = json.load(f)
    f.close()
    edge_ID_dict = {}
    for edge in Topo['edges']:
        dict = {edge['source'] + ',' + edge['target']: edge['edge_name']}
        edge_ID_dict.update(dict)
    # print(edge_ID_dict)

    for path in all_paths:
        temp_id = []
        temp_path = [start]
        for source, target in path:
            temp_id.append(edge_ID_dict[source + ',' + target])
            temp_path.append(target)
        path_id.append(temp_id)
        path_node.append(temp_path)

    return path_id, path_node


# def all_paths_conversion1(all_paths):
#     path_id = []    # 每条边用编号代替
#     path_node = []  # 记录攻击路径上的点
#
#     with open('../input/edgeID.json', 'r') as f:
#         edge_ID_dict = json.load(f)
#     f.close()
#     # print(edge_ID_dict)
#     for path in all_paths:
#         temp_id = []
#         temp_path = ['S0']
#         for source, target in path:
#             temp_id.append(edge_ID_dict[source + ',' + target])
#             temp_path.append(target)
#         path_id.append(temp_id)
#         path_node.append(temp_path)
#
#     return path_id, path_node

def get_rank(m1, m2, m3, m4, weight, visit, edgesnum, topo_path, data_path, out):
    # 从右往左pop
    for i in range(edgesnum - 1, -1, -1):
        if visit[i] == 1:
            m1.pop(i)
            m2.pop(i)
            m3.pop(i)
            m4.pop(i)
            # m10.pop(i)

    # print(visit)

    B_or_C = ['B', 'C', 'C', 'C', 'B', 'B', 'B', 'B', 'C', 'B']  # B表示Benefit,C表示Cost型
    # B_or_C = ['B', 'C', 'C', 'B', 'B', 'B', 'B', 'B', 'C', 'B']  # 新c4

    with open(topo_path, 'r') as f:
        edges = json.load(f)['edges']
    f.close()
    m5_TFN = []
    m6_TFN = []
    m7_TFN = []
    m8 = []
    m9_TFN = []
    for edge in edges:
        if edge['edge_name'] == 'E1':
            continue
        # print(edge['val'])
        # 机密性C(b) 模糊值
        m5_TFN.append(edge['val']['C'])
        # 完整性I(b) 模糊值
        m6_TFN.append(edge['val']['I'])
        # 可用性A(b） 模糊值
        m7_TFN.append(edge['val']['A'])
        # exploit(b)
        m8.append(edge['val']['ES'])
        # 设备影响值（b）模糊值
        m9_TFN.append(edge['val']['TFN'])
        # print(edge['edge_name'], edge['val']['C'], len(m5_TFN))

    # m5_TFN = [(0,1,2),(0,1,2),(2,3,4),(0,1,2),(0,1,2),(0,1,2),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(1,2,3),(2,3,4),(0,1,2),(2,3,4),(0,1,2),(2,3,4),(0,1,2),(0,1,2)]
    m5 = method_MABAC.TFN_exact_value(m5_TFN)
    # print(m5_TFN)

    # m6_TFN = [(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(0,1,2),(2,3,4),(0,1,2),(2,3,4),(1,2,3),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(2,3,4)]
    m6 = method_MABAC.TFN_exact_value(m6_TFN)

    # m7_TFN = [(0, 1, 2), (2, 3, 4), (2, 3, 4), (2, 3, 4), (0, 1, 2),  (2, 3, 4), (2, 3, 4), (0, 1, 2), (2, 3, 4),(0, 1, 2),  (2, 3, 4), (0, 1, 2), (2, 3, 4), (0, 1, 2), (2, 3, 4),  (0, 1, 2), (2, 3, 4), (0, 1, 2),(0, 1, 2)]
    m7 = method_MABAC.TFN_exact_value(m7_TFN)

    # exploit(b)
    # m8 = [0.8, 2.8, 3.9, 2.8, 0.8, 2.8, 2.8, 3.9, 2.8, 3.9, 2.8, 2.3, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9]

    # m9_TFN = [(1,2,3),(1,2,3),(2,3,4),(1,2,3),(1,2,3),(1,2,3),(2,3,4),(2,3,4),(2,3,4),(2,3,4),(3,4,5),(3,4,5),(4,5,6),(4,5,6),(4,5,6),(4,5,6),(4,5,6),(4,5,6),(4,5,6)]
    m9 = method_MABAC.TFN_exact_value(m9_TFN)
    # ini_m9 = [2, 2, 3, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5]
    # m9 = [2*t+7 for t in ini_m9]

    # print(len(m5_TFN), len(m5))

    metrics_10 = [m1] + [m2] + [m3] + [m4] + [m5] + [m6] + [m7] + [m8] + [m9]

    all_metrics_final = []
    g = []
    temp_C = []
    temp_I = []
    temp_A = []
    temp_service = []
    for i in range(len(metrics_10)):
        temp = metrics_10[i]
        if B_or_C[i] == 'B':
            # benefit
            n_m = method_MABAC.benefit_normalize(copy.deepcopy(temp))
        else:
            # cost
            n_m = method_MABAC.cost_normalize(copy.deepcopy(temp))
        A_m = method_MABAC.B_to_A_weight(copy.deepcopy(n_m), weight[i])

        # if i==4:
        #     temp_C.append(A_m)
        # if i==5:
        #     temp_I.append(A_m)
        # if i==6:
        #     temp_A.append(A_m)
        # if i==8:
        #     temp_service.append(A_m)

        g_i = method_MABAC.get_g(copy.deepcopy(A_m), visit)
        final_m = method_MABAC.refresh_A_with_g(copy.deepcopy(A_m), g_i)
        all_metrics_final.append(final_m)

    # print(all_metrics_final)
    data = list(zip(*all_metrics_final))

    # 保存数据
    with open(data_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    temp_sum = []
    temp_sum_exp = []
    temp_c3 = []
    for i in range(len(data)):
        temp_sum.append(sum(data[i]))
        temp_sum_exp.append(sum(data[i]) - data[i][2])
        temp_c3.append(data[i][2])
        # print(data[i], i+2, sum(data[i]),sum(data[i])-data[i][2], data[i][2])

    # print(temp_sum)
    # print(temp_sum_exp)
    # print(temp_c3)
    # print('=======================================================')

    edge_scores = [-100] * edgesnum
    visit_num = 0
    # print(len(data), len(visit))
    for i in range(len(visit)):
        # print(i-visit_num)
        if visit[i] == 1:
            visit_num += 1
            continue
        else:
            edge_scores[i] = sum(data[i - visit_num])
    edgeID_score = []
    for i in range(len(edge_scores)):
        edgeID_score.append(['E' + str(i + 1), edge_scores[i]])
        # print('E'+str(i+1), edge_scores[i])

    out.update({'ranking': Single_round_sorting_results(edgeID_score, edgesnum)})
    best_score = max(edge_scores)
    rank_1_edge = edge_scores.index(best_score)
    # print(rank_1_edge)
    # rank1_edge这个是索引,加入索引为3，说明最重要的边是E4
    return rank_1_edge
    # return


def refresh_path(best_edge, all_paths, topo_path):
    # 删除all_paths中包含best_edge的边
    with open(topo_path, 'r') as f:
        Topo = json.load(f)
    f.close()
    edge_ID_dict = {}
    for edge in Topo['edges']:
        dict = {edge['source'] + ',' + edge['target']: edge['edge_name']}
        edge_ID_dict.update(dict)
    for key in edge_ID_dict.keys():
        if edge_ID_dict[key] == best_edge:
            # print(key)
            delete_edge = (key.split(',')[0], key.split(',')[1])
    # print(delete_edge)
    for i in range(len(all_paths) - 1, -1, -1):
        if delete_edge in all_paths[i]:
            all_paths.pop(i)
    # print(edge_ID_dict)
    return all_paths


def Single_round_sorting_results(edgeID_score, edgesnum):
    edgeID_score.sort(key=lambda x: -x[1])
    ranking = [0] * edgesnum
    for i, res in enumerate(edgeID_score):
        # print(res)
        ranking[int(res[0][1:]) - 1] = i + 1
    # print('ranking=', ranking)
    return ranking

if __name__ == '__main__':
    topo_path = sys.argv[1]; weight_path = sys.argv[2]; data_path = sys.argv[3]; output_path = sys.argv[4]; metrics_path = sys.argv[5]
    with open(weight_path, 'r') as f:
        weight = json.load(f)
    f.close()
    weight = weight['weight']

    # fuzzy bwm c4最好 c5最坏权重结果  对应S0
    # weight = [0.12781813948975462, 0.09935288519287692, 0.08088865347587601, 0.2604045012074287, 0.06105172071668108, 0.08088865347587601, 0.08088865347587601, 0.08088865347587601, 0.12781813948975462]

    # fuzzy bwm c5最好 c4最坏权重结果  对应S1
    # weight = [0.083561288, 0.069617359, 0.137412924, 0.051290191, 0.221193303, 0.083561288, 0.083561288, 0.163604438, 0.10619792]

    # fuzzy bwm c1最好 c5最坏权重结果  对应S2
    # weight = [0.235242276, 0.074831159, 0.089842557, 0.113233549, 0.056194138, 0.074831159, 0.089842557, 0.089842557, 0.176140047]

    # fuzzy bwm c7最好 c5最坏权重结果  对应S3
    # weight = [0.091215851, 0.078491144, 0.123280052, 0.119885057, 0.068506561, 0.119885057, 0.220702944, 0.078491144, 0.09954219]

    # 各个指标权重相等  对应S4
    # weight = [1/9] * 9

    start, end, nodes, edges, nums = get_path(topo_path)
    all_paths = get_path1(start, end, nodes, edges)  # all_paths 记录了攻击路径
    # print(all_paths)
    cutset = []; visit = [0] * nums[2]; visit[0] = 1; best_edge = 0
    out = {}
    while (len(all_paths) > 0):
        # print(len(all_paths))
        # 先把攻击路径转化为path_id 方便指标计算
        # path_id, path_node = all_paths_conversion(all_paths, topo_path, start)
        # print(path_id, '\n', path_node)
        # m1 = method_get_metrics.cal_AttackPath_Count(path_id, nums[2])
        # m2 = method_get_metrics.cal_Shortest_AP_Length(path_id, nums[2])
        # m3 = method_get_metrics.cal_AttackPath_Length_Average(path_id, nums[2])
        # m4 = method_get_metrics.cal_shortest_distance_to_S0(path_id, nums[2])
        # m10 = method_get_metrics.cal_cc(path_node)
        # m10 = method_get_metrics.cal_RCC(path_node, nums[1], nums[2], topo_path)
        # print("m10=",m10)
        # print(m10[3],m10[13])
        with open(metrics_path, 'r') as f:
            metrics = list(csv.reader(f))
            m1 = [float(row[1]) for row in metrics[1:]]
            m2 = [float(row[2]) for row in metrics[1:]]
            m3 = [float(row[3]) for row in metrics[1:]]
            m4 = [float(row[4]) for row in metrics[1:]]
            # m10 = [float(row[5]) for row in metrics[1:]]
        f.close()
        # print(m2)
        best_edge_index = get_rank(m1, m2, m3, m4, weight, visit, nums[2], topo_path, data_path, out)
        best_edge = 'E' + str(best_edge_index + 1)
        cutset.append(best_edge)
        visit[best_edge_index] = 1
        # 更新攻击路径
        all_paths = refresh_path(best_edge, copy.deepcopy(all_paths), topo_path)

        # print('best_edge', best_edge)
        # print('===========================')
        break

    # print('\nfinish')
    # print(cutset)
    out.update({'best_edge': best_edge})
    with open(output_path, 'w') as f:
        json.dump(out, f)
    f.close()
