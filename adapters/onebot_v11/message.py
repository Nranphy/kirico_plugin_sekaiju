from nonebot.adapters.onebot.v11 import (
    Adapter as OneBotv11Adapter,
    Message as OneBotv11Message,
    MessageSegment as OneBotv11MessageSegment
)

from base64 import b64decode
from pathlib import Path
from typing import cast

from ...universal.uni_message import *
from .utils import s2b, s2f

def generate_func(ori_msg: OneBotv11Message) -> UniMessage:
    '''通过 ExampleMessage 类构造 UniMessage'''
    res = UniMessage(ori_msg)
    for ms in ori_msg:
        if ms.type == "text":
            res.append(UniMessageSegment.text(ms, ms.data["text"]))
        elif ms.type == "reply":
            res.append(UniMessageSegment.reply(ms, ms.data["id"]))
        elif ms.type == "at":
            res.append(UniMessageSegment.at(ms, ms.data["qq"]))
        elif ms.type == "image":
            res.append(UniMessageSegment.image(
                ms,
                **s2f(ms.data["file"]),
                cache=s2b(ms.data["cache"]),
                proxy=s2b(ms.data["proxy"]),
                timeout=ms.data["timeout"]
            ))
        elif ms.type == "record":
            res.append(UniMessageSegment.voice(
                ms,
                **s2f(ms.data["file"]),
                cache=s2b(ms.data["cache"]),
                proxy=s2b(ms.data["proxy"]),
                timeout=ms.data["timeout"]
            ))
        elif ms.type == "video":
            res.append(UniMessageSegment.video(
                ms,
                **s2f(ms.data["file"]),
                cache=s2b(ms.data["cache"]),
                proxy=s2b(ms.data["proxy"]),
                timeout=ms.data["timeout"]
            ))
        else:
            res.append(UniMessageSegment.other(ms))
    return res


def export_func(uni_msg: UniMessage) -> OneBotv11Message:
    '''通过 UniMessage 构造 ExampleMessage'''
    res = OneBotv11Message()
    for uni_ms in uni_msg:
        if isinstance(uni_ms, UniText):
            res.append(OneBotv11MessageSegment.text(uni_ms.text))
        elif isinstance(uni_ms, UniReply):
            res.append(OneBotv11MessageSegment.reply(cast(int, uni_ms.msg_id)))
        elif isinstance(uni_ms, UniAt):
            res.append(OneBotv11MessageSegment.at(uni_ms.target_user))
        elif isinstance(uni_ms, UniImage):
            res.append(OneBotv11MessageSegment.image(
                uni_ms.path,
                cache=uni_ms.cache,
                proxy=uni_ms.proxy,
                timeout=uni_ms.timeout
            ))
        elif isinstance(uni_ms, UniVoice):
            res.append(OneBotv11MessageSegment.record(
                uni_ms.path,
                cache=uni_ms.cache,
                proxy=uni_ms.proxy,
                timeout=uni_ms.timeout
            ))
        elif isinstance(uni_ms, UniVideo):
            res.append(OneBotv11MessageSegment.video(
                uni_ms.path,
                cache=uni_ms.cache,
                proxy=uni_ms.proxy,
                timeout=uni_ms.timeout
            ))
        else:
            continue
    return res
        


add_message_change(
    OneBotv11Adapter,
    generate_func,
    export_func,
    OneBotv11Message
)