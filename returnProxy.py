#! /usr/bin/env python
#-*-coding:UTF-8-*-
import string
    
def getproxy():
    inf = open("valid_ip.txt")    # 这里打开刚才存ip的文件
    lines = inf.readlines()
    proxys = []
    for i in range(0,len(lines)):
        proxy_host = "http://" + lines[i].strip()
        proxy_temp = {"http":proxy_host}
        proxys.append(proxy_temp)

    return proxys