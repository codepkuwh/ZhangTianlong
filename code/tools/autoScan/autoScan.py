# 使用说明：
#     1. 配置用户名密码以及各个目录信息
#     2. 上完课之后运行本程序，理论上可以批量上传，但为了避免意外最好上完一课运行一次
#     3. 需要 python3.6+
# 注意：
#     1. 程序使用创建时间进行自动匹配，所以不要把视频复制到工作目录，这样会修改创建时间
#     2. 程序依赖 requests, bs4
#     3. 测试版本，可能有 bug！！
#     4. 不支持试听课上传！！！（可能以后会支持）
#     5. 不确定支不支持引流课！！！
#     6. 识别机制为匹配创建时间在 15 分钟以内的视频


import base64
import json
import logging
import os
import re
import shutil
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,              # 定义输出到文件的log级别，
    format='%(asctime)s in %(filename)s: %(levelname)s %(message)s',    # 定义输出log的格式
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    import codecs
    with codecs.open("config.json", "r", "utf-8-sig") as f:
        config = json.load(f)
        logging.info("loading config.json successfuly!")
except:
    logging.warning("fail to load config.json by codecs, try other way...")
    with open("config.json") as f:
        config = json.load(f.read().decode("utf-8-sig"))
    logging.info("loading config.json successfuly!")

USER = config["user"]  # 用于归档文件命名
USER_NAME = config["user_name"]  # codepku 账号
PSW = config["psw"]   # 密码

section_dict = {
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
    "10": "十",
    "11": "十一",
    "12": "十二"
}


class LoginError(Exception):
    pass


class ArchiveError(Exception):
    pass


def login():
    session = requests.session()
    data = [('login', USER_NAME), ('password', PSW)]
    login_url = "https://edus.codepku.com/api/login/form"
    response = session.post(login_url, data=data)

    if response.status_code == 200:
        logging.info("登录成功！")
    else:
        logging.error("登录失败！")
        raise LoginError("登录失败！")

    return session


