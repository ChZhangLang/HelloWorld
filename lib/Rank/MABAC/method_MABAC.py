import numpy as np

def cost_normalize(list):
    min_data = min(list)
    max_data = max(list)
    for i in range(len(list)):
        list[i] = (max_data - list[i]) / (max_data - min_data)
    return list

def benefit_normalize(list):
    min_data = min(list)
    max_data = max(list)
    for i in range(len(list)):
        list[i] = (list[i] - min_data) / (max_data - min_data)
    return list

def B_to_A_weight(list,w):
    for i in range(len(list)):
        list[i] = w * (1 + list[i])
    return list

def get_g(list, visit):
    s = 1
    for i in range(len(list)):
        if visit[i] == 0:
            s *= list[i]
    res = pow(s, 1/(len(list)-sum(visit)))
    return res

def refresh_A_with_g(list,g):
    for i in range(len(list)):
        list[i] -= g
    return list

def TFN_exact_value(list):
    res = []
    for temp in list:
        res.append((temp[0]+4*temp[1]+temp[2])/6)
        # print(len(res), temp)
    return res
