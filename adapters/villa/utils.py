import nonebot
from nonebot.adapters.villa.adapter import Adapter


adapter_name = Adapter.get_name()
'''适配器名称'''

adapter = nonebot.get_adapter(Adapter)
'''适配器实例'''