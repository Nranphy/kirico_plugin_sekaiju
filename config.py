from nonebot import get_driver

from pydantic import BaseModel



class Config(BaseModel):
    sekaiju_adapters: list[str] = [
        "nonebot-adapter-onebot",
        "nonebot-adapter-console",
        "nonebot-adapter-villa"
    ]
    '''需要适配的 adapter 列表'''

config = Config.parse_obj(get_driver().config)
'''当前插件配置'''