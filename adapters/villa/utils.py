import nonebot
from nonebot.adapters.villa.adapter import Adapter
from typing import Union, Literal, Optional


adapter_name = Adapter.get_name()
'''适配器名称'''

adapter = nonebot.get_adapter(Adapter)
'''适配器实例'''

TIMEOUT = 10

def villa_room_id_convert(
        type: Literal["encode", "decode"],
        villa_id: Optional[int] = None,
        room_id: Optional[int] = None,
        combine_id: Optional[str] = None
    ) -> Union[str, tuple[int, int]]:
    if type == "encode":
        if villa_id is None or room_id is None:
            raise ValueError("encode 模式下，villa_id 与 room_id 均需要提供。")
        return f"{villa_id}+{room_id}"
    if type == "decode":
        if combine_id is None:
            raise ValueError("decode 模式下，需要提供 combine_id.")
        ids = combine_id.split("+")
        if len(ids) != 2 or not ids[0].isnumeric() or not ids[1].isnumeric():
            raise ValueError("所提供的 combine_id 格式有误。")
        return (int(ids[0]), int(ids[1]))