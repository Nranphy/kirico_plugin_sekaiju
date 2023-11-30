from typing import Union, Any, cast
from typing_extensions import override

from nonebot.adapters.onebot.v11 import (
    Bot as OneBotv11Bot,
    Event as OneBotv11Event,
    Message as OneBotv11Message,
    MessageSegment as OneBotv11MessageSegment
)

from ...universal.uni_bot import UniBot, FakeBot, add_bot_method
from ...universal.uni_event import UniEvent
from ...universal.uni_message import UniMessage, convert_message

from .utils import adapter_name, adapter


class OneBotv11UniBot(UniBot):

    origin_bot: OneBotv11Bot

    @override
    async def send(
        self,
        event: UniEvent,
        message: Union[str, UniMessage],
        **kwargs: Any,
    ) -> Any:
        if isinstance(message, UniMessage):
            _message = message.export(
                adapter_name,
                bot=self.origin_bot
            )
        else:
            _message = message
        return await self.origin_bot.send(
            cast(OneBotv11Event, event.origin_event),
            cast(OneBotv11Message, _message),
            **kwargs
        )
    
    @override
    async def call_api(
        self,
        api: str,
        **data: Any
    ) -> Any:
        ...


class OneBotv11FakeBot(FakeBot, OneBotv11Bot):

    @override
    def __init__(self, uni_bot: UniBot):
        # TODO 未通过父类 Bot.__init__ 方法构造
        super().__init__(uni_bot)
        self.adapter = adapter
    
    @override
    async def send(
        self,
        event: OneBotv11Event,
        message: Union[str, OneBotv11Message, OneBotv11MessageSegment],
        **kwargs: Any,
    ) -> Any:
        if isinstance(message, str):
            _message = message
        else:
            _message = UniMessage.generate(
                adapter=adapter_name,
                origin_message=message,
                encode=False
            )
        return await self.uni_bot.send(
            cast(UniEvent, getattr(event, "uni_event")),
            cast(Union[str, UniMessage], _message),
            **kwargs
        )


add_bot_method(
    OneBotv11Bot,
    OneBotv11UniBot,
    OneBotv11FakeBot
)