from nonebot.adapters.villa import Adapter as VillaAdapter
from nonebot.adapters.villa import (
    Message as VillaMessage,
    MessageSegment as VillaMessageSegment
)

from typing import cast

from ...universal.uni_message import *


def generate_func(ori_msg: VillaMessage) -> UniMessage:
    '''通过 VillaMessage 类构造 UniMessage'''
    res = UniMessage(ori_msg)
    for ms in ori_msg:
        if ms.type == "text":
            res.append(UniMessageSegment.text(ms, ms.data["text"]))
        # TODO 需要考虑不同类型的 at，并考虑实现用户信息模型和机器人信息模型
        elif ms.type == "mention_robot":
            res.append(UniMessageSegment.at(ms, ms.data["mention_robot"].user_id, True))
        elif ms.type == "mention_user":
            res.append(UniMessageSegment.at(ms, ms.data["mention_user"].user_id))
        elif ms.type == "mention_all":
            res.append(UniMessageSegment.at(ms, "all", to_me=True))
        elif ms.type == "quote":
            res.append(UniMessageSegment.reply(ms, ms.data["quote"].quoted_message_id))
        elif ms.type == "image":
            res.append(UniMessageSegment.image(
                ms,
                url=ms.data["image"].url
            ))
        else:
            res.append(UniMessageSegment.other(ms))
    return res

def export_func(uni_msg: UniMessage) -> VillaMessage:
    '''通过 UniMessage 构造 VillaMessage'''
    res = VillaMessage()
    for uni_ms in uni_msg:
        if isinstance(uni_ms, UniText):
            res.append(VillaMessageSegment.text(uni_ms.text))
        elif isinstance(uni_ms, UniReply):
            res.append(VillaMessageSegment.quote(uni_ms.msg_id, 0))
        elif isinstance(uni_ms, UniAt):
            res.append(VillaMessageSegment.mention_user(cast(int, uni_ms.target_user)))
        # TODO Message 转换方法需要 Bot 实例
        elif isinstance(uni_ms, UniImage):
            res.append(VillaMessageSegment.image(
                url = uni_ms.url,
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