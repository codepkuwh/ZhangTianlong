#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @date: 2018/12/17 8:59
import logging
import requests
from bs4 import BeautifulSoup


USER_NAME = "登录手机号"
PSW = "登录密码"


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






# 登录情况下, 仅get目标网页源码
def get_html(url):
      session, token = get_token()
      session = login(session, token)
      res = session.get(url)
      html = res.content.decode("utf-8")
      return html


# 获取未过期班级的作业审批信息, 生成作业提交提醒
def get_task():
    url = "https://www.codepku.com/jwgl/task/index"  # 作业审批链接
    html = get_html(url)
    soup = BeautifulSoup(html, "lxml")
    tr_list = soup.find_all("tr")[1:]
    details_url_list = []
    mes = ''
    for tr in tr_list:
        td_list = tr.find_all("td")
        if td_list[3].get_text().strip() == "正常":   # 去掉过期课程
            time = td_list[2].get_text().strip()
            level = td_list[5].get_text().strip()
            homework = td_list[7].get_text().strip()
            details_url = td_list[9].find("a").get("href")
            details_url_list.append(details_url)

            # 获取作业提交的数量, 生成必要的格式, 方便直接发送到班级群中
            info = "截止目前, 仅%d位同学提交了作业, 请没有完成作业的同学抽空尝试做一下, 并将代码提交一下哦." % int(homework[0])

            mes = mes + time + "  " + level + "  作业数量: " + homework + "  班级作业:" + details_url + info + "\n"

    return details_url_list, mes


# 获取每个班级作业的详情页连接
def homework_url():
    details_url_list, mes = get_task()
    print("-----------------------作业提交情况----------------------")
    print(mes)
    print("-----------------------作业详情页----------------------")
    for url in details_url_list:
        html = get_html(url)
        soup = BeautifulSoup(html, "lxml")
        tbody_tag = soup.find("table", attrs={"id": "work_time_tab"})
        tr_tags = tbody_tag.find_all("tr")[1:]
        if tr_tags != []:
            for tr in tr_tags:
                td_tags = tr.find_all("td")
                name = td_tags[0].get_text()
                theme = td_tags[1].get_text()
                submit_time = td_tags[4].get_text()
                # print(tr)
                url = td_tags[5].find("a").get("href")  # 作业封面连接, 需要替换为代码详细页
                url = url.replace("works/", 'python/create_first/?work_id=')
                print(name, "提交时间:", "作业名:", theme, "提交时间: ", submit_time, "作业详细页:", url)


homework_url()
