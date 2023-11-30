from typing import Type, Union, Callable, Optional
from importlib import import_module
from dataclasses import dataclass
from pathlib import Path
from hashlib import md5
from io import BytesIO
import httpx

import nonebot
from nonebot.utils import logger_wrapper
from nonebot.adapters import Adapter



logger = logger_wrapper("世界树")
'''世界树日志记录函数'''


temp_data_path = Path("./data/temp/sekaiju")
'''插件临时文件存放目录'''
temp_data_path.mkdir(parents=True, exist_ok=True)


@dataclass
class AdapterInfo:
    '''适配器信息类'''

    pypi_name: str
    '''适配器 pypi 名称，如 nonebot-adapter-onebot'''
    adapter_module_name: str
    '''适配器模块名称，如 nonebot.adapters.onebot.v11'''
    sekaiju_adapter_name: str
    '''世界树适配器名称，如 onebot_v11'''
    adapter_param_name: str = "Adapter"
    '''适配器内 Adapter 类变量名，一般为 Adapter'''
    sekaiju_adapter_prefix: str = ".adapters."
    '''世界树适配器路径前缀'''
    adapter_cls: Optional[Type[Adapter]] = None
    '''对应 Adapter 类'''

    @property
    def adapter_name(self) -> str:
        '''Adapter 类 get_name 方法所给名称'''
        if self.adapter_cls is None:
            raise ValueError("当前适配器未指定 Adapter 类。")
        return self.adapter_cls.get_name()

    @property
    def adapter(self) -> Adapter:
        '''对应 Adapter 实例'''
        if self.adapter_cls is None:
            raise ValueError("当前适配器未指定 Adapter 类。")
        return nonebot.get_adapter(self.adapter_cls)

    @property
    def sekaiju_adapter_module_name(self) -> str:
        '''世界树适配器模块名称，如 .adapter.onebot_v11'''
        return self.sekaiju_adapter_prefix + self.sekaiju_adapter_name
    
    def register_adapter(self):
        logger("DEBUG", f"注册适配器 {self.pypi_name} 中...")
        adapter_module = import_module(self.adapter_module_name, __package__)
        _adapter: Type[Adapter] = getattr(adapter_module, self.adapter_param_name)
        self.adapter_cls = _adapter
        nonebot.get_driver().register_adapter(_adapter)
        logger("DEBUG", f"注册适配器 {self.pypi_name} 完成。")
    
    def import_sekaiju_adapter(self):
        logger("DEBUG", f"导入 {self.pypi_name} 所对应世界树适配器中...")
        import_module(self.sekaiju_adapter_module_name, __package__)
        logger("DEBUG", f"导入 {self.pypi_name} 所对应世界树适配器完成")


support_adapters_info = {
    "nonebot-adapter-onebot": AdapterInfo(
        "nonebot-adapter-onebot",
        "nonebot.adapters.onebot.v11",
        "onebot_v11"
    ),
    "nonebot-adapter-console": AdapterInfo(
        "nonebot-adapter-console",
        "nonebot.adapters.console",
        "console"
    ),
    "nonebot-adapter-villa": AdapterInfo(
        "nonebot-adapter-villa",
        "nonebot.adapters.villa",
        "villa"
    )
}
'''世界树所支持适配器信息'''

SUPPORTED_ADAPTERS = tuple(support_adapters_info.keys())
'''世界树所支持适配器 pypi 名称'''


def bytes_to_path(bytes_data: Union[bytes, BytesIO]) -> Path:
    '''将 bytes 存储在临时目录，返回文件的绝对路径'''
    if isinstance(bytes_data, BytesIO):
        bytes_data = bytes_data.getvalue()
    file_path = temp_data_path/md5(bytes_data).hexdigest()
    with open(file_path, "wb") as f:
        f.write(bytes_data)
    return file_path.absolute()

def url_to_bytes(url: str, **kwargs) -> bytes:
    '''从 url 地址获取数据'''
    resp = httpx.get(
        url,
        timeout=kwargs.get("timeout", 20)
    )
    return resp.content

def path_to_url(path: Union[str, Path]) -> str:
    if isinstance(path, str):
        path = Path(path)
    raise NotImplementedError("如需要从 path 或 bytes 构造网络 url，请自行实现该函数。")

def bytes_to_url(bytes_data: Union[bytes, BytesIO]) -> str:
    return path_to_url(bytes_to_path(bytes_data))

def url_to_path(url: str, **kwargs) -> Path:
    return bytes_to_path(url_to_bytes(url, **kwargs))

def path_to_bytes(path: Union[str, Path]) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    return data


ascii_map = {ch:str(i+10) for i,ch in enumerate("0123456789"+"ABCDEFGHIJKLMNOPQRSTUVWXYZ"+"abcdefghijklmnopqrstuvwxyz"+"~!@#$%^&*()_+`-=|:<>?[];,./")}
ascii_inverse_map = {v:k for k,v in ascii_map.items()}
MAX_STR_LENGTH = 300
Encoded = str
'''编码后字符串类型'''

def ascii_encode(s: Union[str, int]) -> Encoded:
    '''将字符串编码为数字字符串'''
    _s = str(s)
    if MAX_STR_LENGTH and len(_s) > MAX_STR_LENGTH:
        raise ValueError("所给的s过长。")
    res = ""
    for ch in _s:
        res += ascii_map[ch]
    return res

def ascii_decode(s: Union[Encoded, str, int]) -> str:
    '''将编码后的序列还原'''
    _s = str(s)
    s_length = len(_s)
    if s_length%2:
        raise ValueError("所给s长度为奇数，不是合法的序列。")
    res = ""
    for i in range(0, s_length, 2):
        try:
            res += ascii_inverse_map[_s[i:i+2]]
        except:
            raise ValueError("所给s并非合法序列。")
    return res


__all__ = [
    "logger",
    "temp_data_path",
    "support_adapters_info",
    "SUPPORTED_ADAPTERS",
    "bytes_to_path",
    "url_to_bytes",
    "path_to_url",
    "bytes_to_url",
    "url_to_path",
    "path_to_bytes",
    "ascii_encode",
    "ascii_decode"
]