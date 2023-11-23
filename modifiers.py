from abc import ABC, abstractmethod
from typing import (
    Any,
    cast,
    Type,
    List,
    Union,
    Optional
    )
from typing_extensions import override
from contextvars import ContextVar

from nonebot.dependencies import Param, Dependent
from nonebot.internal.params import (
    Depends,
    BotParam,
    EventParam
)
from nonebot.internal.matcher import (
    Matcher,
    current_bot,
    current_event
)
from nonebot.internal.adapter import (
    Bot,
    Event,
    Message,
    MessageSegment,
    MessageTemplate,
)

from .universal.uni_bot import (
    UniBot,
    check_uni_bot_support,
    check_fake_bot_support
)
from .universal.uni_event import (
    UniEvent,
    check_uni_event_support
)
from .universal.uni_message import convert_message



class Modifier(ABC):
    '''用以包装对 NoneBot2 框架部分内容进行修改的函数'''

    @classmethod
    @abstractmethod
    def main(cls):
        '''对框架代码进行修改'''


class ParamModifier(Modifier):
    '''用以包装对 NoneBot2 框架 Param 类进行修改的函数'''

    param_cls: Type[Param]

    @classmethod
    @abstractmethod
    def main(cls):
        '''对相应的 Param 进行修改'''


class BotParamModifier(ParamModifier):
    '''修改 NoneBot2 框架的 BotParam 类'''

    param_cls: Type[Param] = BotParam

    @staticmethod
    def _check_decorator(func):
        async def inner(
            self,
            bot: Bot,
            **kwargs: Any
        ) -> None:
            setattr(self, "target_bot_cls", None)
            if checker := self.extra.get("checker"):
                # TODO 目前只支持 handler 依赖注入 Bot 仅有单个类型的情况
                try:
                    if all(
                        [
                            issubclass((param_type := checker.type_), Bot),
                            type(bot) is not param_type,
                            check_uni_bot_support(bot),
                            check_fake_bot_support(param_type)
                        ]
                    ):
                        setattr(self, "target_bot_cls", param_type)
                        return
                except TypeError:
                    pass
            return await func(self, bot, **kwargs)
        return inner
    
    @staticmethod
    def _solve_decorator(func):
        async def inner(
            self,
            bot: Bot,
            **kwargs: Any
        ) -> Any:
            if hasattr(self, "target_bot_cls") and getattr(self, "target_bot_cls") is not None:
                return getattr(cast(Type[Bot], getattr(self, "target_bot_cls")), "parse_fake_bot")(getattr(bot, "get_uni_bot")())
            return await func(self, bot, **kwargs)
        return inner
    
    @classmethod
    @override
    def main(cls):
        cls.param_cls._check = cls._check_decorator(cls.param_cls._check)
        cls.param_cls._solve = cls._solve_decorator(cls.param_cls._solve)


class EventParamModifier(ParamModifier):
    '''修改 NoneBot2 框架的 EventParam 类'''

    param_cls: Type[Param] = EventParam

    @staticmethod
    def _check_decorator(func):
        async def inner(
            self,
            event: Event,
            **kwargs: Any
        ) -> None:
            setattr(self, "target_event_cls", None)
            if checker := self.extra.get("checker"):
                # TODO 目前只支持 handler 依赖注入 Event 仅有单个类型的情况
                try:
                    if all(
                        [
                            issubclass((param_type := checker.type_), Event),
                            type(event) is not param_type,
                            not issubclass(type(event), param_type),
                            check_uni_event_support(event),
                            check_uni_event_support(param_type)
                        ]
                    ):
                        param_uni_event = getattr(param_type, "uni_event")
                        current_uni_event = getattr(type(event), "uni_event")
                        if issubclass(current_uni_event, param_uni_event):
                            setattr(self, "target_event_cls", param_type)
                            return
                except TypeError:
                    pass
            return await func(self, event, **kwargs)
        return inner
    
    @staticmethod
    def _solve_decorator(func):
        async def inner(
            self,
            event: Event,
            **kwargs: Any
        ) -> Any:
            if hasattr(self, "target_event_cls") and getattr(self, "target_event_cls") is not None:
                return getattr(cast(Type[Event], getattr(self, "target_event_cls")), "parse_fake_event")(getattr(event, "get_uni_event")())
            return await func(self, event, **kwargs)
        return inner
    
    @classmethod
    @override
    def main(cls):
        cls.param_cls._check = cls._check_decorator(cls.param_cls._check)
        cls.param_cls._solve = cls._solve_decorator(cls.param_cls._solve)

# TODO ArgParam 等 Param 需要对消息进行预处理，需要更改


class MatcherModifier(Modifier):
    '''修改 NoneBot2 框架 Matcher 类'''

    @staticmethod
    def _matcher_send_decorator(func):
        @classmethod
        async def inner(
            cls,
            message: Union[str, Message, MessageSegment, MessageTemplate],
            **kwargs: Any
        ) -> Any:
            if isinstance(message, MessageSegment):
                message = message.get_message_class()(message)
            if isinstance(message, Message) and hasattr(message, "adapter_name"):
                msg_adapter = cast(str, getattr(message, "adapter_name"))
                target_adapter = current_bot.get().adapter.get_name()
                if msg_adapter != target_adapter:
                    message = cast(Message, convert_message(message, msg_adapter, target_adapter))
            return await func(cls, message, **kwargs)
        return inner

    @classmethod
    @override
    def main(cls):
        setattr(Matcher, "send", cls._matcher_send_decorator(Matcher.send))


MODIFIERS: List[Type[Modifier]] = [
    BotParamModifier,
    EventParamModifier,
    MatcherModifier
]
'''ParamModifier 列表，运行 main 方法进行 Param 的更改'''

__all__ = [
    "MODIFIERS"
]