import os
from dotenv import load_dotenv

a = None
b = None
if not a or b:
    print('1')
else:
    print('2')


c = None
if not c:
    print('a')
else:
    print('b')

load_dotenv()
name = os.getenv('ENV1')
print(name)

