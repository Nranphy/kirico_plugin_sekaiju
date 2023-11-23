from nonebot.internal.adapter import Adapter as BaseAdapter


class Adapter(BaseAdapter):
    
    @classmethod
    def get_name(cls) -> str:
        return "Example"