# ./config/libs.py
from datetime import datetime


def horaagora(printc: bool = False):
    content = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if printc:
        print(content)
    return content
