"""Anno 1800 工具链：从解包数据到 JSON 数据库，再到文档与查询。

三条铁律（其它模块都遵守）：

    temp/   原始层：只读的 assets.xml / templates.xml / texts_*.xml + 卡表底稿
    data/   解析层：一个资产一个 JSON（见 docs/data-model.md）
    docs/   展示层：只从 data/ 渲染，不回头读 XML

用法见仓库根目录的 `build_db.py` / `build_cards.py` / `query.py`。
"""

from __future__ import annotations

__version__ = "2.0.0"
