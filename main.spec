# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

# 根据命令行参数来决定是否显示控制台窗口


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
          console=True,
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
