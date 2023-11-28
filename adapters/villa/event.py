from nonebot.adapters.villa.event import (
    EventType,
    Event,
    NoticeEvent,
    JoinVillaEvent,
    SendMessageEvent
)

from nonebot.adapters.villa.models import (
    User,
    Robot,
    Template,
    MessageContentInfoGet,
    TextMessageContent
)

from ...universal.uni_event import (
    Item,
    add_uni_event_items,
    UniEvent,
    UniNoticeEvent,
    UniGroupMessageEvent,
    UniGroupIncreaseNoticeEvent
)

from typing import cast

from .utils import adapter_name, villa_room_id_convert
from ...utils import ascii_encode, ascii_decode



event_type_mapping = {
    EventType.JoinVilla: "notice",
    EventType.SendMessage: "message"
}



add_uni_event_items(
    Event,
    UniEvent,
    event_parse_mapping:={
        "post_type": lambda e: event_type_mapping.get(e.type, "other"),
        "event_id": Item("id", encode=True),
        "time": Item("send_at"),
        "self_id": Item("bot_id")
    },
    event_export_mapping:={
        "robot": lambda e: {
            "villa_id": 0, # 未保存 villa
            "template": {
                "id": e.self_id,
                "name": "机器人", # 未保存机器人名称,
                "icon": "" # 未保存机器人图标
            }
        },
        "type": EventType.SendMessage, # 未能一一对应事件类型
        "id": Item("event_id"),
        "created_at": Item("time"),
        "send_at": Item("time")
    }
)

add_uni_event_items(
    NoticeEvent,
    UniNoticeEvent,
    {
        **event_parse_mapping,
        "post_type": "notice",
        "notice_type": lambda e: "group_increase" if e.type is EventType.JoinVilla else "other",
    },
    {
        **event_export_mapping,
    }
)

add_uni_event_items(
    SendMessageEvent,
    UniGroupMessageEvent,
    {
        **event_parse_mapping,
        "post_type": "message",
        "message_type": "group",
        "message_id": Item("message_id", encode=True),
        "user_id": Item("from_user_id", encode=True),
        "message": Item("message", is_msg=True, origin_adapter=adapter_name),
        "to_me": Item("to_me"),
        "sub_type": "normal",
        "group_id": lambda e: ascii_encode(
            cast(str, villa_room_id_convert(
                "encode",
                e.villa_id,
                e.room_id
            )))
    },
    {
        **event_export_mapping,
        "content": lambda e: {
            "user": { # 未设定默认用户信息
                "portrait_uri": "",
                "extra": {},
                "name": "用户",
                "alias": "",
                "id": e.user_id,
                "portrait": ""
            },
            "trace": None
        },
        "from_user_id": Item("user_id"),
        "send_at": 0,
        "room_id": Item("group_id"),
        "object_name": 0,
        "nickname": "",
        "msg_uid": Item("message_id"),
        "villa_id": Item("group_id"),
        "message": Item("message", is_msg=True, target_adapter=adapter_name),
        "original_message": Item("message", is_msg=True, target_adapter=adapter_name)
    }
)

add_uni_event_items(
    JoinVillaEvent,
    UniGroupIncreaseNoticeEvent,
    {
        **event_parse_mapping,
        "notice_type": "group_increase",
        "sub_type": "approve",
        "group_id": Item("villa_id"),
        "user_id": Item("join_uid", encode=True)
    },
    {
        **event_export_mapping,
        "join_uid": Item("user_id"),
        "join_user_nickname": "用户",
        "join_at": 0,
        "villa_id": Item("group_id")
    }
)