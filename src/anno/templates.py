"""`templates.xml`：模板的默认装槽。

「这张卡能装到哪儿」的权威答案 = 卡牌自己的 `<Item><Allocation>`，没写就继承这里。
踩过的坑：早先看到卡没写装槽就归成「多用途专家」，其实那 800 多张专家各有归属。
"""

from __future__ import annotations

from lxml import etree

from . import paths

NONE = "none"


def default_slots() -> dict[str, str]:
    """`{模板名: 默认装槽内部值}`；模板没写装槽的记空串。"""
    slots: dict[str, str] = {}
    root = etree.parse(str(paths.TEMPLATES)).getroot()
    for template in root.iter("Template"):
        name = (template.findtext("Name") or "").strip()
        if not name:
            continue
        slot = (template.findtext("Properties/Item/Allocation") or "").strip()
        slots[name] = "" if slot.lower() == NONE else slot
    return slots
