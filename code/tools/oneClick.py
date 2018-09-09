# 用于读取文件，并自动按教案、录屏、听课报告分类上传的脚本

import logging
import os
import sys
import base64
import json
import re

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s-[%(levelname)s]-%(message)s', level=logging.DEBUG)

USER_NAME = "18086662005"
PSW = "Bw711286114"

work_path = sys.path[0]
locate = ""   # 16 楼为空，28 楼为 28
print("work_path:", work_path)

# 提交上传记录 form-data
# course_id: 30 python level 2
# course_id: 47 python level 1 第二版
# course_id: 31 python level 3
# course_id: 32 python level 4
# 试讲 type 0  听课报告 type 1  教案 type 2

course_id = {
    "PL1V2": 47,
    "PL2": 30,
    "PL3": 31,
    "PL4": 32
}

course_type = {
    "听课报告": 1,
    "试讲": 0,
    "教案": 2
}


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
    }  # yapf: disable

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

    return session


def get_token():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }  # yapf: disable

    # 用 session 保存 cookies
    session = requests.session()
    response = session.get('https://www.codepku.com/', headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    token = soup.find(attrs={"name": "csrf-token"})["content"]

    return session, token  # 获取 token, 把 session 传回，保存 cookie


def upload_handle():
    pass


def file_handle(file):
    """
    input: 文件名
    return: upload_length, upload_metadata{"filename": "", "filetype": ""}
    """
    pattern = re.compile(r"PL\d\.\d{1,2}", re.I)
    match = pattern.search(file)
    level, chapter = match.group().split(".")
    if level == "PL1" or level == "pl1":
        level = "PL1V2"
    # print(level, chapter)

    # 处理 mp4 文件
    if ".mp4" in file:
        filename = base64.b64encode(bytes(file, encoding='utf8'))
        filetype = base64.b64encode(b"video/mp4")
        upload_metadata = 'filename {},filetype {}'.format(str(filename).strip("b"), str(filetype).strip("b"))
        upload_length = os.path.getsize(os.path.join(work_path, file))

        return upload_metadata, str(upload_length), level, chapter
    # 处理 doc 文件
    pass


def video_uploader(session, file):
    """
    视频上传：
    首先 post 请求 https://video.wuhan.codepku.com/files
    header 中 Upload-Length 是文件大小，Upload-Metadata 是文件信息，用 base64 编码
    返回一个 json 包含：file_path，location，name，status
    然后 patch 请求 https://video.wuhan.codepku.com/files/ + location最后的key
    用于上传视频文件文件
    最后 post https://www.codepku.com/jwgl_api/lesson-prepare/lesson-prepare-submit
    需要提供 Authorization，需要进行 'Basic ' + btoa(username + ':' + password);
    目前还没搞懂怎么把 Authorization 拼出来。
    """
    upload_metadata, upload_length, level, chapter = file_handle(file)

    # post_headers = {
    #     'Upload-Length': upload_length,
    #     'Origin': 'https://www.codepku.com',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    #     'Accept': '*/*',
    #     'Tus-Resumable': '1.0.0',
    #     'Referer': 'https://www.codepku.com/jwgl_edu/preparation_teach/commit_stats',
    #     'Connection': 'keep-alive',
    #     'Content-Length': '0',
    #     'Upload-Metadata': upload_metadata,
    # }
    # # 获取 file_path，location，name（因为上传会修改文件名）
    # response = session.post('https://video.wuhan{}.codepku.com/files'.format(locate), headers=post_headers)
    # res_json = json.loads(response.text)

    # # 上传需要的参数
    # location = res_json["location"]
    # file_path = res_json["file_path"]
    # key = location.split("/")[-1]
    # # print(key)
    # # 上传视频，使用 patch，但是好像不需要patch就能上传，既然浏览器请求了，就保留下来吧。
    # patch_headers = {
    #     'Origin': 'https://www.codepku.com',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Upload-Offset': '0',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    #     'Content-Type': 'application/offset+octet-stream',
    #     'Accept': '*/*',
    #     'Tus-Resumable': '1.0.0',
    #     'Referer': 'https://www.codepku.com/jwgl_edu/preparation_teach/commit_stats',
    #     'Connection': 'keep-alive',
    #     'Content-Length': upload_length,
    # }
    # with open(os.path.join(work_path, file), "rb") as f:
    #     session.patch('https://video.wuhan.codepku.com/files/{}'.format(key), headers=patch_headers, data=f)

    # # get status
    # get_headers = {
    #     # 'Authorization': 'BearereyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3LmNvZGVwa3UuY29tXC9qd2dsXC9wcmVwYXJhdGlvbl90ZWFjaCIsImlhdCI6MTUzNjM3ODkwMCwiZXhwIjoxNTM2NzM4OTAwLCJuYmYiOjE1MzYzNzg5MDAsImp0aSI6IjZXRXoxVENZYmR1MGZ1VXYiLCJzdWIiOjc2MzAzLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.OAKwwgMKdpBbEPZQtjhWS3orpFiRDr723nLJoE1UoL8',
    #     'Origin': 'https://www.codepku.com',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    #     'Accept': 'application/json, text/plain, */*',
    #     'Referer': 'https://www.codepku.com/jwgl_edu/preparation_teach/commit_stats',
    #     'Connection': 'keep-alive',
    # }
    # params = (
    #     ('key', key),
    # )
    # response = requests.get('https://video.wuhan.codepku.com/file_info.php', headers=get_headers, params=params)

    # if json.loads(response.text)["status"] == "OK":
    #     print("成功上传到服务器：{}".format(file))

    # 将上传状态提交到服务器

    payload = {
        "id": "",
        "type": 0,   # type: 0 是试讲录屏
        "title": file,
        "course_id": course_id[level],
        "uploads": [{"filename": file,
                     "link": file_path,
                     "download_link": location,
                     "city": 2}],
        "chapter": chapter
    }
    submit = session.post("https://www.codepku.com/jwgl_api/lesson-prepare/lesson-prepare-submit", data=payload)

    print(submit.text)


def main():
    session, token = get_token()
    session = login(session, token)

    # 取得当前目录下的所有需要上传的文件
    filename_list = [file_ for file_ in os.listdir(work_path) if ".mp4" in file_ or ".doc" in file_]
    print(filename_list)
    # 上传文件
    video_uploader(session, filename_list[0])


# main()

filename_list = [file_ for file_ in os.listdir(work_path) if ".mp4" in file_ or ".doc" in file_]
for f in filename_list:
    print(file_handle(f))

# TODO:
# 文件自动分类
# 视频上传的最后提交
# 文档的自动上传
