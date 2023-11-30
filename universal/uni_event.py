'''
提供各种的 UniEvent 基类。

每个适配器需要考虑每个事件是否需要与某个 UniEvent 关联。

若需要关联，则需要调用 add_uni_event_items 为该 Event 类添加目标 UniEvent 与字段映射 mapping，
具体请参见 Item 与 add_uni_event_items 函数文档。

如不对 Event 做出更改，则保持原有行为。
'''

from typing import (
    cast,
    Type,
    Union,
    Literal,
    Optional,
    Callable,
    Any
)
from pydantic import parse_obj_as, BaseModel
from dataclasses import dataclass, field
from collections import defaultdict
from inspect import iscoroutinefunction

from nonebot.internal.adapter import Event as BaseEvent
from nonebot.internal.adapter import Adapter, Bot

from .uni_message import UniMessage, convert_message
from ..utils import ascii_encode, ascii_decode, Encoded



@dataclass
class Item:
    """
    用于指代对应类的字段名，也可设定函数对该字段进行处理。

    :param name: 对应类的字段名。
    :param default: 指定对应类的字段不存在时的默认取值。
    :param call: 
        作用于对应字段值的函数。
        若给定 call ，则会另将对应字段值传入该 Callable 对象，以返回结果作为最终结果。
    :param is_msg: 
        所指定字段是否为 Message 对象。若是，则会自动根据 origin_adapter 与 target_adapter 构造覆盖 call。
    :param origin_adapter:
        仅当 is_msg=True 时生效。代表指定字段消息的适配器名称，留空代表从 UniMesssage 进行转换。
    :param target_adapter:
        仅当 is_msg=True 时生效。代表目标消息类型的适配器名称，留空代表转化为 UniMesssage。
    :param from_origin_kwargs:
        将原消息转化为 UniMessage 时传入对应转换函数的额外参数。
    :param to_target_kwargs:
        将 UniMessage 导出为目标消息时传入对应转换函数的额外参数。
    :param encode: 
        将 call 用 utils.ascii_encode 函数覆盖，用于适配 id 等 Union[int,str] 字段。
        一般用于转入通用模式时。
    :param decode: 
        将 call 用 utils.ascii_decode 函数覆盖，用于适配 id 等 Union[int,str] 字段。
        一般用于从通用模式转出。
    """

    name: str
    default: Optional[Any] = None
    call: Optional[Callable] = None
    is_msg: bool = False
    origin_adapter: Optional[Union[str, Adapter, Type[Adapter]]] = None
    target_adapter: Optional[Union[str, Adapter, Type[Adapter]]] = None
    from_origin_kwargs: dict[str, Any] = field(default_factory=dict)
    to_target_kwargs: dict[str, Any] = field(default_factory=dict)
    encode: bool = False
    decode: bool = False

    def __post_init__(self):
        if self.call is not None and not isinstance(self.call, Callable):
            raise ValueError("Item.call 必须为 Callable 对象。")
        if self.is_msg:
            if self.origin_adapter is None and self.target_adapter is None:
                raise ValueError("Item.origin_adapter 与 Item.target_adapter 需要至少有一个不为空。")
            async def inner_1(msg):
                return await convert_message(
                    message=msg,
                    origin_adapter=self.origin_adapter,
                    target_adapter=self.target_adapter,
                    from_origin_kwargs=self.from_origin_kwargs,
                    to_target_kwargs=self.to_target_kwargs
                )
            self.call = inner_1
        if self.encode or self.decode:
            if self.is_msg:
                raise ValueError("Item.is_msg 与 Item.encode、Item.decode 不能同时为 True.")
            if self.encode and self.decode:
                raise ValueError("Item.encode、Item.decode 仅能有一个为 True.")
            if self.encode:
                self.call = ascii_encode
            elif self.decode:
                self.call = ascii_decode
        if self.call is not None and not iscoroutinefunction(self.call):
            def inner_2(func):
                async def inner_3(*args, **kwargs):
                    return func(*args, **kwargs)
                return inner_3
            self.call = inner_2(self.call)


