import nonebot

from .config import config
from .utils import logger, SUPPORTED_ADAPTERS, support_adapters_info
from .modifiers import MODIFIERS



registered_adapters: list[str] = []

sekaiju_adapters: list[str] = []
'''完成世界树代理适配器激活的适配器名称列表'''


logger("INFO", "开始注册所选适配器...")
driver = nonebot.get_driver()
for adapter_name in config.sekaiju_adapters:
    if adapter_name not in SUPPORTED_ADAPTERS:
        logger("ERROR", f"{adapter_name} 适配器未被世界树支持，请检查拼写是否有误。")
        continue
    
    try:
        support_adapters_info[adapter_name].register_adapter()
    except ModuleNotFoundError:
        logger("ERROR", f"{adapter_name} 适配器导入失败，请检查适配器是否正确安装。")
        continue
    
    registered_adapters.append(adapter_name)
    logger("DEBUG", f"{adapter_name} 适配器已确认导入并注册。")

if registered_adapters:
    logger("INFO", f"确认注册适配器完成，成功注册的适配器有 {', '.join(registered_adapters)}")
else:
    logger("INFO", f"当前不存在被世界树成功注册的适配器。")


logger("INFO", "激活世界树代理适配器中...")
for adapter_name in registered_adapters:
    try:
        support_adapters_info[adapter_name].import_sekaiju_adapter()
    except ModuleNotFoundError:
        logger("ERROR", f"{adapter_name} 激活世界树代理适配器时失败，请检查对应 AdapterInfo 内容或对应世界树适配器模块是否有误。")
        continue
    
    sekaiju_adapters.append(adapter_name)
    logger("DEBUG", f"{adapter_name} 适配器已完成代理适配器激活。")

if sekaiju_adapters:
    logger("INFO", f"激活代理适配器完成，当前受世界树代理的适配器有 {', '.join(sekaiju_adapters)}")
else:
    logger("INFO", f"当前没有受世界树代理的适配器。")

if sekaiju_adapters:
    logger("INFO", "修改 NoneBot2 部分功能中...")
    for param in MODIFIERS:
        param.main()
        logger("DEBUG", f"运行 {param.__name__} 完成。")
    logger("INFO", "修改 NoneBot2 部分功能完成。")
else:
    logger("INFO", "由于当前没有受世界树代理的适配器，已跳过对 NoneBot2 的功能修改。")



__all__ = [
    "sekaiju_adapters"
]