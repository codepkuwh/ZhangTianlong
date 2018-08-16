# -*- coding: utf-8 -*-
import types
import sys
from functools import wraps


# 自定义异常，用于保存递归时参数的变化
class TailRecurseException(BaseException):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_call_optimized(func):
    """
    尾递归优化的装饰器. 如果不是其祖父，则抛出一个异常携带函数参数, 
    然后捕获异常携带的参数继续调用.

    非尾递归会报错.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        f = sys._getframe()  # 获取栈帧
        # 在调用栈中，top 和祖父节点是同一函数对象时，即调用过程为 warpper -> fib -> wapper
        # 这时发生了递归，抛出异常用于捕获函数的参数
        # 发生异常后，异常向上传递，同时传递异常的函数 pop 出栈，直到前一个 warpper 中异常被处理
        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while True:
                try:
                    return func(*args, **kwargs)
                except TailRecurseException as e:
                    # 更新参数
                    args = e.args
                    kwargs = e.kwargs

    return wrapper


def tramp(gen, *args, **kwargs):
    g = gen(*args, **kwargs)
    while isinstance(g, types.GeneratorType):  # 不停的 next 直到 fib return cur
        g = next(g)
    return g # return cur


@tail_call_optimized
def fib(count, cur=0, next_=1):
    if count <= 1:
        return cur
    else:
        # 尾递归版本的 fib
        return fib(count - 1, next_, cur + next_)


def fib2(count, cur=0, next_=1):
    if count <= 1:
        yield cur  # 计数为 1 时，返回 cur
    else:
        # 尾递归版本的 fib，使用生成器
        yield fib2(count - 1, next_, cur + next_)  # 生成一个生成器，传递变量


print(fib(10000) == tramp(fib2, 10000))

