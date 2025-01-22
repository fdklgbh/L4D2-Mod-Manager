# -*- coding: utf-8 -*-
# @Time: 2025/1/20
# @Author: Administrator
# @File: dialog.py
from typing import Union

from qfluentwidgets import Dialog, MessageBox

__all__ = ['customDialog', 'customMessageBox']


def customDialog(title, content, parent, yesBtn: Union[bool, str] = '确定', cancelBtn: Union[bool, str] = '取消',
                 hideTitleBar=True):
    w = Dialog(title, content, parent)
    _buttonStatus(yesBtn, cancelBtn, w)
    if hideTitleBar:
        w.windowTitleLabel.hide()
    return w.exec()


def _buttonStatus(yesBtn, cancelBtn, w):
    if isinstance(yesBtn, str):
        w.yesButton.setText(yesBtn)
    else:
        if yesBtn is False:
            w.yesButton.hide()
            w.buttonLayout.insertStretch(0, 1)
    if isinstance(cancelBtn, str):
        w.cancelButton.setText(cancelBtn)
    else:
        if cancelBtn is False:
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(0, 1)
    if cancelBtn is False and yesBtn is False:
        w.buttonGroup.hide()


def customMessageBox(title, message, parent, yesBtn: Union[bool, str] = '确定', cancelBtn: Union[bool, str] = '取消',
                     canCopy=False):
    w = MessageBox(title, message, parent)
    _buttonStatus(yesBtn, cancelBtn, w)
    w.setContentCopyable(canCopy)
    return w.exec()

