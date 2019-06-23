# coding: utf-8
from flask import Flask, request, render_template, abort, url_for
from random import randint

import sys
import importlib
importlib.reload(sys)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/level4-4/", methods=["GET", "POST"])
def level4_4():
    if request.method == "GET":
        if "python-requests" in request.headers.get("User-Agent", None):
            return """恭喜你成功使用 get!
    你通过 get 提交的数据是：
    {}""".format(dict(request.args))

        return render_template("level4-4.html")

    elif request.method == "POST":
        return """恭喜你成功使用 post!
    你通过 URL 提交的数据是：
    {}
    你通过 post 提交的数据是：
    {}""".format(dict(request.args), dict(request.form))

    else:
        return "你好像使用了其他请求哦"


@app.route("/level4-5/")
def level4_5():
    return render_template("level4-5.html")


@app.route("/level4-5/<status_code>")
def status_handler(status_code):
    try:
        return abort(int(status_code)), status_code
    except LookupError:
        return "你好像输入了不合法的状态码哦"


@app.route("/level4-6/")
def level4_6():
    # print(request.headers)
    if "python" in request.headers.get("User-Agent"):
        return "你是爬虫吧？试试设置 User-Agent？"
    # if request.headers.get("Referer") is None or "python-site" not in request.headers.get("Referer"):
    if request.headers.get("Referer") is None:
        return "你是爬虫吧？试试设置 Referer？"
    return render_template("level4-6.html")


@app.route("/level4-7/")
def level4_7():
    row = randint(5, 10)
    col = randint(5, 10)
    target = (randint(0, row-1), randint(0, col-1))

    return render_template("level4-7.html", row=row, col=col, target=target)


magic_num = [-1, -1]
call_times = [0]


@app.route("/level4-8/")
def level4_8():
    init_num()
    return render_template("level4-8.html", num=0)


@app.route("/level4-8/<num>")
def level4_8_handle(num):
    if call_times[0] == 10:
        call_times[0] = 0
        return render_template("level4-8.html", num=magic_num[0], next_=23333)
    if num == str(23333):
        return "NICE WORK"
    if num == str(magic_num[0]):
        change_num()
        return render_template("level4-8.html", num=magic_num[0], next_=magic_num[0])
    return "你找错地方了"


@app.route("/level4-9/")
def level4_9():
    return render_template("level4-9.html")


@app.route("/level4-9/data")
def level4_9_handle():
    import time
    time.sleep(3)
    return "数据"


def init_num():
    call_times = 0
    magic_num.clear()
    magic_num.append(1)


def change_num():
    call_times[0] += 1
    magic_num.pop(0)
    magic_num.append(randint(1, 1000000))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
