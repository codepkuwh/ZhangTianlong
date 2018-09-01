# -*- coding:utf8 -*-
import datetime
import subprocess
import time
import logging
import ctypes
import sys

import requests
from requests.utils import get_encodings_from_content
from lxml import etree

# logging.basicConfig(format='%(asctime)s-[%(levelname)s]-%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s-[%(levelname)s]-%(message)s', filename='./testlog.log', filemode='w', level=logging.DEBUG)


def get_porxy():
    """
    从 doub.io 获取免费的代理账号
    """
    headers = {
        # 'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'cache-control': 'max-age=0',
        'authority': 'doub.loan',
        'referer': 'https://doub.loan/',
    }

    try:
        # respone = requests.get('https://doub.io/sszhfx/', headers=headers, verify=False, proxies=proxies)
        respone = requests.get('https://doub.io/sszhfx/', headers=headers, verify=False)
        respone.content.decode("utf8", "ignore").encode("gbk", "ignore")
        respone = respone.text
        logging.debug("get brook porxy succeed.")
    except:
        logging.error("fail to get brook porxy. exit process.")
        raise   # 记录错误信息，然后 raise

    html = etree.HTML(respone)

    result = html.xpath('/html/body/section/div[3]/div/div[1]/pre[3]/text()')

    # ip、端口、密码
    ips = [result[3].strip(), result[10].strip()]
    ports = [result[4].strip(), result[11].strip()]
    psws = [result[5].strip(), result[12].strip()]

    # 有两个账号可以用，选其一即可
    # porxy = (ips[0], ports[0], psws[0])
    porxy = (ips[1], ports[1], psws[1])

    logging.info("get {0}:{1} psw: {2}".format(*porxy))
    return porxy


def get_cmd(porxy):
    """
    生成 cmd 命令
    """
    cmd = r"brook.exe client -l 127.0.0.1:1984 -i 127.0.0.1 -s {ip}:{port} -p {psw}".format(ip=porxy[0], port=porxy[1], psw=porxy[2])
    logging.debug("gen cmd: {}".format(cmd))
    return cmd


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_hosts():
    """
    修改 hosts，需要管理员权限
    """
    if is_admin():
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r+") as f:
            l = f.readlines()
            for line in l:
                if "104.28.2.6 doub.io" in line:
                    logging.info("hosts already change")
                    return
            f.writelines(["104.28.2.6 doub.io \n"])
            logging.info("add new line in hosts")
    else:
        # 需要 python3，重新跑一遍，以管理员身份运行
        # __file__：本文件 sys.executable：python 解释器
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


check_hosts()

porxy = get_porxy()
p = subprocess.Popen(get_cmd(porxy), shell=True)
logging.debug("run cmd succeed.")

while True:
    while True:  # 定时器
        now = datetime.datetime.now()
        if now.hour == 3 and now.minute == 5:  # 凌晨3点5分
            logging.debug("schedule task at 3:05")
            new_porxy = get_porxy()

            if porxy != new_porxy:  # 如果代理更新，就结束原来进程，更新代理
                p.kill()
                logging.debug("kill old process succeed.")
                porxy = new_porxy

                time.sleep(5)
                p = subprocess.Popen(get_cmd(porxy), shell=True)
                logging.debug("run cmd: succeed.")

            else:
                logging.info("porxy wasn't change, nothing should to do.")

            logging.debug("schedule task end.")
            time.sleep(60)
            break  # 跳出定时任务

        time.sleep(20)
