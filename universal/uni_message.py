'''
提供统一的 UniMessage 与各类 UniMessageSegment 类。

每个适配器需要实现 UniMessage 与其 Message 的两种转换函数，
并将函数对应放入 GENERATE_MAPPING 与 EXPORT_MAPPING 字典中。

另外需在 Message 类中添加 adapter_name 字段。

上述操作可通过 add_message_change 函数完成，详细请参考相关函数文档。
'''

from typing import (
    cast,
    List,
    Type,
    Union,
    Optional,
    Callable,
    TypeVar,
    Literal,
    Protocol,
    Any
)
from dataclasses import dataclass
from pathlib import Path
from io import BytesIO
from PIL import Image

from nonebot.internal.adapter import Adapter, Message, MessageSegment, Bot

from ..utils import (
    path_to_url,
    path_to_bytes,
    bytes_to_path,
    bytes_to_url,
    url_to_bytes,
    url_to_path,
    Encoded
)


@dataclass
class UniMessageSegment:
    '''UniMessageSegment 基类。'''

    type: str
    
    origin_ms: MessageSegment
    '''原消息段'''

    @staticmethod
    def text(origin_ms: MessageSegment, text: str) -> "UniText":
        return UniText("text", origin_ms, text)
    
    @staticmethod
    def reply(origin_ms: MessageSegment, msg_id: Encoded) -> "UniReply":
        return UniReply("reply", origin_ms, msg_id)
    
    @staticmethod
    def at_all(origin_ms: MessageSegment, to_me: bool=True) -> "UniAtAll":
        return UniAtAll("at_all", origin_ms, to_me)
    
    @staticmethod
    def at_user(origin_ms: MessageSegment, target_user: Encoded, to_me: bool=False) -> "UniAtUser":
        return UniAtUser("at_user", origin_ms, target_user, to_me)
    
    @staticmethod
    def at_me(origin_ms: MessageSegment, to_me: bool=True) -> "UniAtMe":
        return UniAtMe("at_me", origin_ms, to_me)
    
    @staticmethod
    def image(
        origin_ms: MessageSegment,
        path: Optional[Union[str, Path]] = None,
        bytes: Optional[Union[bytes, BytesIO]] = None,
        url: Optional[str] = None,
        cache: bool = True,
        proxy: bool = True,
        timeout: Optional[int] = None
    ) -> "UniImage":
        return UniImage(
            "image",
            origin_ms,
            path,
            bytes,
            url,
            cache=cache,
            proxy=proxy,
            timeout=timeout
        )
    
    @staticmethod
    def voice(
        origin_ms: MessageSegment,
        path: Optional[Union[str, Path]] = None,
        bytes: Optional[Union[bytes, BytesIO]] = None,
        url: Optional[str] = None,
        cache: bool = True,
        proxy: bool = True,
        timeout: Optional[int] = None
    ) -> "UniVoice":
        return UniVoice(
            "voice",
            origin_ms,
            path,
            bytes,
            url,
            cache=cache,
            proxy=proxy,
            timeout=timeout
        )

    @staticmethod
    def video(
        origin_ms: MessageSegment,
        path: Optional[Union[str, Path]] = None,
        bytes: Optional[Union[bytes, BytesIO]] = None,
        url: Optional[str] = None,
        cache: bool = True,
        proxy: bool = True,
        timeout: Optional[int] = None
    ) -> "UniVideo":
        return UniVideo(
            "video",
            origin_ms,
            path,
            bytes,
            url,
            cache=cache,
            proxy=proxy,
            timeout=timeout
        )

    @staticmethod
    def other(origin_ms: MessageSegment) -> "UniOther":
        return UniOther("other", origin_ms)

@dataclass
class UniText(UniMessageSegment):
    '''文本信息'''

    text: str

    type: Literal["text"]


@dataclass
class UniReply(UniMessageSegment):
    '''回复信息'''

    msg_id: Encoded
    '''编码后的回复消息 ID'''

    type: Literal["reply"]


@dataclass
class UniAt(UniMessageSegment):
    '''at 信息'''


