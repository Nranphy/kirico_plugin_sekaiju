from nonebot.internal.adapter import (
    Message as BaseMessage,
    MessageSegment as BaseMessageSegment,
)


class MessageSegment(BaseMessageSegment["Message"]):
    pass

class Message(BaseMessage[MessageSegment]):
    pass