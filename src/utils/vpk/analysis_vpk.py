# -*- coding: utf-8 -*-
# @Time: 2025/12/18
# @Author: Administrator
# @File: analysis_vpk.py
import re
from pathlib import Path
from typing import TypeAlias

import vdf

from core import LogBase, appConstants, MenuCategory, Menu, VPKInfo
from schemas import ModCategory
from schemas.vpk_file_schemas import VPKFilePath
from .open_vpk import OpenVPK

CategoryResult: TypeAlias = ModCategory | None
FileList: TypeAlias = list[str]
Data: TypeAlias = dict[str, str]


class AnalysisVPK(LogBase):
    TAG = "AnalysisVPK"

    def getAddonInfo(self, path: Path, category: ModCategory = None) -> VPKInfo:
        vpk = OpenVPK(path)
        if not vpk.verify():
            self.logger.warning(f"{path.stem} 不是VPK文件")
            return self._no_data(path)
        data = vpk.get_addonInfo()
        if data:
            try:
                result: dict[str, dict[str, str]] = vdf.loads(data)
                key = None
                for i in result.keys():
                    if i.lower() == "addoninfo":
                        key = i
                        break
                if key is None:
                    raise SyntaxError(f"不存在addoninfo字段，字段有{result.keys()}")
                result: dict[str, str] = {
                    key.lower(): value for key, value in result.get(key).items()
                }
            except SyntaxError:
                self.logger.warning(f"vdf解析<{path.stem}>文件失败，开始手动解析")
                result: dict[str, str] = self._manual_parsing(data)
                self.logger.debug("解析成功")
            except Exception as e:
                self.logger.exception(f"出现异常信息:{e}")
                result = {}
        else:
            result = {}
            self.logger.warning(f"{path.stem} 没有addoninfo.txtt文件")
        filelist: list[str] = [i for i in vpk]
        if not category:
            category = self.check_type(filelist, result)
            if not category:
                for key in appConstants.mapKey:
                    value = result.get(key, "")
                    if value == "1":
                        category = ModCategory(category="地图")
                        break
                else:
                    category = ModCategory(category="其他")
        return VPKInfo(
            fileName=path.stem,
            category=category.category,
            subCategory=category.subCategory,
            addonInfo=result,
            addonInfoContent=data,
            customAddonInfo=result,
            customAddonInfoContent=data,
            url=self._url(path),
        )

    def check_type(self, fileList: list[str], data: dict[str, str]) -> CategoryResult:
        if category := self._check_map(fileList, data):
            return category
        if category := self._check_sky(fileList):
            return category
        vpkFilePath = VPKFilePath()
        for file in fileList:
            if file.endswith(".mdl"):
                vpkFilePath.mdl.append(file)
            elif file.endswith(".vtf"):
                vpkFilePath.vtf.append(file)
            elif file.endswith(".vmt"):
                vpkFilePath.vmt.append(file)
            elif file.startswith(("maps/", "missions")) or file.endswith(
                (".vtx", ".vvd", ".phy", ".jpg", ".png")
            ):
                continue
            else:
                vpkFilePath.path.append(file)
        if category := self._check_interface(vpkFilePath):
            return category
        if category := self._check_survivors(vpkFilePath):
            return category
        if category := self._check_others(vpkFilePath):
            return category
        return None

    def _check_others(self, info: VPKFilePath):
        for category in MenuCategory:
            if category in [
                MenuCategory.SURVIVOR,
                MenuCategory.MAP,
                MenuCategory.INFECTED,
            ]:
                continue
            if not Menu.get_category(category):
                return None
            return self._check_other(info, category)
        return None

    def _check_other(self, info: VPKFilePath, category: MenuCategory) -> CategoryResult:

        def check_suffix_rules(filepath: str, suffixPath: list[str]):
            if not suffixPath:
                return None
            return Path(filepath).stem in suffixPath

        def check_path(file_list: list[str] | str, path_list: list[str], regex=False):
            if not path_list:
                return False
            if isinstance(file_list, str):
                file_list = [file_list]
            for file in file_list:
                for path in path_list:
                    if regex and re.findall(file, path):
                        return True
                    elif not regex and file.startswith(path):
                        return True
            return False

        def check_file(suffix):
            if not (path_list := getattr(info, suffix, None)):
                return None
            regex_key = file_suffix + "_path_regex"
            for file in path_list:
                if category in [
                    MenuCategory.WEAPON,
                    MenuCategory.MELEE,
                    MenuCategory.MEDICAL,
                    MenuCategory.THROW,
                ]:
                    if not re.findall(
                        r"^(?:materials/)?models/.*?(?=[vw]_models|weapons).*$", file
                    ):
                        continue
                cats = Menu.get_category(category)
                if not Menu.has_child(category):
                    if not check_path(file, cats.get(regex_key), True):
                        continue
                    if check_suffix_rules(file, cats.get(suffix)):
                        return self.__result_category(category)
                    continue
                for sub, rules in cats.items():
                    if not (suffix_rule := rules.get(suffix)):
                        continue
                    if not check_path(file, rules.get(regex_key), True):
                        continue
                    if check_suffix_rules(file, suffix_rule):
                        return self.__result_category(category, sub)
            return None

        for file_suffix in ["mdl", "vmt", "vtf"]:
            if res := check_file(file_suffix):
                return res
        data = Menu.get_category(category)
        if not Menu.has_child(category):
            if check_path(info.path, data.get("path"), data.get("regex", False)):
                return self.__result_category(category, "")
        else:
            for k, sub in data.items():
                sub: dict
                if k == "脚本":
                    continue
                if check_path(info.path, sub.get("path"), sub.get("regex", False)):
                    return self.__result_category(category, k)
            if category == MenuCategory.ITEMS:
                script = Menu.subcategory_rules(category, "脚本")
                if check_path(
                    info.path, script.get("path"), script.get("regex", False)
                ):
                    return self.__result_category(category, "脚本")
        return None

    def _check_survivors(self, info: VPKFilePath):
        def res(sub):
            return self.__result_category(MenuCategory.SURVIVOR, sub)

        rules: dict[str, str] = Menu.get_category(MenuCategory.SURVIVOR)
        for mdl in info.mdl:
            if result := re.findall(r"models/survivors/survivor_(.+)\.mdl", mdl):
                for k, v in rules.items():
                    if k in ["语音", "比尔躯体"]:
                        continue
                    if result[0] == v:
                        return res(k)
            if "models/survivors/namvet/namvet_deathpose.mdl" == mdl:
                return res("比尔躯体")
        for path in info.path:
            if re.findall(rules.get("语音"), path):
                return res("语音")
        return None

    @staticmethod
    def __result_category(category, sub="") -> ModCategory:
        return ModCategory(category=category, subCategory=sub)

    def _check_interface(self, info: VPKFilePath) -> CategoryResult:
        def res(sub):
            return self.__result_category(MenuCategory.INFECTED, sub)

        rules = Menu.get_category(MenuCategory.INFECTED)
        for file in info.mdl:
            if not file.startswith("models/infected/"):
                continue
            name = Path(file).stem
            for i, value in rules.items():
                if regex := value.get("regex"):
                    if re.findall(regex, name):
                        return res(i)
                if mdl := value.get("mdl"):
                    if name in mdl:
                        return res(i)
        folders: set[str] = set()
        for file in info.vtf + info.vmt:
            if not file.startswith("materials/models/infected"):
                continue
            folders.add(file.split("/")[3])
        if len(folders) > 1:
            return res("多种特感")
        elif folders:
            for i, value in rules.items():
                if value.get("folder") == list(folders)[0]:
                    return res(i)
        sound_regex = rules.get("语音").get("path")
        for file in info.path:
            for regex in sound_regex:
                if re.findall(regex, file):
                    return res("语音")

        return None

    @staticmethod
    def _check_sky(fileList: FileList) -> CategoryResult:
        for file in fileList:
            if file.startswith("materials/skybox") and file.split("/")[-1].startswith(
                "sky_"
            ):
                return ModCategory(category=MenuCategory.ITEMS, subCategory="天空盒")
        return None

    @staticmethod
    def _check_map(fileList, data) -> CategoryResult:
        """
        检测地图类型
        Args:
            fileList:
            data:

        Returns:

        """
        maps = Menu.get_category(MenuCategory.MAP)
        for file in fileList:
            if any(re.findall(i, file) for i in maps.get("path_regex")):
                return ModCategory(category=MenuCategory.MAP)
        for key in appConstants.mapKey:
            if data.get(key) == "1":
                return ModCategory(category=MenuCategory.MAP)
        return None

    def _manual_parsing(self, text: str) -> dict[str, str]:
        res = text.splitlines()
        res = list(filter(None, res))
        data = appConstants.modKey
        find_key = ""
        result = {}
        for i in res:
            if find_key in data:
                data.remove(find_key)
            i = i.strip().lstrip("\t")
            temp = re.split(r"\s+", i, maxsplit=1)
            if i == "{" or i == '"AddonInfo"' or i == "}" or i == "":
                continue
            if temp[-1] == "''" or temp[-1] == '""':
                continue
            if len(temp) == 1:
                continue
            key, value = temp[0].lower(), temp[1]
            for j in data:
                if j in key:
                    if "addondescription_fr" in key:
                        continue
                    key = self._strip_quotes(key)
                    if key in appConstants.modKey:
                        value = self._remove_slash(value)
                        result[key] = self._strip_quotes(value)
                    find_key = key
                    break
        return result

    @staticmethod
    def _remove_slash(data):
        if "//" in data:
            count = data.count("//")
            if "http://" in data:
                if count > 1:
                    data = data.rsplit("//", maxsplit=1)[0].strip()
            elif count == 1:
                data = data.split("//")[0]
        return data

    @staticmethod
    def _strip_quotes(data: str):
        return data.strip().strip("\"'")

    def _no_data(self, path: Path) -> VPKInfo:
        return VPKInfo(
            fileName=path.stem, url=self._url(path), category="其他", subCategory=""
        )

    @staticmethod
    def _url(path: Path):
        return (
            ""
            if not path.stem.isdigit()
            else f"https://steamcommunity.com/sharedfiles/filedetails/?id={path.stem}"
        )