@dataclass
class UniAtAll(UniAt):
    '''at 全体成员信息'''

    to_me: bool = True

    type: Literal["at_all"]


@dataclass
class UniAtUser(UniAt):
    '''at 用户信息'''

    target_user: Encoded
    '''编码后的 at 目标用户 id'''

    to_me: bool = False

    type: Literal["at_user"]


@dataclass
class UniAtMe(UniAt):
    '''at 机器人信息'''

    to_me: bool = True

    type: Literal["at_me"]


@dataclass
class UniMedia(UniMessageSegment):
    '''
    媒体信息

    path、bytes、url 至少需要提供其一，且前述优先度递减。

    如获取 url 时，若 url 为空，则先后检查 path、bytes，并尝试构造 url。
    '''

    _path: Optional[Union[str, Path]] = None
    '''媒体文件路径'''
    _bytes: Optional[Union[bytes, BytesIO]] = None
    '''媒体内容'''
    _url: Optional[str] = None
    '''媒体网络链接地址'''
    cache: bool = True
    proxy: bool = True
    timeout: Optional[int] = None

    @property
    def path(self) -> str:
        if self._path is not None:
            if isinstance(self._path, Path):
                return str(self._path.absolute())
            return self._path
        if self._bytes is not None:
            return str(bytes_to_path(self._bytes))
        if self._url is not None:
            return str(url_to_path(
                self._url,
                cache=self.cache,
                proxy=self.proxy,
                timeout=self.timeout
            ))
        raise ValueError("UniMedia 参数不足，无法获取 path。")

    @property
    def bytes(self) -> bytes:
        if self._bytes is not None:
            if isinstance(self._bytes, BytesIO):
                return self._bytes.getvalue()
            return self._bytes
        if self._path is not None:
            return path_to_bytes(self._path)
        if self._url is not None:
            return url_to_bytes(
                self._url,
                cache=self.cache,
                proxy=self.proxy,
                timeout=self.timeout
            )
        raise ValueError("UniMedia 参数不足，无法获取 bytes。")

    @property
    def url(self) -> str:
        if self._url is not None:
            return self._url
        if self._path is not None:
            return path_to_url(self._path)
        if self._bytes is not None:
            return bytes_to_url(self._bytes)
        raise ValueError("UniMedia 参数不足，无法获取 url。")
    
    def __post_init__(self):
        self.check_content()

    def check_content(self):
        if not (self._path or self._bytes or self._url):
            raise ValueError("构造 UniMedia 时参数不足。")


@dataclass
class UniImage(UniMedia):
    '''图像信息'''

    type: Literal["image"]

    @property
    def size(self) -> tuple[int, int]:
        pic = Image.open(BytesIO(self.bytes))
        return pic.size

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]


@dataclass
class UniVoice(UniMedia):
    '''音频信息'''

    type: Literal["voice"]


@dataclass
class UniVideo(UniMedia):
    '''视频信息'''

    type: Literal["video"]


@dataclass
class UniOther(UniMessageSegment):
    '''其他信息类型'''

    type: Literal["other"]


uni_ms_mapping: dict[str, Type[UniMessageSegment]] = {
    "text": UniText,
    "reply": UniReply,
    "at_all": UniAtAll,
    "at_user": UniAtUser,
    "at_me": UniAtMe,
    "image": UniImage,
    "voice": UniVoice,
    "video": UniVideo,
    "other": UniOther
}


