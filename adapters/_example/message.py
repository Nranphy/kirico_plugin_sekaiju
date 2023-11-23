'''
需要围绕原适配器的 Message 进行更改，
具体请参考 uni_message.py 文档。
'''

from .example_adapter import Adapter as ExampleAdapter
from .example_adapter import Message as ExampleMessage

from ...universal.uni_message import UniMessage, add_message_change


def generate_func(ori_msg: ExampleMessage) -> UniMessage:
    '''通过 ExampleMessage 类构造 UniMessage'''
    ...

def export_func(uni_msg: UniMessage) -> ExampleMessage:
    '''通过 UniMessage 构造 ExampleMessage'''
    ...


add_message_change(
    ExampleAdapter,
    generate_func,
    export_func,
    ExampleMessage
)