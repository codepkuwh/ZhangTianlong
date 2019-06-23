'''需求
自动生成评价

根据5个维度，以及5个维度的评分进行随机选择
五个维度
    计算思维
    逻辑思维
    问题分析
    动手实践
    创新思维
分数范围：6~10
'''

from random import choice, shuffle, randint
import json
import os


def gen_comments(scores):
    '''
    input 五元列表，依次是5个维度的评分
    '''

    with open(os.path.join(os.path.dirname(__file__), "comments.json"), encoding="utf-8") as f:
        c_dict = json.load(f)
        ref = list(c_dict.keys())  # 获取评价维度
        shuffle(ref)  # 打乱排序

        txt = ""
        for i, key in enumerate(ref):
            # print(key, i)
            txt = txt + choice(c_dict[key][str(scores[i])]) + "，"
        print(txt)


def test():
    for _ in range(10):
        l = [randint(6, 10), randint(6, 10), randint(6, 10), randint(6, 10), randint(6, 10), randint(6, 10)]
        print("input:", l)
        gen_comments(l)

test()