class UniMessage(List[UniMessageSegment]):

    origin_message: Message
    '''原 Message'''

    def __init__(self, origin_message: Message):
        self.origin_message = origin_message

    @staticmethod
    def generate(
        adapter: Union[str, Adapter, Type[Adapter]],
        origin_message: Union[Message, MessageSegment],
        bot: Optional[Bot] = None,
        encode: bool = True,
        **kwargs
    ):
        """
        通过原 Message 与 Bot 构造 UniMessage 对象。

        :param adapter: 原 Message 所对应的 adapter 类或实例，或对应名称字符串。
        :param origin_message: 原 Message 或 MessageSegment 实例。
        :param bot: 原 Message 或 MessageSegment 所对应 Bot 实例，部分转换函数可能要求该参数。
        :param encode: 是否要对原 Message 中的 id 进行编码。
        :return: 构造完成的 UniMessage 对象。
        """
        if isinstance(adapter, str):
            adapter_name = adapter
        else:
            adapter_name = adapter.get_name()
        if not (generate_func := GENERATE_MAPPING.get(adapter_name)):
            raise ValueError(f"适配器 {adapter_name} 未设定 UniMessage 生成方法。")
        if isinstance(origin_message, MessageSegment):
            origin_message = cast(Type[Message], origin_message.get_message_class())(origin_message)
        return generate_func(ori_msg=origin_message, bot=bot, encode=encode, **kwargs)

    def export(
            self,
            adapter: Union[str, Adapter, Type[Adapter]],
            bot: Optional[Bot] = None,
            decode: bool = True,
            **kwargs
        ) -> Message:
        """
        通过目标 Bot 实例构造 UniMessage 对象。

        :param adapter: 目标 Message 所对应的 adapter 类或实例，或对应名称字符串。
        :param bot: 目标 Message 所对应 Bot 实例，部分转换函数可能要求该参数。
        :param decode: 是否要对 UniMessage 中的 id 进行解码。
        :return: 构造完成的目标 Message 对象。
        """
        if isinstance(adapter, str):
            adapter_name = adapter
        else:
            adapter_name = adapter.get_name()
        if not (export_func := EXPORT_MAPPING.get(adapter_name)):
            raise ValueError(f"适配器 {adapter_name} 未设定 UniMessage 导出方法。")
        return export_func(uni_msg=self, bot=bot, decode=decode, **kwargs)


TM1 = TypeVar("TM1", bound=Message, contravariant=True)
TM2 = TypeVar("TM2", bound=Message, covariant=True)
TB = TypeVar("TB", bound=Bot, contravariant=True)

class Generater(Protocol[TM1, TB]):
    def __call__(
            self,
            ori_msg: TM1,
            bot: Optional[TB] = None,
            encode: bool = True,
            **kwargs
        ) -> UniMessage: ...

class Exporter(Protocol[TM2, TB]):
    def __call__(
            self,
            uni_msg: UniMessage,
            bot: Optional[TB] = None,
            decode: bool = True,
            **kwargs
        ) -> TM2: ...


GENERATE_MAPPING: dict[str, Generater] = {}
'''存放各适配器对应 Message 转换 UniMessage 的方法'''

EXPORT_MAPPING: dict[str, Exporter] = {}
'''存放各适配器对应 UniMessage 导出 Message 的方法'''

def add_message_change(
        adapter: Union[str, Adapter, Type[Adapter]],
        generate_func: Generater,
        export_func: Exporter,
        message_cls: Type[Message]
    ):
    """
    为 Message 类添加对应适配器名称，并将转换函数放入对应字典中。

    :param adapter: 对应的 adapter 类或实例，或对应名称字符串。
    :param generate_func: 对应 Message 转换 UniMessage 的函数。
    :param export_func: 对应 UniMessage 导出 Message 的函数。
    :param message_cls: 对应适配器的 Message 类。
    """
    if isinstance(adapter, str):
        adapter_name = adapter
    else:
        adapter_name = adapter.get_name()
    setattr(message_cls, "adapter_name", adapter_name)
    GENERATE_MAPPING[adapter_name] = generate_func
    EXPORT_MAPPING[adapter_name] = export_func

