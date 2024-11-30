# -*- coding: utf-8 -*-
# @Time: 2024/11/13
# @Author: Administrator
# @File: test1.py
from pathlib import Path
import json
from common.read_vpk import open_vpk
import re

l4d2 = Path(r'E:/SteamLibrary/steamapps/common/Left 4 Dead 2/left4dead2')
path_list = [
    Path(r'F:/求生之路2/禁用mod'),
    l4d2 / 'addons',
    l4d2 / 'addons' / 'workshop'
]
save_data = {}

out_folder = Path(r'F:\_SystemFiles\Desktop\tmp')
out_file = out_folder / 'result.json'
for path in path_list:
    for file in path.glob('*.vpk'):
        vpk = open_vpk(file)
        if not vpk:
            continue
        key = file.stem
        if key in save_data:
            print('文件重复', file)
        save_data.setdefault(key, [])
        for vpk_file_path in vpk:
            save_data[key].append(vpk_file_path)
with open(out_file, 'w', encoding='utf8') as f:
    json.dump(save_data, f, ensure_ascii=False, indent=4)