class UniEvent(BaseModel):
    '''事件标记基类'''

    origin_event: BaseEvent
    '''构建该 UniEvent 的原 Event 实例'''
    
    post_type: Literal["message", "notice", "request", "meta", "other"]
    '''事件类型'''

    event_id: Encoded
    '''编码后的事件 id'''
    
    time: Optional[int] = None
    '''事件发生的时间戳'''

    self_id: Optional[Union[str, int]] = None
    '''收到事件的机器人 ID'''

    extra: dict[str, Any] = {}

    @classmethod
    @property
    def support_events(cls) -> list[Type[BaseEvent]]:
        '''该 UniEvent 所支持的 Event'''
        return uni_event_support[cls]

    @staticmethod
    async def _parse_params(
        origin_event: BaseEvent,
        mapping: dict[str, Union[Item, Callable, Any]]
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        for k, v in mapping.items():
            if isinstance(v, Item):
                params[k] = getattr(origin_event, v.name, v.default)
                if v.call is not None:
                    params[k] = await v.call(params[k])
            elif isinstance(v, Callable):
                params[k] = v(origin_event)
            else:
                params[k] = v
        params["origin_event"] = origin_event
        return params

    @classmethod
    async def parse(
        cls,
        origin_event: BaseEvent,
        mapping: dict[str, Union[Item, Callable, Any]]
    ):
        '''用 Event 构建 UniEvent'''
        uni_event = parse_obj_as(
            cls,
            await cls._parse_params(origin_event, mapping)
        )
        return uni_event

    async def _export_params(
            self,
            mapping: dict[str, Union[Item, Callable, Any]]
        ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        for k, v in mapping.items():
            if isinstance(v, Item):
                params[k] = getattr(self, v.name, v.default)
                if v.call is not None:
                    params[k] = await v.call(params[k])
            elif isinstance(v, Callable):
                params[k] = v(self)
            else:
                params[k] = v
        return params
    
    async def export(
            self,
            event_cls: Type[BaseEvent],
            mapping: dict[str, Union[Item, Callable, Any]]
        ) -> BaseEvent:
        '''将 UniEvent 导出为目标 Event'''
        event = parse_obj_as(
            event_cls,
            await self._export_params(mapping)
        )
        setattr(event, "uni_event", self)
        return event


# Message Events
class UniMessageEvent(UniEvent):
    '''消息事件标记'''

    post_type: Literal["message"]

    message_type: Literal["private", "group"]
    '''消息类型，如 private 为私聊，group 为群聊'''

    message_id: Encoded
    '''编码后的消息 ID'''

    user_id: Encoded
    '''编码后的发送者 ID'''

    message: UniMessage
    '''消息内容'''
    
    to_me: bool
    '''消息是否与机器人有关'''

    raw_message: Optional[str] = None
    '''原始消息内容'''


class UniPrivateMessageEvent(UniMessageEvent):
    '''私聊消息事件标记'''

    sub_type: Literal["friend", "group", "other"]
    '''消息子类型，分别表示好友消息、临时会话、其他'''


class UniGroupMessageEvent(UniMessageEvent):
    '''群消息事件标记'''

    sub_type: Literal["normal", "anonymous", "notice"]
    '''消息子类型，分别表示正常消息、匿名消息、系统提示'''

    group_id: Encoded
    '''编码后的群聊 ID'''


# Notice Events
class UniNoticeEvent(UniEvent):
    '''通知事件标记'''

    post_type: Literal["notice"]

    notice_type: Literal[
        "group_increase",
        "group_decrease",
        "group_ban",
        "group_recall",
        "private_recall",
        "friend_add",
        "simple_interaction"
        "other"
    ]
    '''通知类型'''


class UniGroupIncreaseNoticeEvent(UniNoticeEvent):
    '''群成员增加事件标记'''

    notice_type: Literal["group_increase"]

    sub_type: Literal["approve", "invite"]
    '''事件子类型，分别表示审核入群、邀请入群'''
    
    group_id: Encoded
    '''编码后的群聊 ID'''
    
    operator_id: Optional[Encoded] = None
    '''编码后的操作者 ID'''
    
    user_id: Encoded
    '''编码后的加入者 ID'''


class UniGroupDecreaseNoticeEvent(UniNoticeEvent):
    '''群成员减少事件标记'''

    notice_type: Literal["group_decrease"]

    sub_type: Literal["leave", "kick", "kick_me"]
    '''事件子类型，分别表示主动退群、成员被踢、登录号被踢'''
    
    group_id: Encoded
    '''编码后的群聊 ID'''
    
    operator_id: Encoded
    '''编码后的操作者 ID'''
    
    user_id: Encoded
    '''编码后的离开者 ID'''


class UniGroupBanNoticeEvent(UniNoticeEvent):
    '''群禁言事件标记'''

    notice_type: Literal["group_ban"]

    sub_type: Literal["ban", "lift_ban"]
    '''事件子类型，分别表示禁言、解除禁言'''
    
    group_id: Encoded
    '''编码后的群聊 ID'''
    
    operator_id: Encoded
    '''编码后的操作者 ID'''
    
    user_id: Encoded
    '''编码后的被禁言者 ID'''
    
    duration: int
    '''被禁言时长，单位秒'''


class UniRecallNoticeEvent(UniNoticeEvent):
    '''消息撤回事件标记'''

    notice_type: Literal["group_recall", "private_recall"]

    user_id: Encoded
    '''编码后的消息发送者 ID'''
    
    message_id: Encoded
    '''编码后的被撤回的消息 ID'''


class UniGroupRecallNoticeEvent(UniNoticeEvent):
    '''群消息撤回事件标记'''

    notice_type: Literal["group_recall"]

    group_id: Encoded
    '''编码后的群聊 ID'''
    
    operator_id: Encoded
    '''编码后的操作者 ID'''


class UniPrivateRecallNoticeEvent(UniNoticeEvent):
    '''私聊消息撤回事件标记'''

    notice_type: Literal["private_recall"]


class UniFriendAddNoticeEvent(UniNoticeEvent):
    '''好友添加事件标记'''

    notice_type: Literal["friend_add"]
    
    user_id: Encoded
    '''编码后的新添加好友 ID'''


class UniSimpleInteractionNoticeEvent(UniNoticeEvent):
    '''简单交互事件标记'''

    notice_type: Literal["simple_interaction"]
    
    user_id: Encoded
    '''编码后的操作者 ID'''
    
    target_id: Encoded
    '''编码后的接收者 ID'''

    group_id: Optional[Encoded] = None
    '''编码后的群聊 ID'''


# Request Events
class UniRequestEvent(UniEvent):
    '''请求事件标记'''

    post_type: Literal["request"]

    request_type: Literal[
        "friend",
        "group",
        "other"
    ]
    '''请求类型'''


class UniFriendRequestEvent(UniRequestEvent):
    '''添加好友事件标记'''
    
    request_type: Literal["friend"]

    user_id: Encoded
    '''编码后的发送请求者 ID'''

    comment: Optional[str]
    '''验证信息'''


class UniGroupRequestEvent(UniRequestEvent):
    '''加群请求/邀请事件标记'''
    
    request_type: Literal["group"]

    sub_type: Literal["add", "invite"]
    '''事件子类型，分别表示加群请求、邀请入群请求'''

    group_id: Encoded
    '''编码后的群聊 ID'''
    
    user_id: Encoded
    '''编码后的操作者 ID'''

    comment: Optional[str]
    '''验证信息'''


# Meta Events
class UniMetaEvent(UniEvent):
    '''元事件标记'''

    post_type: Literal["meta"]

    meta_event_type: Literal["lifecycle", "heartbeat", "other"]
    '''元事件类型'''


class UniLifecycleMetaEvent(UniMetaEvent):
    '''生命周期元事件标记'''

    meta_event_type: Literal["lifecycle"]
    
    sub_type: Literal["enable", "disable", "connect"]
    '''事件子类型，分别表示启用、停用、WebSocket 连接成功'''


class UniHeartbeatMetaEvent(UniMetaEvent):
    '''心跳元事件'''

    meta_event_type: Literal["heartbeat"]

    online: bool
    '''在线状态'''
    
    interval: int
    '''到下次心跳的间隔，单位毫秒'''


uni_event_support: dict[Type[UniEvent], list[Type[BaseEvent]]] = defaultdict(list)


def add_uni_event_items(
        event_cls: Type[BaseEvent],
        uni_event_cls: Type[UniEvent],
        parse_mapping: Optional[dict[str, Union[Item, Callable, Any]]] = None,
        export_mapping: Optional[dict[str, Union[Item, Callable, Any]]] = None
) -> None:
    """
    为原 Event 类指定 UniEvent 类，并设定参数映射（parse_mapping 与 export_mapping）。

    :param event_cls: 原 Event 类
    :param uni_event_cls: 指定的 UniEvent 类
    :param parse_mapping:
        通过原 Event 类实例构造 UniEvent 实例的参数映射。
        键为目标 UniEvent 的字段名，值为 Item类（参数含义请参见对应函数文档），
        或以原 Event 实例为唯一参数的 Callable 对象，或为非 Callable 的其他对象。
    :param export_mapping:
        通过 UniEvent 实例构造该 Event 实例的参数映射。
        键为该 Event 的字段名，值为 Item类（参数含义请参见对应函数文档），
        或以指定 UniEvent 类实例为唯一参数的 Callable 对象，或为非 Callable 的其他对象。

    当 parse_mapping 与 export_mapping 均留空时，将会为原 Event 类设定空字典参数映射。

    当仅有 export_mapping 留空时，将试图从 parse_mapping 中取出 (str, str) 键值对构建 export_mapping.
    可为 export_mapping 传入空字典避免上述构建过程。
    """
    # TODO 暂不支持"仅提供 UniEvent 与 Event 之间的单向转换"，需要改写构造过程
    if parse_mapping is not None and export_mapping is None:
        temp_export_mapping = {}
        for k, v in parse_mapping.items():
            if type(k) == type(v) == str:
                temp_export_mapping[v] = k
        export_mapping = temp_export_mapping
    if parse_mapping is None and export_mapping is None:
        parse_mapping = {}
        export_mapping = {}
    setattr(event_cls, "uni_event", uni_event_cls)
    setattr(event_cls, "parse_mapping", parse_mapping)
    setattr(event_cls, "export_mapping", export_mapping)
    async def get_uni_event(self):
        return await cast(Type[UniEvent], self.uni_event).parse(self, cast(dict, self.parse_mapping))
    @classmethod
    async def parse_fake_event(cls, uni_event: UniEvent):
        return await uni_event.export(cls, cast(dict, cls.export_mapping))
    setattr(event_cls, "get_uni_event", get_uni_event)
    setattr(event_cls, "parse_fake_event", parse_fake_event)
    uni_event_support[uni_event_cls].append(event_cls)
    

def check_uni_event_support(event_or_cls: Union[BaseEvent, Type[BaseEvent]]) -> bool:
    '''检查 Event 类或实例是否支持转化为 UniEvent'''
    return hasattr(event_or_cls, "uni_event")


__all__ = [
    "Item",
    "UniEvent",
    "UniMessageEvent",
    "UniPrivateMessageEvent",
    "UniGroupMessageEvent",
    "UniNoticeEvent",
    "UniGroupIncreaseNoticeEvent",
    "UniGroupDecreaseNoticeEvent",
    "UniGroupBanNoticeEvent",
    "UniRecallNoticeEvent",
    "UniGroupRecallNoticeEvent",
    "UniPrivateRecallNoticeEvent",
    "UniFriendAddNoticeEvent",
    "UniSimpleInteractionNoticeEvent",
    "UniRequestEvent",
    "UniFriendRequestEvent",
    "UniGroupRequestEvent",
    "UniMetaEvent",
    "UniLifecycleMetaEvent",
    "UniHeartbeatMetaEvent",
    "add_uni_event_items",
    "check_uni_event_support"
]