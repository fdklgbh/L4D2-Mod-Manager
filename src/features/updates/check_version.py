# -*- coding: utf-8 -*-

from collections.abc import Mapping

import requests
from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from loguru import logger
from packaging import version
from qfluentwidgets_pro import MessageBox

from shared.app import appConstants

UPDATE_URL = "https://fdklgbh.github.io/L4D2-Mod-Manager/update_version.json"


def build_update_result(
    data: Mapping[str, object], current_version: str, is_dev: bool
) -> dict[str, object]:
    try:
        remote_version = str(data["version"])
        package_url = data["package"]
        if not isinstance(package_url, str) or not package_url:
            raise ValueError("package url is invalid")

        local = version.parse(current_version.split(" ")[0])
        remote = version.parse(remote_version)
    except (KeyError, TypeError, ValueError):
        return {"status": False, "msg": "版本信息格式错误,请稍后重试!"}

    update = local < remote or (is_dev and local == remote)
    result: dict[str, object] = {"status": True, "update": update}
    if update:
        result["url"] = package_url
        result["version"] = remote_version
    return result


class CheckVersion(QThread):
    resultSignal = Signal(dict)

    def run(self):
        self.resultSignal.emit(self.sendRequest())

    @staticmethod
    def sendRequest() -> dict[str, object]:
        try:
            response = requests.get(UPDATE_URL, timeout=5)
        except requests.RequestException:
            return {"status": False, "msg": "请求失败或者超时,请检查网络状态!"}

        if response.status_code != 200:
            logger.warning("更新检查响应码: {}", response.status_code)
            return {
                "status": False,
                "msg": f"响应码: {response.status_code},具体信息看日志",
            }

        try:
            data = response.json()
        except ValueError:
            return {"status": False, "msg": "更新信息解析失败,请稍后重试!"}

        if not isinstance(data, Mapping):
            return {"status": False, "msg": "版本信息格式错误,请稍后重试!"}

        return build_update_result(data, appConstants.VERSION, appConstants.DEBUG)


def show_version_dialog(result: Mapping[str, object], parent, isAuto=False):
    need_open = False
    hide_cancel = False
    yes_text = "去更新"

    if result.get("status") is True:
        if result.get("update") is True:
            content = f"有新版本 {appConstants.VERSION} -> {result.get('version')}"
            need_open = True
        elif isAuto:
            return
        else:
            content = "当前已是最新版本, 无需更新"
            hide_cancel = True
            yes_text = "确定"
    else:
        content = str(result.get("msg") or "检查更新失败,请稍后重试!")
        yes_text = "确定"

    dialog = MessageBox("更新", content, parent.window())
    dialog.yesButton.setText(yes_text)
    if hide_cancel:
        dialog.cancelButton.hide()
        dialog.buttonLayout.insertStretch(0, 1)
    dialog.cancelButton.setText("关闭")

    if dialog.exec() and need_open:
        url = result.get("url")
        remote_version = result.get("version")
        if isinstance(url, str) and isinstance(remote_version, str):
            QDesktopServices.openUrl(QUrl(f"{url.rstrip('/')}/tag/{remote_version}"))


__all__ = ["CheckVersion", "UPDATE_URL", "build_update_result", "show_version_dialog"]
