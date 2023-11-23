from pydantic import BaseModel
from typing import Union, Optional
from pathlib import Path



class User(BaseModel):
    '''用户信息模型'''

    id: str
    '''内置用户 id'''
    name: str
    '''用户名称'''
    avatar: Union[str, Path]
    '''用户头像'''
    level: int
    '''用户等级'''

    qq_id: Optional[str] = None
    villa_id: Optional[str] = None

class Group(BaseModel):
    '''群聊信息模型'''

    id: str
    name: str
    platform: str
    is_available: bool

class Channel(BaseModel):
    '''频道信息模型'''

    id: str
    name: str
    platform: str
    default_room_id: str
    '''默认消息房间'''
    welcome_room_id: str
    '''欢迎消息房间'''

class Room(BaseModel):
    '''房间信息模型'''

    id: str
    name: str
    platform: str
    is_available: bool