# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

# jenkins 设置环境变量来判断是否需要显示黑窗口

import os

CONSOLE = os.environ.get('CONSOLE', 'true')

if CONSOLE == 'true':
    console_window = True
else:
    console_window = False


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[("./resources", "resources"), ("./view", "view"),
                    ("./common", "common"), ("./ui", "ui")],
             hiddenimports=["Crypto.Cipher.AES", "Crypto.Util.Padding","Crypto.Random", "logzero", "qfluentPackage",
                            "qfluentPackage.windows", "qfluentPackage.widget", "chardet", "vdf"],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='L4D2 Mod Manager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=console_window,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          windowed=True,
          contents_directory='.',
          version='verison_info.txt')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               name="L4D2 Mod Manager",
               upx=True,
               upx_exclude=[])
