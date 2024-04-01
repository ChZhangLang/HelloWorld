import json
import csv
from math import inf
import sys
# sys.path.append('..')
from lib.Rank.MABAC import mabac

inf_value = 1000
# 统计通过每条边的攻击路径数量
def cal_AttackPath_Count(path_id, num):
    APC = [0] * num  # 一共20条边，初始化为0
    for path in path_id:
        for edge in path:
            # print(edge)
            APC[int(edge[1:])-1] += 1
    # print(APC)
    return APC

# 统计通过每条边的最短路径长度
def cal_Shortest_AP_Length(path_id, num):
    Shortest_len = [inf_value] * num
    for path in path_id:
        for edge in path:
            Shortest_len[int(edge[1:])-1] = min(Shortest_len[int(edge[1:])-1], len(path) + 1)
    # print('shortest', Shortest_len)
    return Shortest_len

# 统计通过每条边的攻击路径长度的均值
def cal_AttackPath_Length_Average(path_id, num):
    AP_length = [0] * num
    AP_cnt = [0] * num
    for path in path_id:
        for edge in path:
            AP_length[int(edge[1:])-1] += len(path) + 1
            AP_cnt[int(edge[1:])-1] += 1
    AP_length_aver = [0] * num
    for i in range(len(AP_length)):
        if AP_cnt[i] != 0:
            AP_length_aver[i] = AP_length[i] / AP_cnt[i]
        else:
            AP_length_aver[i] = 0
            # print(AP_length)
    # print(AP_cnt)
    # print(AP_length_aver)
    # new_c3 = [1/t for t in AP_length_aver]
    # return new_c3
    return AP_length_aver

# 统计漏洞距离攻击起点的最短距离
def cal_shortest_distance_to_S0(path_id, num):
    shortest_dis = [inf_value] * num
    for path in path_id:
        for dis, edge in enumerate(path):
            shortest_dis[int(edge[1:])-1] = min(shortest_dis[int(edge[1:])-1], dis + 1)
    # print(shortest_dis)
    # end_dis = [8-t for t in shortest_dis]
    # return end_dis
    return shortest_dis

# 计算CC,计算边到其他节点最短距离和的倒数
def cal_cc(path, topo_path):
    with open(topo_path, 'r') as f:
        edge_ID_dict = json.load(f)
    f.close()

    node_num = 11
    node_dis = [[inf_value] * node_num for _ in range(node_num)]
    for te in path:
        for i in range(len(te)-1):
            for j in range(i+1,len(te)):
                if te[j] == 'T':
                    node_i, node_j = int(te[i][1:]), node_num - 1
                else:
                    node_i, node_j = int(te[i][1:]), int(te[j][1:])
                # print(node_i, node_j)
                node_dis[node_i][node_j] = min(node_dis[node_i][node_j], j-i)
        # print('=====')
    CC_node = [0] * node_num
    for i in range(len(node_dis)):
        for j in range(len(node_dis[i])):
            if node_dis[i][j] != inf_value:
                CC_node[i] += node_dis[i][j]
    CC_edge = [0] * 20
    for key in edge_ID_dict.keys():
        CC_edge[int(edge_ID_dict[key][1:]) - 1] = CC_node[int(key.split(',')[0][1:])]
    # print(CC_edge)
    for i,num in enumerate(CC_edge):
        if CC_edge[i] == 0:
            CC_edge[i] = 0
        else:
            CC_edge[i] = (node_num-1) / CC_edge[i]
    # print(CC_edge)
    # for k in CC_edge:
    #     print(k)
    return CC_edge

