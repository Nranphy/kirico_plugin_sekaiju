'''
提供统一的 UniBot 基类与 FakeBot 标记类。

UniBot 负责实现统一接口，用对应的原 Bot 实现具体功能；
FakeBot 负责重写对应 Bot 的接口，用 UniBot 实现具体功能。

每个适配器需要实现以下内容：

1. 继承 UniBot 类，并重写 send 与 call_api 抽象方法。
其中， call_api 方法需要根据 UniBot 所给不同参数表进行处理。

2. 继承 FakeBot 类与该适配器原有 Bot 类，并重写相关方法为通过 UniBot 实现原有功能。
该类 __init__ 方法应仅有 UniBot 一个参数。

3. 通过 add_uni_bot_method 函数，为适配器原有 Bot 类添加相应方法。
'''

from abc import abstractmethod, ABC
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
    Type,
    Union,
    Optional
)
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot


if TYPE_CHECKING:
    from .uni_event import UniEvent
    from .uni_message import UniMessage


class UniBot(BaseBot):
    '''UniBot 基类。
    
    提供 Bot 基础通用接口。'''

    origin_bot: BaseBot
    '''构建该 UniBot 的原 Bot 实例'''
    
    @override
    def __init__(self, bot: BaseBot):
        self.origin_bot = bot

    @abstractmethod
    async def send(
        self,
        event: "UniEvent",
        message: Union[str, "UniMessage"],
        **kwargs: Any,
    ) -> Any:
        """
        调用机器人基础发送消息接口。

        参数:
            event: 上报事件
            message: 要发送的消息（此时一般是 UniMessage）
            kwargs: 任意额外参数
        """

    @abstractmethod
    async def call_api(
        self,
        api: str,
        **data: Any
    ) -> Any:
        """
        调用机器人 API 接口。

        一般需要根据所支持的不同平台 API 的映射表进行转换。

        参数:
            api: API 名称
            data: API 数据
        """


class FakeBot(ABC):
    '''通过 UniBot 实现原 Bot 功能的 FakeBot 类标记。'''

    uni_bot: UniBot

    def __init__(self, uni_bot: UniBot):
        '''__init__ 方法应仅有 UniBot 一个参数'''
        self.uni_bot = uni_bot
        self.id = uni_bot.origin_bot.self_id


def add_bot_method(
        origin_bot_cls: Type[BaseBot],
        uni_bot_cls: Optional[Type[UniBot]] = None,
        fake_bot_cls: Optional[Type[FakeBot]] = None
    ):
    """
    为 Bot 类添加获取对应 UniBot 与构建对应 FakeBot 的方法。

    :param origin_bot_cls: 原 Bot 类。
    :param uni_bot_cls:
        所给 Bot 类对应的 UniBot 类。
        将为 Bot 类添加 uni_bot_cls 字段与 get_uni_bot 方法，通过 get_uni_bot 获取对应 UniBot 实例。
        留空则代表 Bot 不支持转 UniBot.
    :param fake_bot_cls:
        所给 Bot 类对应的 FakeBot 类。
        将为 Bot 类添加 fake_bot_cls 字段与 parse_fake_bot 方法。
        留空则代表 Bot 不支持从 UniBot 构建 FakeBot.
    """
    if uni_bot_cls is not None:
        setattr(origin_bot_cls, "uni_bot_cls", uni_bot_cls)
        def get_uni_bot(self):
            return cast(Type[UniBot], self.uni_bot_cls)(self)
        setattr(origin_bot_cls, "get_uni_bot", get_uni_bot)

    if fake_bot_cls is not None:
        setattr(origin_bot_cls, "fake_bot_cls", fake_bot_cls)
        @classmethod
        def parse_fake_bot(cls, uni_bot: UniBot) -> FakeBot:
            return cast(Type[FakeBot], cls.fake_bot_cls)(uni_bot)
        setattr(origin_bot_cls, "parse_fake_bot", parse_fake_bot)


def check_uni_bot_support(bot_or_cls: Union[BaseBot, Type[BaseBot]]) -> bool:
    '''检查 Bot 类或实例是否支持转化为 UniBot'''
    return hasattr(bot_or_cls, "uni_bot_cls")

def check_fake_bot_support(bot_or_cls: Union[BaseBot, Type[BaseBot]]) -> bool:
    '''检查 Bot 类或实例是否支持从 UniBot 构建 FakeBot'''
    return hasattr(bot_or_cls, "fake_bot_cls")


__all__ = [
    "UniBot",
    "FakeBot",
    "check_uni_bot_support",
    "check_fake_bot_support"
]