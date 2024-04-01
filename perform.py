import os
import json
import time
import psutil
import eventlet
eventlet.monkey_patch()
import csv
from datetime import datetime


with open('input/MainInput.json', 'r') as f:
        input = json.loads(f.read())
f.close()
timeout = input["timeout"]
list = input["nums"]
for i in range(len(list)):
    # print('now operating No.'+str(i))
    # pipe = os.popen('python3 main.py {} {} {} &'.format(list[i][0], list[i][1], list[i][2]))
    # ppid = os.getpid()
    # child = psutil.Process(ppid).children()
    # print(child)
    # cpid = int((str(child[0]).split(',')[0]).split('=')[1])

    
    try:
        with eventlet.Timeout(timeout, True):
            print('now operating No.'+str(i))
            pipe = os.popen('python3 main.py {} {} {} &'.format(list[i][0], list[i][1], list[i][2]))
            ppid = os.getpid()
            child = psutil.Process(ppid).children()
            cpid = int((str(child[0]).split(',')[0]).split('=')[1])
            
            pipe.read()
            print('No.'+str(i)+' finish\n')
    except eventlet.timeout.Timeout:
        print('No.'+str(i)+' timeout!')
        os.system("ps -ef|grep -E 'main.py|expand.py|Weight|cal_metrics.py|Rank'|grep -v grep|awk '{print $2}'|xargs kill -9")
        # os.system('ps -ef|grep python3')
        
        with open('result/exception.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timeout', datetime.now(), 'No.'+str(i), list[i][0], list[i][1], list[i][2]])
        f.close()

        
    

