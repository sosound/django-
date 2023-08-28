import string
import random


# 生成特定长度的验证码，包含数字和字母
def generate_verification_code(length):
    # 定义验证码中包含的字符类型
    chars = string.ascii_letters + string.digits  # 包含大小写字母和数字
    # 使用random.choices方法生成随机验证码
    code = ''.join(random.choices(chars, k=length))
    return code
