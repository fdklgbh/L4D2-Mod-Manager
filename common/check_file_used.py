# -*- coding: utf-8 -*-
# @Time: 2024/12/22
# @Author: Administrator
# @File: check_file_used.py
import win32file


def is_used(filename):
    try:
        vHandle = win32file.CreateFile(str(filename), win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING,
                                       win32file.FILE_ATTRIBUTE_NORMAL, None)
        return int(vHandle) == win32file.INVALID_HANDLE_VALUE
    except:
        return True
    finally:
        try:
            win32file.CloseHandle(vHandle)
        except:
            pass


__all__ = ['is_used']

if __name__ == '__main__':
    p = r'E:\SteamLibrary\steamapps\common\Left 4 Dead 2\left4dead2\addons\map 活死人黎明加长版 - 副本.vpk'
    print(is_used(p))