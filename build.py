# -*- coding: utf-8 -*-
# @Time: 2025/4/14
# @Author: Administrator
# @File: build.py
import shutil
import subprocess
import os
import sys
from pathlib import Path
import py7zr
import time

def compress_with_py7zr(source_path, output_7z):
    """使用 py7zr 库压缩文件/目录"""
    try:
        # 创建 7z 压缩包
        with py7zr.SevenZipFile(output_7z, 'w') as archive:
            archive.writeall(source_path, os.path.basename(source_path))
        print(f"成功生成压缩包：{output_7z}")

    except Exception as e:
        print(f"压缩失败：{str(e)}")
        sys.exit(1)


def run_nuitka_build():
    start = time.time()
    # 定义动态参数
    output_dir = Path(os.environ.get('output_dir', './output'))
    icon = Path(__file__).parent / 'resources' / 'icon' / 'l4d2_256x256.ico'
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)
    output_filename = "L4D2 Mod Manager"
    main_script = "main.py"
    VERSION = '0.1.2.2'

    # 检查主脚本是否存在
    if not os.path.exists(main_script):
        print(f"错误：未找到入口文件 {main_script}")
        sys.exit(1)
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    # 定义 Nuitka 命令
    command = [
        "nuitka",
        "--standalone",
        "--windows-disable-console",
        # "--msvc=latest",
        '--mingw64',
        "--show-memory",
        "--jobs=16",
        "--show-progress",
        # '--recurse-all',
        "--enable-plugin=pyqt5",
        '--follow-imports',
        "--include-module=qfluentwidgets",
        "--include-module=qfluentwidgets.components",
        "--include-module=qfluentwidgets.components.dialog_box",
        "--include-module=qfluentwidgets.components.dialog_box.mask_dialog_base",
        f"--output-filename={output_filename}",
        f"--output-dir={output_dir}",
        '--file-description=求生之路mod管理器',
        f'--file-version={VERSION}',
        f'--product-version={VERSION}',
        '--company-name=fdklgbh',
        '--assume-yes-for-downloads',
        f'--windows-icon-from-ico={icon}',
        main_script
    ]

    try:
        print("开始编译...")
        subprocess.check_call(command, shell=True, env=os.environ.copy())
        print(f"\n编译成功！可执行文件路径：{os.path.join(output_dir, output_filename)}")
    except subprocess.CalledProcessError as e:
        print(f"\n编译失败，错误代码：{e.returncode}")
        sys.exit(str(e))
    except FileNotFoundError:
        print("\n未找到 Nuitka，请先安装：pip install nuitka")
        sys.exit(1)

    print('打包完成,耗时:', time.time() - start, "秒")
    output_folder = Path(output_dir).absolute() / main_script.replace('.py', '.dist')
    if not output_folder.exists():
        sys.exit('输出路径不存在')
    output_folder.replace(output_folder.parent / 'L4D2 Mod Manager')
    output_folder = output_folder.parent / 'L4D2 Mod Manager'
    assert output_folder.exists(), '输出路径不存在'
    output_7z = output_folder.parent / 'L4D2 Mod Manager.7z'
    compress_with_py7zr(output_folder, output_7z)


if __name__ == "__main__":
    run_nuitka_build()
