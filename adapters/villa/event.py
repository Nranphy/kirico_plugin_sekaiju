from nonebot.adapters.villa.event import (
    SendMessageEvent
)

from nonebot.adapters.villa.event import (
    EventType
)
from nonebot.adapters.villa.api import (
    User,
    Robot,
    Template,
    MessageContentInfoGet,
    TextMessageContent
)

from ...universal.uni_event import (
    Item,
    add_uni_event_items,
    UniGroupMessageEvent
)

from .utils import villa_adapter_name



parse_mapping = {
    "post_type": "other",
    "event_id": Item("id"),
    "time": Item("created_at"),
}
export_mapping = {
    # TODO 默认 Robot 可以采用设置中的机器人名称等内容
    "robot": Robot(villa_id=0, template=Template(id="", name="", icon="")),
    # "type": None,
    "id": Item("event_id"),
    "created_at": Item("time"),
    "send_at": Item("time"),
}

add_uni_event_items(
    SendMessageEvent,
    UniGroupMessageEvent,
    parse_mapping={
        **parse_mapping,
        "message_type": "group",
        "message_id": Item("msg_uid"),
        "user_id": Item("from_user_id"),
        "message": Item("message", is_msg=True, origin_adapter=villa_adapter_name),
        "to_me": Item("to_me"),
        "sub_type": "normal",
        "group_id": Item("room_id")
    },
    export_mapping={
        **export_mapping,
        "content": lambda uni_event: MessageContentInfoGet(
            # TODO 缺少通用用户模型
            user=User(
                portraitUri="",
                extra={},
                name="",
                alias="",
                id=uni_event.user_id,
                portrait=""
            ),
            content=TextMessageContent(text="")
        ),
        "from_user_id": Item("user_id"),
        "msg_uid": Item("message_id"),
        "room_id": Item("group_id"),
        "to_me": Item("to_me"),
        "message": Item("message", is_msg=True, target_adapter=villa_adapter_name),
        "raw_message": Item("message", is_msg=True, target_adapter=villa_adapter_name)
    }
)