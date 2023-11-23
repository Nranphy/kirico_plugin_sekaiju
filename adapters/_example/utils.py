'''
用于放置其他模块通用的工具。
'''

import nonebot
from .example_adapter import Adapter


adapter_name = Adapter.get_name()
'''适配器名称'''

adapter = nonebot.get_adapter(Adapter)
'''适配器实例'''