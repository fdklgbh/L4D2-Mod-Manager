# -*- coding: utf-8 -*-
# @Time: 2025/12/17
# @Author: Administrator
# @File: open_vpk.py
import struct
from pathlib import Path

import chardet

from shared.runtime import LogBase

from . import vpk_change as vpk


class OpenVPK(LogBase):
    TAG = "VPK"

    def __init__(self, filePath: Path):
        self._filePath = filePath
        self._vpk: vpk.VPK = self._open()

    def _open(self):
        path = self._filePath
        try:
            pak1 = vpk.open(path)
        except UnicodeError:
            pak1 = vpk.open(path, path_enc="ansi")
        except TypeError:
            self.logger.error(f"{path}文件打开失败")
            return None
        except struct.error:
            self.logger.error(f"{path}文件不是vpk文件")
            return False
        except FileNotFoundError as e:
            raise
        except Exception as e:
            self.logger.error(f"{path}文件打开过程中出现错误, 错误信息:{e}")
            return None
        return pak1

    def __iter__(self):
        return iter(self._vpk)

    def verify(self) -> bool:
        return bool(self._vpk)

    def get_addonInfo(self) -> str:
        try:
            with self._vpk.get_file("addoninfo.txt") as f:
                content = f.read()
        except KeyError:
            return ""
        return self._decode_file(content) or ""

    def get_img(self, imgName: str = "addonimage.jpg"):
        with self._vpk.get_file(imgName) as f:
            content = f.read()
            return content

    def _decode_file(self, content: bytes):
        """
        二进制文件解码返回数据
        Args:
            content:

        Returns:

        """
        try:
            try:
                result = content.decode("utf8")
            except UnicodeError:
                result = content.decode("gbk")
        except UnicodeError:
            try:
                res = chardet.detect(content)
                encoding = res["encoding"]
                if encoding == "ISO-8859-1":
                    encoding = "ansi"
                try:
                    result = content.decode(encoding)
                except UnicodeError:
                    encoding = "ISO-8859-1"
                    result = content.decode(encoding)
            except UnicodeError:
                self.logger.warning(f"解码失败")
                return False
        return result


if __name__ == "__main__":
    a = OpenVPK(Path(r"E:\l4d2\禁用mod\1987326534.vpk"))
    for i in a:
        print(i)
