from nonebot.adapters.villa import Adapter as VillaAdapter
from nonebot.adapters.villa import Bot as VillaBot
from nonebot.adapters.villa import (
    Message as VillaMessage,
    MessageSegment as VillaMessageSegment
)

from typing import cast, Optional

from ...universal.uni_message import *
from ...utils import ascii_encode, ascii_decode

from .utils import TIMEOUT


async def generate_func(
        ori_msg: VillaMessage,
        bot: Optional[VillaBot] = None,
        encode: bool = True,
        **kwargs
    ) -> UniMessage:
    '''通过 VillaMessage 类构造 UniMessage'''
    res = UniMessage(ori_msg)
    for ms in ori_msg:
        if ms.type == "text":
            res.append(UniMessageSegment.text(ms, ms.data["text"]))
        elif ms.type == "mention_robot":
            res.append(UniMessageSegment.at_me(ms))
        elif ms.type == "mention_user":
            if encode:
                res.append(UniMessageSegment.at_user(ms, ascii_encode(ms.data["mention_user"].user_id)))
            else:
                res.append(UniMessageSegment.at_user(ms, ms.data["mention_user"].user_id))
        elif ms.type == "mention_all":
            res.append(UniMessageSegment.at_all(ms))
        elif ms.type == "quote":
            if encode:
                res.append(UniMessageSegment.reply(ms, ascii_encode(ms.data["quote"].quoted_message_id)))
            else:
                res.append(UniMessageSegment.reply(ms, ms.data["quote"].quoted_message_id))
        elif ms.type == "image":
            res.append(UniMessageSegment.image(
                ms,
                url=ms.data["image"].url
            ))
        else:
            res.append(UniMessageSegment.other(ms))
    return res

async def export_func(
        uni_msg: UniMessage,
        bot: Optional[VillaBot] = None,
        decode: bool = True,
        **kwargs
    ) -> VillaMessage:
    '''通过 UniMessage 构造 VillaMessage'''
    if bot is None:
        raise ValueError("将 UniMessage 转出为大别野 Message 时，必须要有 Bot 参数。")
    res = VillaMessage()
    for uni_ms in uni_msg:
        if isinstance(uni_ms, UniText):
            res.append(VillaMessageSegment.text(uni_ms.text))
        elif isinstance(uni_ms, UniReply):
            if decode:
                res.append(VillaMessageSegment.quote(ascii_decode(uni_ms.msg_id), 0))
            else:
                res.append(VillaMessageSegment.quote(uni_ms.msg_id, 0))
        elif isinstance(uni_ms, UniAtAll):
            res.append(VillaMessageSegment.mention_all())
        elif isinstance(uni_ms, UniAtUser):
            temp_kwargs = {}
            if (villa_id := kwargs.get("villa_id")) is None:
                temp_kwargs["villa_id"] = villa_id
            if (user_name := kwargs.get("user_name")) is None:
                temp_kwargs["user_name"] = user_name
            elif villa_id is None:
                temp_kwargs["user_name"] = "用户"
            if decode:
                res.append(VillaMessageSegment.mention_user(
                    cast(int, ascii_decode(uni_ms.target_user)),
                    **temp_kwargs
                ))
            else:
                res.append(VillaMessageSegment.mention_user(
                    cast(int, uni_ms.target_user),
                    **temp_kwargs
                ))
        elif isinstance(uni_ms, UniAtMe):
            res.append(VillaMessageSegment.mention_robot(bot_id=bot.self_id, bot_name=bot.nickname))
        elif isinstance(uni_ms, UniImage):
            res.append(VillaMessageSegment.image(
                url = (await bot.upload_image(uni_ms.bytes)).url,
                width = uni_ms.width,
                height= uni_ms.height
            ))
        else:
            continue
    return res


add_message_change(
    VillaAdapter,
    generate_func,
    export_func,
    VillaMessage
)