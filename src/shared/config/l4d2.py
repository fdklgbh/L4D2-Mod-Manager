# -*- coding: utf-8 -*-
# @Time: 2025/12/19
# @Author: Administrator
# @File: l4d2cfg.py
import os
import platform
import shutil
import tempfile
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from qfluentwidgets_pro import ConfigItem
import vdf

from .settings import setting_cfg


class L4d2Config:
    @property
    def l4d2_path(self):
        return self._path(setting_cfg.l4d2_Path)

    @l4d2_path.setter
    def l4d2_path(self, value):
        setting_cfg.set(setting_cfg.l4d2_Path, value)

    @property
    def disable_mod_path(self):
        return self._path(setting_cfg.disable_mod_path)

    @disable_mod_path.setter
    def disable_mod_path(self, value):
        Path(value).mkdir(exist_ok=True)
        setting_cfg.set(setting_cfg.disable_mod_path, value)

    @property
    def l4d2_vpk_path(self):
        name = "vpk.exe" if self.is_win else "vpk"
        return Path(self.l4d2_path) / "bin" / name

    @property
    def vpk_application_is_exists(self):
        return self.l4d2_vpk_path.exists()

    @property
    def auto_update(self):
        return setting_cfg.auto_update.value

    @property
    def auto_update_item(self) -> ConfigItem:
        return setting_cfg.auto_update

    @auto_update.setter
    def auto_update(self, value):
        setting_cfg.set(setting_cfg.auto_update, value)

    @property
    def gcfspace_path(self):
        return self._path(setting_cfg.gcfspace_path)

    @gcfspace_path.setter
    def gcfspace_path(self, value):
        setting_cfg.set(setting_cfg.gcfspace_path, value)

    @property
    def addons_path(self):
        return (self.l4d2_path / "left4dead2" / "addons").resolve()

    @property
    def workshop_path(self):
        return (self.addons_path / "workshop").resolve()

    def is_addons(self, path):
        return self.addons_path == Path(path).resolve()

    def is_workshop(self, path):
        return self.workshop_path == Path(path).resolve()

    def is_disable_mod_path(self, path):
        return self.disable_mod_path == Path(path).resolve()

    @staticmethod
    def _path(item):
        if value := setting_cfg.get(item):
            return Path(value).resolve()
        return ""

    @property
    def addonlist_file(self) -> Path | None:
        if not (game_path := self.l4d2_path):
            return None
        return Path(game_path) / "left4dead2" / "addonlist.txt"

    def _validated_addonlist_file(self) -> Path:
        """在应用路径边界校验后返回配置的 addonlist 路径。"""
        if not (game_path := self.l4d2_path):
            raise RuntimeError("L4D2游戏目录未配置")

        game_root = Path(game_path).expanduser().resolve()
        addonlist_file = self.addonlist_file
        if addonlist_file is None:
            raise RuntimeError("L4D2游戏目录未配置")
        addonlist_file = Path(addonlist_file).expanduser().resolve()
        expected_file = (game_root / "left4dead2" / "addonlist.txt").resolve()
        try:
            addonlist_file.relative_to(game_root)
        except ValueError as error:
            raise ValueError("addonlist.txt 必须位于 L4D2 游戏目录内") from error
        if addonlist_file != expected_file:
            raise ValueError("addonlist.txt 路径不符合 L4D2 目录结构")
        if not expected_file.parent.is_dir():
            raise FileNotFoundError(f"L4D2 目录不存在: {expected_file.parent}")
        return expected_file

    def read_addonlist(self, used: bool | None = None) -> dict[str, str] | list[str]:
        """读取 VDF AddonList，接受 UTF-8 和 GBK 编码的文件。"""
        addonlist_file = self._validated_addonlist_file()
        if not addonlist_file.exists():
            return {} if used is None else []
        if not addonlist_file.is_file():
            raise IsADirectoryError(f"addonlist.txt 不是文件: {addonlist_file}")

        raw_data = addonlist_file.read_bytes()
        parsed: dict[str, Any] | None = None
        last_error: Exception | None = None
        for encoding in ("utf-8-sig", "gbk"):
            try:
                parsed = vdf.loads(raw_data.decode(encoding))
            except (UnicodeDecodeError, SyntaxError, ValueError) as error:
                last_error = error
                continue
            break
        if parsed is None:
            raise ValueError(
                f"无法解析 addonlist.txt: {addonlist_file}"
            ) from last_error

        addonlist = next(
            (value for key, value in parsed.items() if key.lower() == "addonlist"),
            None,
        )
        if not isinstance(addonlist, Mapping):
            raise ValueError("addonlist.txt 缺少 AddonList 结构")

        data = {str(key): str(value) for key, value in addonlist.items()}
        if used is None:
            return data
        return [
            key
            for key, value in data.items()
            if key.lower().endswith(".vpk") and (used is False or value == "1")
        ]

    def backup_addonlist(self) -> Path | None:
        """为当前 addonlist 创建可恢复的同目录备份。"""
        addonlist_file = self._validated_addonlist_file()
        if not addonlist_file.exists():
            return None
        if not addonlist_file.is_file():
            raise IsADirectoryError(f"addonlist.txt 不是文件: {addonlist_file}")

        backup_file = addonlist_file.with_name(f"{addonlist_file.name}.bak")
        shutil.copy2(addonlist_file, backup_file)
        return backup_file

    def write_addonlist(self, data: Mapping[str, Any]) -> None:
        """通过同目录临时文件替换写入 AddonList。"""
        if not isinstance(data, Mapping):
            raise TypeError("addonlist 数据必须是映射")
        addonlist_data = data.get("AddonList", data)
        if not isinstance(addonlist_data, Mapping):
            raise TypeError("AddonList 数据必须是映射")

        addonlist_file = self._validated_addonlist_file()
        serialized = vdf.dumps(
            {
                "AddonList": {
                    str(key): str(value) for key, value in addonlist_data.items()
                }
            }
        )
        self.backup_addonlist()

        temporary_file: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{addonlist_file.name}.",
                suffix=".tmp",
                dir=addonlist_file.parent,
            )
            os.close(descriptor)
            temporary_file = Path(temporary_name)
            with temporary_file.open("w", encoding="gbk", newline="\n") as file:
                file.write(serialized)
                file.flush()
                os.fsync(file.fileno())
            temporary_file.replace(addonlist_file)
        finally:
            if temporary_file is not None and temporary_file.exists():
                temporary_file.unlink()

    @property
    @lru_cache()
    def is_win(self):
        return platform.system() == "Windows"


l4d2Config = L4d2Config()

__all__ = ["l4d2Config"]
