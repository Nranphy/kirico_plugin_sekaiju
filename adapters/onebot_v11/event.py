from nonebot.adapters.onebot.v11 import Adapter
from nonebot.adapters.onebot.v11 import (
    Event,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    NoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupBanNoticeEvent,
    FriendAddNoticeEvent,
    GroupRecallNoticeEvent,
    FriendRecallNoticeEvent,
    NotifyEvent,
    PokeNotifyEvent,
    LuckyKingNotifyEvent,
    HonorNotifyEvent,
    RequestEvent,
    FriendRequestEvent,
    GroupRequestEvent,
    MetaEvent,
    LifecycleMetaEvent,
    HeartbeatMetaEvent
)

from ...universal.uni_event import (
    Item,
    add_uni_event_items,
    UniEvent,
    UniMessageEvent,
    UniPrivateMessageEvent,
    UniGroupMessageEvent,
    UniNoticeEvent,
    UniGroupIncreaseNoticeEvent,
    UniGroupDecreaseNoticeEvent,
    UniGroupBanNoticeEvent,
    UniRecallNoticeEvent,
    UniGroupRecallNoticeEvent,
    UniPrivateRecallNoticeEvent,
    UniFriendAddNoticeEvent,
    UniSimpleInteractionNoticeEvent,
    UniRequestEvent,
    UniFriendRequestEvent,
    UniGroupRequestEvent,
    UniMetaEvent,
    UniLifecycleMetaEvent,
    UniHeartbeatMetaEvent
)


add_uni_event_items(
    Event,
    UniEvent,
    event_parse_mapping:={
        "post_type": Item("post_type"),
        "event_id": lambda e: e.get_session_id(),
        "time": Item("time"),
        "self_id": Item("self_id", encode=True),
    },
    event_export_mapping:={
        "time": Item("time"),
        "self_id": Item("self_id"),
        "post_type": Item("post_type")
    }
)

add_uni_event_items(
    MessageEvent,
    UniMessageEvent,
    message_event_parse_mapping:={
        **event_parse_mapping,
        "post_type": "message",
        "message_type": Item("message_type"),
        "message_id": Item("message_id", encode=True),
        "user_id": Item("user_id", encode=True),
        "message": Item("message", is_msg=True, origin_adapter=Adapter),
        "to_me": Item("to_me"),
        "raw_message": Item("raw_message")
    },
    message_event_export_mapping:={
        **event_export_mapping,
        "post_type": "message",
        "sub_type": "other",
        "user_id": Item("user_id"),
        "message_type": Item("message_type"),
        "message_id": Item("message_id"),
        "message": Item("message", is_msg=True, target_adapter=Adapter),
        "original_message": Item("message", is_msg=True, target_adapter=Adapter),
        "raw_message": str(Item("message", is_msg=True, target_adapter=Adapter)),
        "font": 0,
        "sender": {},
        "to_me": Item("to_me")
    }
)

add_uni_event_items(
    PrivateMessageEvent,
    UniPrivateMessageEvent,
    {
        **message_event_parse_mapping,
        "sub_type": Item("sub_type")
    },
    {
        **message_event_export_mapping,
        "message_type": "private"
    }
)

add_uni_event_items(
    GroupMessageEvent,
    UniGroupMessageEvent,
    {
        **message_event_parse_mapping,
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id", encode=True)
    },
    {
        **message_event_export_mapping,
        "message_type": "group",
        "group_id": Item("group_id")
    }
)

add_uni_event_items(
    NoticeEvent,
    UniNoticeEvent,
    notice_event_parse_mapping:={
        **event_parse_mapping,
        "post_type": "notice",
        "notice_type": "other"
    },
    notice_event_export_mapping:={
        **event_export_mapping,
        "post_type": "notice",
        "notice_type": Item("notice_type")
    }
)

add_uni_event_items(
    GroupIncreaseNoticeEvent,
    UniGroupIncreaseNoticeEvent,
    {
        **notice_event_parse_mapping,
        "notice_type": "group_increase",
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id", encode=True),
        "operator_id": Item("operator_id", encode=True),
        "user_id": Item("user_id", encode=True)
    },
    {
        **notice_event_export_mapping,
        "notice_type": "group_increase",
        "sub_type": Item("sub_type"),
        "user_id": Item("user_id"),
        "group_id": Item("group_id"),
        "operator_id": Item("operator_id")
    }
)

add_uni_event_items(
    GroupDecreaseNoticeEvent,
    UniGroupDecreaseNoticeEvent,
    {
        **notice_event_parse_mapping,
        "notice_type": "group_decrease",
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id", encode=True),
        "operator_id": Item("operator_id", encode=True),
        "user_id": Item("user_id", encode=True)
    },
    {
        **notice_event_export_mapping,
        "notice_type": "group_decrease",
        "sub_type": Item("sub_type"),
        "user_id": Item("user_id"),
        "group_id": Item("group_id"),
        "operator_id": Item("operator_id")
    }
)

