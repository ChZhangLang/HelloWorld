import multiprocessing

from lib import expand, cal_metrics
from lib.Weight import fuzzy_bwm
from lib.Rank.MABAC import mabac
from datetime import datetime
import os, shutil, json, csv, psutil, sys
from multiprocessing import Process
M = 1024*1024

def addtimeline(weightmethod, weight_input):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y%m%d%H%M%S%f")
    # print("Timestamp:", timestamp)

    new_folder_path = os.path.join('result/history/', timestamp)
    os.makedirs(new_folder_path)
    os.makedirs(new_folder_path+'/single_res')
    os.makedirs(new_folder_path+'/inputs')
    # 要复制的文件列表
    file_list = ['graph_stat.json', 'weight.json', 'path_metrics.csv', 'rank.json']
    for file_name in file_list:
        source_file = os.path.join('result/', file_name)
        shutil.copy2(source_file, new_folder_path+'/single_res')
    shutil.copytree(os.path.join('result/', 'tmp'), os.path.join(new_folder_path, 'tmp'))
    file_list = ['input.json', 'MainInput.json', weightmethod+'_input/'+weight_input]
    for file_name in file_list:
        source_file = os.path.join('input/', file_name)
        shutil.copy2(source_file, new_folder_path+'/inputs')
    return current_datetime

def save(addnum, linknum, multi):
    with open('input/MainInput.json', 'r') as f:
        input = json.loads(f.read())
    f.close()
    weightmethod = input['weight']; rankmethod = input['rank']
    weight_input = input['weight_input']
    jounal1_path = 'result/stat_all.csv'; jounal2_path = 'result/perform_log.csv'
    
    # 添加时间戳并备份
    timestamp = addtimeline(weightmethod, weight_input)

    # stat_all.csv
    jounal1 = []
    with open("result/graph_stat.json", 'r') as f:
        stat = json.loads(f.read())
    f.close()
    hostsnum=stat["hostsnum"]; edgesnum=stat["edgesnum"]; pathsnum=stat["pathsnum"]
    with open("result/tmp/time.log", 'r') as f:
        log = f.read()
    f.close()
    ls1 = log.split()
    err = []; ls = []; j=0; flag=0
    for i in range(len(ls1)):
        if flag==1:
            flag-=1
            continue
        try:
            ls.append(float(ls1[i]))
            j+=1
        except:
            if j+1 == i or j+2 == i:
                ls.append('None')
            err.append(ls1[i])
            if ls1[i] == 'signal' or ls1[i] == 'code':
                err.append(ls1[i+1])
                flag += 1

    exception = ' '.join(err)
    print(ls)
    with open('result/tmp/exception.txt', 'w') as f:
        f.write(exception)
    expandtime=ls[0]; expandmem=ls[1]
    weighttime=ls[2]; weightmem=ls[3]
    metricstime=ls[4]; metricsmem=ls[5]
    ranktime=ls[6]; rankmem=ls[7]
    jounal1.append([timestamp, weightmethod, rankmethod, hostsnum, edgesnum, pathsnum, expandtime, expandmem, weighttime, weightmem, metricstime, metricsmem, ranktime, rankmem, exception])
    with open(jounal1_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(jounal1[0])

    # perform_log.csv
    jounal2 = []
    jounal2.append([timestamp, weightmethod, rankmethod, addnum, linknum, multi])
    # print(jounal2)
    with open(jounal2_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(jounal2[0])

def main(addnum, linknum, multi):
    with open('input/MainInput.json', 'r') as f:
        input = json.loads(f.read())
    f.close()
    weightmethod = input['weight']; rankmethod = input['rank']
    jounal1_path = 'result/stat_all.csv'; jounal2_path = 'result/perform_log.csv'



    while True:
        # print('expanding...\n')
        p = os.system('/usr/bin/time -f"%e %M" -o ./result/tmp/time.log python3 ./lib/expand.py {} {} {} {} {} {}'.format(addnum, linknum, multi, 'input/input.json', 'result/tmp/topo', 'result/graph_stat'))
        if p!=0:
            break

        # print('begin caculating weights...\n')
        weight_input = input['weight_input']
        if weightmethod == 'fuzzy_bwm':
            p = os.system('/usr/bin/time -f"%e %M" -a -o ./result/tmp/time.log python3 ./lib/Weight/fuzzy_bwm.py {} {}'.format('input/fuzzy_bwm_input/'+weight_input, 'result/weight.json'))
        if p!=0:
            break

        # print('begin caculating metrics...\n')
        p = os.system('/usr/bin/time -f"%e %M" -a -o ./result/tmp/time.log python3 ./lib/cal_metrics.py {} {}'.format('result/tmp/topo.json', 'result/path_metrics.csv'))
        if p!=0:
            break

        # print('begin caculating ranks...\n')
        if rankmethod == 'mabac':
            os.system('/usr/bin/time -f"%e %M" -a -o ./result/tmp/time.log python3 ./lib/Rank/MABAC/mabac.py {} {} {} {} {}'.format('result/tmp/topo.json', 'result/weight.json', 'result/tmp/data.csv', 'result/rank.json', 'result/path_metrics.csv'))
        break

    
    


if __name__ == '__main__':
    addnum = int(sys.argv[1]); linknum = int(sys.argv[2]); multi = int(sys.argv[3])
    main(addnum, linknum, multi)
    print('finish!')
    save(addnum, linknum, multi)
    sys.exit()
    