def get_token(session):
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    response = session.get('https://edus.codepku.com/class_schedule', headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    token = soup.find(attrs={"name": "csrf-token"}).get("content")
    logging.debug(f"success get token: {token}")
    return session, token


def get_teacherid(session):
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://edus.codepku.com/recordLesson/index',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    response = session.get('https://edus.codepku.com/class_schedule', headers=headers)
    pattern = r"teacherId = '\d+';"
    result = re.search(r"\d+", re.search(pattern, response.text).group()).group()
    return session, result


def get_uploads(session):
    """ 获取需要上传的视频 """
    # session = login()
    res = session.get("https://edus.codepku.com/api/class-record/need-uploads")
    res = json.loads(res.text)
    course_info = res.get("data").get("times")

    def filter_info(date):
        for item in course_info.get(date):
            if item.get("sn"):
                return item.get("sn")
            elif item.get("free_class_students"):
                return item.get("free_class_students")

    # 获取有正式课的课程列表，其中可能有试听课
    need_upload = map(lambda date: course_info.get(date), filter(filter_info, course_info))
    need_upload = list(need_upload)
    logging.debug(f"SUCCESS get upload list: {need_upload}")
    return need_upload


def scan_file():
    filename_list = [file_ for file_ in os.listdir(config["cwd"]) if ".mp4" in file_]
    return filename_list


def archive(f, class_type, level, period, section, class_):  # 文件名，N OR P，level，第几期，第几课，班级，目标路径
    """ 重命名并归档到对应目录 """
    # 转化时间格式
    date = time_stamp_to_time(os.path.getmtime(os.path.join(config["cwd"], f)))

    # 格式化命名
    new_name = f"{date}_{class_type}L{level}_T{period}_C{class_}_第{section_dict[str(section)]}节_{USER}.mp4"
    logging.info(f"rename {f} ---> {new_name}")
    os.rename(f, new_name)

    # 判断目录是否存在
    if class_type.upper() == "P":
        target = config["PythonDir"]
    elif class_type.upper() == "N":
        target = config["NoipDir"]
    elif class_type.upper() == "S":
        target = config["Scratch"]
    elif class_type.upper() == "A":
        target = config["Arduino"]
    else:
        logging.error("不支持的课程，视频未发生移动")
        raise ArchiveError("不支持的课程")

    if not os.path.exists(f"{target}/L{level}/第{period}期/C{class_}"):
        os.makedirs(f"{target}/L{level}/第{period}期/C{class_}")

    # 移动文件到目标目录
    logging.info(f"move {new_name} to {target}")
    shutil.move(os.path.join(config["cwd"], new_name), f"{target}/L{level}/第{period}期/C{class_}")


def archive_free(f):
    logging.info(f"move {f} to {config['free']}")
    os.makedirs(config["free"])
    shutil.move(f, config["free"])


def time_stamp_to_time(timestamp, fmt='%Y%m%d'):
    """ 转换时间格式 """
    timeStruct = time.localtime(timestamp)
    return time.strftime(fmt, timeStruct)


def time_to_stamp(t):
    return time.mktime(time.strptime(t, "%Y-%m-%d %H:%M:%S"))


def get_create_time(f):
    t = os.path.getctime(f)
    logging.info(f"文件 {f} 的创建时间是: {time_stamp_to_time(t, fmt='%Y-%m-%d %H:%M:%S')}")
    return t


def upload(session, f, section, small_class_time_id):
    # 先 post https://video.wuhan22.codepku.com/files 获取 uuid
    # 然后 patch https://video.wuhan22.codepku.com/files/{uuid}
    # 然后 get https://video.wuhan22.codepku.com/file_info.php?key={uuid}
    # 然后 get https://video.wuhan22.codepku.com/get_md5.php?path={path}
    # 保存，原理待验证
    #   试听 post https://edus.codepku.com/api/class-record/free-class-record-videos
    #   正式课 post https://edus.codepku.com/api/class-record/record-videos
    #       修改 put https://edus.codepku.com/api/class-record/record  ？？？？？
    # 提交，原理待验证
    #   post https://edus.codepku.com/api/class-record/finish

    # session = login()
    # session, token = get_token(session)   # no use
    # post_to_file(session, f, section, small_class_time_id)
    pass


def post_to_file(session, f, section, small_class_time_id, **kw):
    # ===============================================================
    headers = {
        'Tus-Resumable': '1.0.0',
        'Upload-Length': str(os.path.getsize(os.path.join(config["cwd"], f))),
        'Origin': 'https://edus.codepku.com',
        'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Upload-Metadata': 'filename {},filetype dmlkZW8vbXA0'.format(base64.b64encode(f.encode(encoding="utf-8")).decode('ascii')),
    }
    r = session.post("https://video.wuhan22.codepku.com/files/", headers=headers).json()
    # assert r["status"] == "SUCCESS"
    uuid = r["id"]
    file_name = r["file_path"].split("src")[-1]
    logging.debug(f"get uuid: {uuid}, file_name: {file_name}")
    # ===============================================================
    headers = {
        'Tus-Resumable': '1.0.0',
        'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload',
        'Origin': 'https://edus.codepku.com',
        'Upload-Offset': '0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Content-Type': 'application/offset+octet-stream',
    }

    with open(f, "rb") as data:  # 上传视频
        logging.info(f"patch file to server.....{f}")
        response = requests.patch('https://video.wuhan22.codepku.com/files/{}'.format(uuid), headers=headers, data=data)
        logging.info("patch file complited!")
    # ===============================================================
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload',
        'Origin': 'https://edus.codepku.com',
        # 'X-XSRF-TOKEN': 'vML0bjuQjyQymRa3wdRoyQgh8gEq3FtxDazuZR3y',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    }
    params = (
        ('key', uuid),
    )
    response = requests.get('https://video.wuhan22.codepku.com/file_info', headers=headers, params=params).json()

    file_path = response["file_path"].split("src")[-1]
    location = response["location"]
    name = response["meta_data"]["filename"]

    logging.info(f"upload success(but not record). get file_path: {file_path}, location: {location}, name: {name}")
    # ===============================================================
    if section and small_class_time_id:
        headers = {
            'Origin': 'https://edus.codepku.com',
            # 'X-XSRF-TOKEN': token,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        data = {
            "small_class_time_id": small_class_time_id,
            "chapter": section,
            "params": [{
                "link": file_path,
                "download_link": location,
                "title": name,
                "sort": 1,
                "city": 4,
                "is_cdn": 0}]
        }
        data = json.dumps(data)

        logging.debug(f"make record data: {data}")
        response = session.post('https://edus.codepku.com/api/class-record/record-videos', headers=headers, data=data)
        assert json.loads(response.text).get("msg") == "操作成功"
        logging.info("record SUCCESS!")
        # ===============================================================
        headers = {
            'Origin': 'https://edus.codepku.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload?init=1',
            'Connection': 'keep-alive',
        }

        data = f'{{"small_class_time_id":{small_class_time_id}}}'

        response = session.post('https://edus.codepku.com/api/class-record/finish', headers=headers, data=data)
        assert json.loads(response.text).get("msg") == "操作成功"
        logging.info(f"视频【{name}】提交成功！")
    else:
        headers = {
            'Origin': 'https://edus.codepku.com',
            # 'X-XSRF-TOKEN': token,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        data = {
            "free_class_student_id": kw.get("free_class_student_id"),
            "params": [{
                "link": file_path,
                "download_link": location,
                "title": name,
                "sort": 1,
                "city": 4,
                "is_cdn": 0}]
        }
        data = json.dumps(data)

        logging.debug(f"make record data: {data}")
        response = session.post('https://edus.codepku.com/api/class-record/free-class-record-videos', headers=headers, data=data)
        # assert json.loads(response.text).get("code") == 200
        logging.info("record SUCCESS!")
        # ===============================================================
        headers = {
            'Origin': 'https://edus.codepku.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://edus.codepku.com/jwgl_edu/class_record/upload?init=1',
            'Connection': 'keep-alive',
        }

        data = f'{{"free_class_student_id":{kw.get("free_class_student_id")}}}'
        response = session.post('https://edus.codepku.com/api/class-record/finish', headers=headers, data=data)
        # assert json.loads(response.text).get("code") == 200
        logging.info(f"视频【{name}】提交成功！")


def get_schedule(session, teacherid, date):
    """
    获取date这一周的时间表
    date是周一的日期
    """

    url = "https://edus.codepku.com/schedule/get_teacher_schedule"
    headers = {
        'Origin': 'https://edus.codepku.com',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'X-CSRF-TOKEN': 'ztzkA09moHQ2ky07ElWW9vkwtF8CtktOwFhCYdx7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://edus.codepku.com/class_schedule',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    form_data = {
        'scheduleDate': date,
        'teacherId': teacherid
    }

    response = session.post(url, headers=headers, data=form_data).json()
    schedule = response["data"]["data"]

    return session, schedule


def parse_schedule(html):
    """解析时间表，是个生成器"""
    soup = BeautifulSoup(html, "lxml")

    items = soup(class_="class-curriculum-table-tds")
    for row in items:  # 课表中的每一行
        if "周一" in row.text:
            continue

        cols = row.select(".ea-first-td")  # 课表中的每一列

        for item in cols:
            if item.select(".ea-null-td"):  # 排除没课的
                continue
            else:
                try:
                    class_info = item.find(class_="course_name").text  # PL1第三期07班
                    end_time = item.select('div[classtime]')[0]["classtime"]  # 2018-12-02 19:30
                    people_num = item.find(class_="real-people-num").text  # 6 人
                    during = item.select("div > p:nth-of-type(3)")[0].text  # 09.02-12.02(19:30)
                    progress = item.select("div > p:nth-of-type(2)")[0].text
                    day_of_week = datetime.strptime(end_time, '%Y-%m-%d %H:%M').weekday()  # 6
                    class_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M').time()  # 19:30:00
                    tid = item.select('div[classtime]')[0]["text"]

                    yield (class_info, end_time, people_num, during, progress.replace(u'\xa0', u' '), str(day_of_week), str(class_time), tid)

                except AttributeError:
                    if "试听课" in item.p.string:
                        # logging.debug("这是一节试听课")
                        pass
                    else:
                        logging.error("发生了未知错误")


def get_section(session, class_name, date, teacherid, cid):
    """ 获取class_name 在 date 时的上课进度 """
    # session = login()
    _, html = get_schedule(session, teacherid, date)
    for i in parse_schedule(html):
        name, _, _, _, section, _, _, tid = i
        if name == class_name and str(tid) == str(cid):
            return int(section.split(" ")[-1].split("/")[0]) + 1


def main():
    session = login()
    if not config["teacherid"]:
        session, teacherid = get_teacherid(session)
        logging.info(f"find teacherid: {teacherid}")
        # with open("confing.json", "w") as f:
        #     json.dump(config, f)
        #     logging.info(f"set teacherid to {teacherid}")
    else:
        teacherid = config["teacherid"]
    for all_task in get_uploads(session):
        for task in all_task:  # 获取全部上传任务
            logging.debug(f"process task: {task}")
            for f in scan_file():
                logging.debug(f"process file: {f}")
                if task.get("free_class_students"):  # 是1v1试听课
                    if abs(time_to_stamp(task.get("start_at")) - get_create_time(f)) < 15 * 60:
                        post_to_file(session, f, None, None, free_class_student_id=task["id"])

                        if config["archive"]:
                            try:
                                archive_free(f)
                            except Exception as e:
                                logging.error(f"归档失败！{e}")
                    continue
                class_name = task["small_class"]["title"]
                date = time_stamp_to_time(time_to_stamp(task.get("time")), '%Y-%m-%d')
                section = get_section(session, class_name, date, teacherid, task["id"])
                if abs(time_to_stamp(task.get("time")) - get_create_time(f)) < 15 * 60:
                    logging.info(f"找到适合的视频【{f}】，将上传至 {class_name} 的第 {section} 节课，id 是{task['id']}")
                    post_to_file(session, f, section, task["id"])
                    class_type = task["sn"][0]
                    level = task["sn"][2]
                    period = task["sn"][4]
                    class_ = task["sn"].split("C")[-1][:2]
                    logging.debug(f"解析课程参数: class_type: {class_type}, level: {level}, period: {period}, class_: {class_}")
                    if config["archive"]:
                        try:
                            archive(f, class_type, level, period, section, class_)
                        except Exception as e:
                            logging.error(f"归档失败！{e}")


if __name__ == "__main__":
    main()
    os.system('pause')
