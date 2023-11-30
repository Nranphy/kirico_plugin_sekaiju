from nonebot.adapters.onebot.v11 import (
    Adapter as OneBotv11Adapter,
    Bot as OneBotv11Bot,
    Message as OneBotv11Message,
    MessageSegment as OneBotv11MessageSegment
)

from typing import cast, Optional

from ...universal.uni_message import *
from ...utils import ascii_encode, ascii_decode
from .utils import s2b, s2f

async def generate_func(
        ori_msg: OneBotv11Message,
        bot: Optional[OneBotv11Bot] = None,
        encode: bool = True,
        **kwargs
    ) -> UniMessage:
    '''通过 ExampleMessage 类构造 UniMessage'''
    res = UniMessage(ori_msg)
    for ms in ori_msg:
        if ms.type == "text":
            res.append(UniMessageSegment.text(ms, ms.data["text"]))
        elif ms.type == "reply":
            if encode:
                res.append(UniMessageSegment.reply(ms, ascii_encode(ms.data["id"])))
            else:
                res.append(UniMessageSegment.reply(ms, ms.data["id"]))
        elif ms.type == "at":
            if ms.data["qq"] == "all":
                res.append(UniMessageSegment.at_all(ms))
            else:
                if bot is not None and str(bot.self_id) == str(ms.data["qq"]):
                    res.append(UniMessageSegment.at_me(ms))
                else:
                    if encode:
                        res.append(UniMessageSegment.at_user(ms, ascii_encode(ms.data["qq"])))
                    else:
                        res.append(UniMessageSegment.at_user(ms, ms.data["qq"]))
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


async def export_func(
            uni_msg: UniMessage,
            bot: Optional[OneBotv11Bot] = None,
            decode: bool = True,
            **kwargs
        ) -> OneBotv11Message:
    '''通过 UniMessage 构造 ExampleMessage'''
    res = OneBotv11Message()
    for uni_ms in uni_msg:
        if isinstance(uni_ms, UniText):
            res.append(OneBotv11MessageSegment.text(uni_ms.text))
        elif isinstance(uni_ms, UniReply):
            if decode:
                res.append(OneBotv11MessageSegment.reply(int(ascii_decode(cast(int, uni_ms.msg_id)))))
            else:
                res.append(OneBotv11MessageSegment.reply(cast(int, uni_ms.msg_id)))
        elif isinstance(uni_ms, UniAtAll):
            res.append(OneBotv11MessageSegment.at("all"))
        elif isinstance(uni_ms, UniAtMe):
            if bot is not None:
                res.append(OneBotv11MessageSegment.at(bot.self_id))
            else:
                ...
        elif isinstance(uni_ms, UniAtUser):
            if decode:
                res.append(OneBotv11MessageSegment.at(ascii_decode(uni_ms.target_user)))
            else:
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