import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from typing import Optional, Any
from base64 import b64decode
from pathlib import Path


adapter_name = Adapter.get_name()
'''适配器名称'''

adapter = nonebot.get_adapter(Adapter)
'''适配器实例'''

def s2b(s:str, default:bool = True) -> bool:
    '''将字符串转化为对应字面量布尔值或默认值'''
    _s = s.lower()
    if _s == "true":
        return True
    if _s == "false":
        return False
    return default

def s2f(s:str) -> dict[str, Any]:
    '''将媒体 MessageSegment 的 file 字段转化为参数字典'''
    res = {}
    if s.startswith("file:///"):
        res["_path"] = Path(s.strip("file:///"))
    if s.startswith("base64://"):
        b64 = s.strip("base64://")
        res["_bytes"] = b64decode(b64)
    return res