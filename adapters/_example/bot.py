'''
需要围绕原适配器的 Bot 类进行更改，
具体请参考 uni_bot.py 文档。
'''

from typing import Union, Any
from typing_extensions import override

from .example_adapter import Bot as ExampleBot

from ...universal.uni_bot import UniBot, FakeBot, add_bot_method
from ...universal.uni_event import UniEvent
from ...universal.uni_message import UniMessage


class ExampleUniBot(UniBot):

    origin_bot: ExampleBot

    @override
    async def send(
        self,
        event: UniEvent,
        message: Union[str, UniMessage],
        **kwargs: Any,
    ) -> Any:
        '''使用 ExampleBot 接口完成操作'''
    
    @override
    async def call_api(
        self,
        api: str,
        **data: Any
    ) -> Any:
        '''根据 UniBot 文档所提供的 API，调用 ExampleBot 完成操作。'''


class ExampleFakeBot(FakeBot, ExampleBot):
    '''
    先后继承 FakeBot 和 ExampleBot，
    保证 FakeBot.__init__ 方法被默认调用，它将唯一参数的 UniBot 设为 self.uni_bot 字段。

    之后根据 ExampleBot 的接口进行重写，操作均通过 UniBot 完成。
    '''

    @override
    def __init__(self, uni_bot: UniBot):
        super().__init__(uni_bot)
        ...


add_bot_method(
    ExampleBot,
    ExampleUniBot,
    ExampleFakeBot
)