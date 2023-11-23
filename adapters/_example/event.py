'''
需要对原适配器每个 Event 类进行更改，
具体请参考 uni_event.py 文档。
'''

from .example_adapter import Event as ExampleEvent

from ...universal.uni_event import UniEvent, add_uni_event_items


add_uni_event_items(
    ExampleEvent,
    UniEvent, # 这里需要选择对应的 UniEvent，且下列参数表也要对应。
    {},
    {}
)