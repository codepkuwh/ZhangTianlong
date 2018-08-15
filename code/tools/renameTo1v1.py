# -*- coding: utf-8 -*-
import os
import time
import shutil

# 自己的名字
USER_NAME = "张天龙"
# 录屏文件所在目录
dir_name = r"./"
# 目标文件目录
target_dir = r"D:\python\python-张天龙\课堂录屏\1V1"

def time_stamp_to_time(timestamp):
    """
    转换时间格式
    """
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y%m%d',timeStruct)

filename_list = [file_ for file_ in os.listdir(dir_name) if ".mp4" in file_]

for filename in filename_list:
    # 防止一天多节1v1导致重名，输入名字作为区别
    std_name = input("请输入文件{}的学生姓名：\n".format(filename))

    # 转化时间格式
    date = time_stamp_to_time(os.path.getmtime(os.path.join(dir_name, filename)))
    
    # 格式化命名
    new_name = "{0}_P_{1}1v1试听_张天龙.mp4".format(date, std_name)
    os.rename(filename, new_name)

    # 移动文件到目标目录
    shutil.move(os.path.join(dir_name, new_name), target_dir) 
    
input()