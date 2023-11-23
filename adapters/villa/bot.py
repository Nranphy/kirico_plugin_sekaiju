from typing_extensions import override
from typing import TYPE_CHECKING, Union, Any, cast

from nonebot.adapters.villa import (
    Bot as VillaBot,
    Adapter as VillaAdapter
)
from nonebot.adapters.villa.config import BotInfo
from nonebot.adapters.villa.event import Event
from nonebot.adapters.villa.message import Message, MessageSegment

from ...universal.uni_bot import UniBot, FakeBot
from ...universal.uni_message import UniMessage

if TYPE_CHECKING:
    from ...universal.uni_event import UniEvent
    


class VillaUniBot(UniBot):

    @override
    def __init__(self, bot: VillaBot):
        self.origin_bot = bot

    @override
    async def send(
        self,
        event: "UniEvent",
        message: Union[str, UniMessage],
        **kwargs: Any,
    ) -> Any:
        if isinstance(message, UniMessage):
            _message = message.export(self.origin_bot.adapter.get_name())
        else:
            _message = message
        return await self.origin_bot.send(event.origin_event, _message, **kwargs)

class VillaFakeBot(FakeBot, VillaBot):

    @override
    def __init__(self, uni_bot: UniBot):
        fake_adapter = cast(VillaAdapter, ...)
        fake_self_id = "VillaFakeBot"
        fake_bot_info = BotInfo(
            bot_id="",
            bot_secret="",
            pub_key="",

        )
        FakeBot.__init__(self, uni_bot)
        VillaBot.__init__(
            self,
            fake_adapter,
            fake_self_id,
            fake_bot_info
        )
    
    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any
    ) -> str:
        if isinstance(message, MessageSegment):
            message = message.get_message_class()(message)
        if isinstance(message, Message):
            _message = UniMessage.generate(VillaAdapter.get_name(), message)
        else:
            _message = message
        return await  self.uni_bot.send(
            getattr(event, "get_uni_event")(),
            _message,
            **kwargs
        )