from pydantic import BaseModel
from typing import Union, Optional
from pathlib import Path


# TODO 后续可能支持多平台用户绑定
class PlatformUserData(BaseModel):
    '''各平台用户信息'''

    id: Union[int, str]
    '''平台用户 id'''
    name: str
    '''平台用户昵称'''

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
    platform_data: dict[str, PlatformUserData] = {}
    '''用户各平台信息'''

# TODO 后续可通过本地存储群聊、频道、房间信息满足其他需求
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