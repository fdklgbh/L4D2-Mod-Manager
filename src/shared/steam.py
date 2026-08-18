# -*- coding: utf-8 -*-
"""Steam 安装发现辅助工具。"""

import platform
from pathlib import Path
from typing import Iterable

import vdf

L4D2_APP_ID = "550"


def find_l4d2_path(steam_roots: Iterable[Path] | None = None) -> Path | None:
    """从 Steam 库元数据中查找已安装的 L4D2 目录。"""
    roots = find_steam_roots() if steam_roots is None else steam_roots

    for steam_root in roots:
        for library_root in _library_roots(Path(steam_root)):
            manifest = library_root / "steamapps" / f"appmanifest_{L4D2_APP_ID}.acf"
            app_state = _load_vdf(manifest).get("AppState", {})
            if not isinstance(app_state, dict):
                continue

            install_dir = app_state.get("installdir")
            if not install_dir:
                continue

            game_path = library_root / "steamapps" / "common" / str(install_dir)
            if _is_l4d2_path(game_path):
                return game_path.resolve()

    return None


def find_steam_roots(system: str | None = None, home: Path | None = None) -> list[Path]:
    """返回当前操作系统可能使用的 Steam 根目录。"""
    system = platform.system() if system is None else system
    home = Path.home() if home is None else home

    if system == "Windows":
        candidates = _windows_steam_roots()
    elif system == "Linux":
        candidates = [
            home / ".steam" / "steam",
            home / ".steam" / "root",
            home / ".local" / "share" / "Steam",
            home / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",
        ]
    elif system == "Darwin":
        candidates = [
            home / "Library" / "Application Support" / "Steam",
        ]
    else:
        candidates = []

    return [path for path in _unique_paths(candidates) if path.is_dir()]


def _library_roots(steam_root: Path) -> list[Path]:
    library_file = steam_root / "steamapps" / "libraryfolders.vdf"
    data = _load_vdf(library_file)
    library_folders = data.get("libraryfolders", {})

    candidates = [steam_root]
    if isinstance(library_folders, dict):
        for library in library_folders.values():
            if not isinstance(library, dict):
                continue
            path = library.get("path")
            if path:
                candidates.append(Path(path))

    return _unique_paths(candidates)


def _windows_steam_roots() -> list[Path]:
    try:
        import winreg
    except ImportError:
        return []

    registry_locations = (
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Valve\Steam"),
    )
    roots = []

    for hive, key_path in registry_locations:
        try:
            with winreg.OpenKey(hive, key_path) as key:
                for value_name in ("SteamPath", "InstallPath"):
                    try:
                        value, _ = winreg.QueryValueEx(key, value_name)
                    except OSError:
                        continue
                    if value:
                        roots.append(Path(value))
        except OSError:
            continue

    return roots


def _load_vdf(path: Path) -> dict:
    if not path.is_file():
        return {}

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            data = vdf.load(file)
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def _is_l4d2_path(path: Path) -> bool:
    return (path / "left4dead2" / "addons" / "workshop").is_dir()


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique = []
    seen = set()

    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)

    return unique


__all__ = ["find_l4d2_path", "find_steam_roots"]
