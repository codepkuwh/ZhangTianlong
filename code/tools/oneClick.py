# 用于读取文件，并自动按教案、录屏、听课报告分类上传的脚本

import logging
import os
import sys

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s-[%(levelname)s]-%(message)s', level=logging.DEBUG)

USER_NAME = "18086662005"
PSW = "**********"
work_path = sys.path[0]


def login(session, token):
    login_headers = {
        'Origin': 'https://www.codepku.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-CSRF-TOKEN': token,  # 没有这个会 500
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.codepku.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    } # yapf: disable

    data = [('name', USER_NAME), ('password', PSW), ('from_modal', 1),
            ('remember', 'on')]

    login_url = "https://www.codepku.com/ajax-login"

    response = session.post(login_url, headers=login_headers, data=data)
    # print(response.request.headers)
    # print(response.status_code, response.cookies.get_dict())
    # response = session.get('https://www.codepku.com/admin')
    print(response.status_code)
    if response.status_code == 200:
        logging.info("登录成功！")
    else:
        logging.info("登录失败！")

    return session, response.status_code


def get_token():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    } # yapf: disable

    # 用 session 保存 cookies
    session = requests.session()
    response = session.get('https://www.codepku.com/', headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    token = soup.find(attrs={"name": "csrf-token"})["content"]

    return session, token  # 获取 token, 把 session 传回，保存 cookie


def upload_handle():
    pass


def read_file():
    pass


def upload(session, file):
    """
    视频上传：
    首先 post 请求 https://video.wuhan.codepku.com/files
    header 中 Upload-Length 是文件大小，Upload-Metadata 是文件信息，用 base64 编码
    返回一个 json 包含：file_path，location，name，status
    然后 patch 请求 https://video.wuhan.codepku.com/files/ + location最后的key
    用于上传视频文件文件
    最后 post https://www.codepku.com/jwgl_api/lesson-prepare/lesson-prepare-submit
    需要提供 Authorization，需要进行 atob
    """
    headers = {
        # 'Upload-Length': '119471479',
        'Origin': 'https://www.codepku.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5702.400 QQBrowser/10.2.1893.400',
        'Accept': '*/*',
        'Tus-Resumable': '1.0.0',
        'Referer': 'https://www.codepku.com/jwgl_edu/preparation_teach/commit_stats',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        # 'Upload-Metadata': 'filename MjAxODA4MDlfUEwxLjdf6K+V6K6yX+W8oOWkqem+mS5tcDQ=,filetype dmlkZW8vbXA0',
    }
    response = session.post('https://video.wuhan28.codepku.com/files', headers=headers)


def controler():
    # session, token = get_token()
    # session = login(session, token)

    # 取得当前目录下的所有需要上传的文件
    filename_list = [file_ for file_ in os.listdir(work_path) if ".mp4" in file_ or ".doc" in file_]
    print(filename_list[0])
    # 读取文件
    with open(filename_list[0]) as f:
        upload(session, f)

controler()
# TODO:
# 读取文件
# 自动上传