# 计算残余中心性
# 计算删除某条边后的残余中心性
def cal_RCC(path, nodenum, edgenum, topo_path):
    # for t in range(len(path)):
    #     print(path[t])
    # print('-=-==-=-==-=')
    # print(edge_ID_dict)
    with open(topo_path, 'r') as f:
        Topo = json.load(f)
    f.close()
    edge_ID_dict = {}
    for edge in Topo['edges']:
        dict = {edge['source'] + ',' + edge['target']: edge['edge_name']}
        edge_ID_dict.update(dict)
    RCC = [0] * edgenum
    node_num = nodenum + 1
    for i in range(len(RCC)):
        delete_edge = 'E'+str(i+1)  # 删除的边为E(i+2)
        for key in edge_ID_dict.keys():
            if edge_ID_dict[key] == delete_edge:
                source = key.split(',')[0]
                target = key.split(',')[1]
                break
        after_delete_paths = []  # 删除了某条边剩余的攻击路径
        for each_path in path:
            # print(each_path)
            flag = 1
            for q in range(len(each_path)-1):
                # print(each_path[q], each_path[q + 1])
                if each_path[q] == source and each_path[q+1] == target:
                    flag = -1
                    # print(1)
                    break
            if flag == 1:
                after_delete_paths.append(each_path)
        # print(after_delete_paths)
        node_dis = [[inf] * node_num for _ in range(node_num)]  # 记录节点到其他节点的最短距离
        # print(after_delete_paths)
        for temp_path in after_delete_paths:
            # print(temp_path)
            for u in range(len(temp_path)-1):
                # print("u ", temp_path[u])
                for v in range(u+1,len(temp_path)):
                    if temp_path[v] == 'T':
                        node_dis[int(temp_path[u][1:])][-1] = min(v-u, node_dis[int(temp_path[u][1:])][-1])
                    else:
                        node_dis[int(temp_path[u][1:])][int(temp_path[v][1:])] = min(v-u, node_dis[int(temp_path[u][1:])][int(temp_path[v][1:])])
                        # print(int(temp_path[v][1:]), node_dis[int(temp_path[u][1:])][int(temp_path[v][1:])])
            # print(node_dis[int(temp_path[u][1:])], "\n")

        res = 0
        for x in range(len(node_dis)):
            for y in range(len(node_dis[0])):
                res += 1/node_dis[x][y]
        # print("res", res)
        # for k in node_dis:
        #     print(k)
        # print(delete_edge, len(after_delete_paths),res)
        # for k in after_delete_paths:
        #     print(k)
        # print('=====================')
        # break
        RCC[i] = res
    # print(RCC)
    return RCC


def cal_path_metrics(topo_path, AttackPath_Count, Shortest_AP_Length, AttackPath_Length_Average, shortest_distance_to_S0, output_path):
    with open(topo_path, 'r') as f:
        edges = json.load(f)['edges']
    f.close()
    path_metrics = [['边', '攻击路径数量', '最短路径长度', '攻击路径长度的均值', '距离攻击起点的最短距离', '边到其他节点最短距离和的倒数']]
    # print(AttackPath_Count)
    for edge in edges:
        name = edge['edge_name']
        no = int(name[1:])-1
        ac = AttackPath_Count[no]
        # print(no, ac)
        sal = Shortest_AP_Length[no]
        ala = AttackPath_Length_Average[no]
        sdt0 = shortest_distance_to_S0[no]
        # cc = CC[no]
        path_metrics.append([name, ac, sal, ala, sdt0])
    # print(path_metrics)
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(path_metrics)

if __name__ == '__main__':
    topo_path = sys.argv[1]; metrics_path = sys.argv[2]
    start, end, nodes, edges, nums = mabac.get_path(topo_path)
    all_paths = mabac.get_path1(start, end, nodes, edges)  # all_paths 记录了攻击路径
    path_id, path_node = mabac.all_paths_conversion(all_paths, topo_path, start)
    m1 = cal_AttackPath_Count(path_id, nums[2])
    m2 = cal_Shortest_AP_Length(path_id, nums[2])
    m3 = cal_AttackPath_Length_Average(path_id, nums[2])
    m4 = cal_shortest_distance_to_S0(path_id, nums[2])
    # m10 = cal_RCC(path_node, nums[1], nums[2], topo_path)
    cal_path_metrics(topo_path, m1, m2, m3, m4, metrics_path)