add_uni_event_items(
    GroupBanNoticeEvent,
    UniGroupBanNoticeEvent,
    {
        **notice_event_parse_mapping,
        "notice_type": "group_ban",
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id", encode=True),
        "operator_id": Item("operator_id", encode=True),
        "user_id": Item("user_id", encode=True),
        "duration": Item("duration")
    },
    {
        **notice_event_export_mapping,
        "notice_type": "group_ban",
        "sub_type": Item("sub_type"),
        "user_id": Item("user_id"),
        "group_id": Item("group_id"),
        "operator_id": Item("operator_id"),
        "duration": Item("duration")
    }
)

recall_notice_event_parse_mapping = {
    **notice_event_parse_mapping,
    "user_id": Item("user_id", encode=True),
    "message_id": Item("message_id", encode=True)
}

add_uni_event_items(
    GroupRecallNoticeEvent,
    UniGroupRecallNoticeEvent,
    {
        **recall_notice_event_parse_mapping,
        "notice_type": "group_recall",
        "group_id": Item("group_id", encode=True),
        "operator_id": Item("operator_id", encode=True)
    },
    {
        **notice_event_export_mapping,
        "notice_type": "group_recall",
        "user_id": Item("user_id"),
        "group_id": Item("group_id"),
        "operator_id": Item("operator_id"),
        "message_id": Item("message_id")
    }
)

add_uni_event_items(
    FriendRecallNoticeEvent,
    UniPrivateRecallNoticeEvent,
    {
        **recall_notice_event_parse_mapping,
        "notice_type": "friend_recall",
    },
    {
        **notice_event_export_mapping,
        "notice_type": "friend_recall",
    }
)

add_uni_event_items(
    FriendAddNoticeEvent,
    UniFriendAddNoticeEvent,
    {
        **notice_event_parse_mapping,
        "notice_type": "friend_add",
        "user_id": Item("user_id", encode=True)
    },
    {
        **notice_event_export_mapping,
        "notice_type": "friend_add",
        "user_id": Item("user_id")
    }
)

add_uni_event_items(
    PokeNotifyEvent,
    UniSimpleInteractionNoticeEvent,
    {
        **notice_event_parse_mapping,
        "notice_type": "simple_interaction",
        "group_id": Item("group_id", encode=True),
        "user_id": Item("user_id", encode=True),
        "target_id": Item("target_id", encode=True)
    },
    {
        **notice_event_export_mapping,
        "notice_type": "notify",
        "sub_type": "poke",
        "user_id": Item("user_id"),
        "group_id": Item("group_id"),
        "target_id": Item("target_id")
    }
)

add_uni_event_items(
    RequestEvent,
    UniRequestEvent,
    request_event_parse_mapping:={
        **event_parse_mapping,
        "post_type": "request",
        "request_type": "other"
    },
    request_event_export_mapping:={
        **event_export_mapping,
        "post_type": "request",
        "request_type": Item("request_type")
    }
)

add_uni_event_items(
    FriendRequestEvent,
    UniFriendRequestEvent,
    {
        **request_event_parse_mapping,
        "request_type": "friend",
        "user_id": Item("user_id", encode=True),
        "comment": Item("comment"),
    },
    {
        **request_event_export_mapping,
        "request_type": "friend",
        "user_id": Item("user_id"),
        "comment": Item("comment"),
        "flag": ""
    }
)
# TODO 快捷方法 approve、reject 需要额外考虑

add_uni_event_items(
    GroupRequestEvent,
    UniGroupRequestEvent,
    {
        **request_event_parse_mapping,
        "request_type": "group",
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id", encode=True),
        "user_id": Item("user_id", encode=True),
        "comment": Item("comment")
    },
    {
        **request_event_export_mapping,
        "request_type": "group",
        "sub_type": Item("sub_type"),
        "group_id": Item("group_id"),
        "user_id": Item("user_id"),
        "comment": Item("comment"),
        "flag": ""
    }
)

add_uni_event_items(
    MetaEvent,
    UniMetaEvent,
    meta_event_parse_mapping:={
        **event_parse_mapping,
        "post_type": "meta",
        "meta_event_type": "other"
    },
    meta_event_export_mapping:={
        **event_export_mapping,
        "post_type": "meta_event",
        "meta_event_type": "other"
    }
)

add_uni_event_items(
    LifecycleMetaEvent,
    UniLifecycleMetaEvent,
    {
        **meta_event_parse_mapping,
        "meta_event_type": "lifecycle",
        "sub_type": Item("sub_type")
    },
    {
        **meta_event_parse_mapping,
        "meta_event_type": "lifecycle",
        "sub_type": Item("sub_type")
    }
)

add_uni_event_items(
    HeartbeatMetaEvent,
    UniHeartbeatMetaEvent,
    {
        **meta_event_parse_mapping,
        "meta_event_type": "heartbeat",
        "online": lambda e: e.status.online,
        "interval": Item("interval")
    },
    {
        **meta_event_parse_mapping,
        "meta_event_type": "heartbeat",
        "status": {"online": True, "good": True},
        "interval": Item("interval")
    }
)