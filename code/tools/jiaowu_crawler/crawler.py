import logging
import os
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,              # 定义输出到文件的log级别，
    format='%(asctime)s in %(filename)s: %(levelname)s %(message)s',    # 定义输出log的格式
    datefmt='%Y-%m-%d %H:%M:%S'
)


USER_NAME = "18086662005"
PSW = "Bw711286114"
teacherId = 76303   # 可能是个常量，在教务系统查看源代码搜索一下teacherId


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

    if response.status_code == 200:
        logging.info("登录成功！")
    else:
        logging.error("登录失败！")

    return session


def get_schedule(teacherid, date, session, token):
    """
    获取date这一周的时间表
    date是周一的日期
    """

    url = "https://www.codepku.com/jwgl/schedule/get_teacher_schedule"
    headers = {
        'Origin': 'https://www.codepku.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-CSRF-TOKEN': token,
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.codepku.com/jwgl',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }
    form_data = {
        "scheduleDate": date,
        "teacherId": teacherid
    }

    response = session.post(url, headers=headers, data=form_data).json()
    schedule = response["data"]["data"]

    return schedule, session, token


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

                    # print("class_info:", class_info)
                    # print("end_time:", end_time)
                    # print("people_num:", people_num)
                    # print("during:", during)
                    # print("progress:", progress)
                    # print("day_of_week:", day_of_week)
                    # print("class_time:", class_time)
                    # print("tid:", tid)
                    # print()

                    yield (class_info, end_time, people_num, during, progress.replace(u'\xa0', u' '), str(day_of_week), str(class_time), tid)

                except AttributeError:
                    if "试听课" in item.p.string:
                        logging.warning("这是一节试听课")
                    else:
                        logging.error("发生了未知错误")


def get_students_info(tid, end_time, session, token):
    """
    爬取续班信息
    """
    url = "https://www.codepku.com/jwgl/schedule/detail"
    headers = {
        'Origin': 'https://www.codepku.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-CSRF-TOKEN': token,
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.codepku.com/jwgl',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    post_data = {
        "tid": tid,
        "tmp": 1,
        "class_time": end_time
    }

    response = session.post(url, headers=headers, data=post_data).json()
    html = response["data"]

    # 爬取一个班级中每个学生的续班情况
    for url in parse_students_info(html):
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        all_course = soup.select("table > tbody > tr")
        std_name = soup.select(".top-menu-navibar > ol > li:nth-of-type(2) > span")[0].string

        # 结构化每个人的报班情况
        for course in all_course:
            # print(course.prettify())
            course_name = course.select("td:nth-of-type(2)")[0].string
            pay_time = course.select("td:nth-of-type(3)")[0].string
            rest_course = course.select("td:nth-of-type(6)")[0].string
            course_status = course.select("td:nth-of-type(9) > span")[0].string
            yield (std_name, course_name, pay_time, rest_course, course_status)


def parse_students_info(html):
    """
    解析详细信息的html，提取每个学生的续班链接，返回给 get_students_info 爬取续班信息
    """
    soup = BeautifulSoup(html, "lxml")
    for item in soup.select("tr > td:nth-of-type(3) > a"):
        url = item["href"]
        yield url


def run():
    session, token = get_token()
    session = login(session, token)
    html, session, token = get_schedule(76303, "2018-11-06", session, token)

    with open(os.path.join(os.path.dirname(__file__), "schedule.csv"), "w") as f:
        with open(os.path.join(os.path.dirname(__file__), "xuban.csv"), "w") as ff:
            for row in parse_schedule(html):
                f.write(",".join(row)+"\n")   # 写入本周的时间表
                _, end_time, _, during, *_, tid = row

                for col in get_students_info(tid, end_time, session, token):
                    _, _, pay_time, rest_course, *_ = col
                    start, end = during[:-7].split("-")   # 课程开始时间和结束时间

                    # 判断是否算续报
                    pay_time = datetime.strptime(pay_time, '%Y-%m-%d %H:%M:%S')
                    if float(start) < float(end):
                        start, end = str(datetime.now().year)+'.'+start, str(datetime.now().year)+'.'+end
                    else:
                        start, end = str(datetime.now().year)+'.'+start, str(datetime.now().year+1)+'.'+end
                    start, end = datetime.strptime(start, '%Y.%m.%d'), datetime.strptime(end, '%Y.%m.%d')
                    if rest_course == "12" and start < pay_time:
                        xuban = "True"
                    else:
                        xuban = "False"
                    ff.write(str(start) + "," + str(end) + "," + ",".join(col) + "," + xuban + "\n")   # 写入续班信息

    logging.info("任务完成！")


run()