def convert_message(
        message: Union[Message, MessageSegment, UniMessage],
        origin_adapter: Optional[Union[str, Adapter, Type[Adapter]]] = None,
        target_adapter: Optional[Union[str, Adapter, Type[Adapter]]] = None,
        origin_bot: Optional[Bot] = None,
        target_bot: Optional[Bot] = None,
        from_origin_encode: bool = True,
        to_target_decode: bool = True,
        from_origin_kwargs: dict[str, Any] = {},
        to_target_kwargs: dict[str, Any] = {}
    ) -> Union[Message, UniMessage]:
    """
    将给定消息转化为目标形式。

    :param message: 需要转化的消息。
    :param origin_adapter: 原消息适配器类、实例或名称。留空则代表从 UniMessage 导出。
    :param target_adapter: 目标消息适配器类、实例或名称。留空则代表构造为 UniMessage.
    :param origin_bot: 原消息所对应 Bot 实例，部分转换函数可能要求该参数。也可将参数放在 from_origin_kwargs 中。
    :param target_bot: 目标消息所对应 Bot 实例，部分转换函数可能要求该参数。也可将参数放在 to_target_kwargs 中。
    :param from_origin_encode: 将原消息转化为 UniMessage 时是否要对其中的 id 进行编码。也可将参数放在 from_origin_kwargs 中。
    :param to_target_decode: 将 UniMessage 导出为目标消息时是否要对其中的 id 进行解码。也可将参数放在 to_target_kwargs 中。
    :param from_origin_kwargs: 将原消息转化为 UniMessage 时传入对应转换函数的额外参数。
    :param to_target_kwargs: 将 UniMessage 导出为目标消息时传入对应转换函数的额外参数。

    origin_adapter 与 target_adapter 需要至少有一个不为 None.
    """
    if origin_adapter is None and target_adapter is None:
        raise ValueError("origin_adapter 与 target_adapter 需要至少有一个不为 None。")
    
    if origin_adapter is not None:
        if isinstance(origin_adapter, str):
            origin_adapter_name = origin_adapter
        else:
            origin_adapter_name = origin_adapter.get_name()
    else:
        origin_adapter_name = None
    if target_adapter is not None:
        if isinstance(target_adapter, str):
            target_adapter_name = target_adapter
        else:
            target_adapter_name = target_adapter.get_name()
    else:
        target_adapter_name = None
    
    if origin_adapter_name is not None and origin_adapter_name not in GENERATE_MAPPING.keys():
        raise ValueError(f"指定适配器 {origin_adapter_name} 不支持转化为 UniMessage.")
    if target_adapter_name is not None and target_adapter_name not in EXPORT_MAPPING.keys():
        raise ValueError(f"指定适配器 {target_adapter_name} 不支持从 UniMessage 导出。")
    
    if origin_adapter_name is not None and target_adapter_name is None:
        if isinstance(message, Message) or isinstance(message, MessageSegment):
            return UniMessage.generate(
                adapter=origin_adapter_name,
                origin_message=message,
                bot=origin_bot,
                encode=from_origin_encode,
                **from_origin_kwargs
            )
        else:
            raise ValueError("由于需要转化为 UniMessage，参数 massage 应该为 Message 或 MessageSegment 对象。")
    
    if origin_adapter_name is None and target_adapter_name is not None:
        if isinstance(message, UniMessage):
            return message.export(
                adapter=target_adapter_name,
                bot=target_bot,
                decode=to_target_decode,
                **to_target_kwargs
            )
        else:
            raise ValueError("由于需要导出为 Message，参数 massage 应该为 UniMessage 类对象。")

    if (isinstance(message, Message) or isinstance(message, MessageSegment)):
        return UniMessage.generate(
            adapter=cast(str, origin_adapter_name),
            origin_message=message,
            bot=origin_bot,
            encode=from_origin_encode,
            **from_origin_kwargs
        ).export(
            adapter=cast(str, target_adapter_name),
            bot=target_bot,
            decode=to_target_decode,
            **to_target_kwargs
        )
    else:
        raise ValueError("由于需要转换 Message，参数 message 应该为 Message 或 MessageSegment 对象。")


__all__ = [
    "UniMessageSegment",
    "UniText",
    "UniReply",
    "UniAtAll",
    "UniAtUser",
    "UniAtMe",
    "UniMedia",
    "UniImage",
    "UniVoice",
    "UniVideo",
    "UniOther",
    "uni_ms_mapping",
    "UniMessage",
    "GENERATE_MAPPING",
    "EXPORT_MAPPING",
    "add_message_change",
    "convert_message"
]