import time


def time_test(func):
    def inner(*arg, **kwargs):
        start_time = time.time()
        result = func(*arg, **kwargs)
        end_time = time.time()
        print('开始时间戳：', start_time)
        print('结束时间戳：', end_time)
        print('%s函数执行时间：' % func.__name__, end_time - start_time)
        return result
    return inner


def async_decorator(async_func):
    async def wrapper(*args, **kwargs):
        print(f"Before calling {async_func.__name__}")
        response = await async_func(*args, **kwargs)
        print(f"After calling {async_func.__name__}")
        return response
    return wrapper
