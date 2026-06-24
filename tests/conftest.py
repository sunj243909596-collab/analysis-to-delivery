"""pytest 配置：把 scripts/ 加入 sys.path 以便 import task_confirm_check"""

import sys
from pathlib import Path

# 添加 scripts/ 到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))