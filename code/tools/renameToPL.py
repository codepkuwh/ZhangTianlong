# -*- coding: utf-8 -*-
"""
格式化录屏并移动到指定目录,
使用前先修改配置
"""
import os
import time
import shutil

# 自己的名字
USER_NAME = "张天龙"
# 录屏文件所在目录
dir_name = r"./"
# 目标文件目录
target_dir = r"D:\python\python-张天龙\课堂录屏\PL{0}\C{1}"

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

def time_stamp_to_time(timestamp):
    """
    转换时间格式
    """
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y%m%d',timeStruct)

# 找到录屏文件
filename_list = [file_ for file_ in os.listdir(dir_name) if ".mp4" in file_]

# 遍历录屏文件
for filename in filename_list:   
    # 输入level和进度
    level = input("请输入文件{}的level：\n".format(filename)) 
    section = input("请输入文件{}的进度（节数）：（使用数字）\n".format(filename)) 
    class_ = input("请输入文件{}的班级：（使用数字）\n".format(filename)) 

    # 转化时间格式
    date = time_stamp_to_time(os.path.getmtime(os.path.join(dir_name, filename)))

    # 格式化命名
    new_name = "{0}_P_L{1}_C{2}_第{3}节_张天龙.mp4".format(date, level, class_, section_dict[section])
    os.rename(filename, new_name)

    # 判断目录是否存在
    if not os.path.exists(target_dir.format(level, class_)):
        os.makedirs(target_dir.format(level, class_))

    # 移动文件到目标目录
    shutil.move(os.path.join(dir_name, new_name), target_dir.format(level, class_)) 
    
input()