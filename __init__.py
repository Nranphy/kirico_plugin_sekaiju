from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name = 'kirico_plugin_sekaiju',
    description = "实现插件多平台适配的世界树插件",
    usage =
'''
在不修改插件与适配器代码的前提下，适配多平台消息响应。
''',
    extra={
        "author": "Nranphy",
        "visible": False,
        "default_enable": True
    }
)



from .functions import sekaiju_adapters