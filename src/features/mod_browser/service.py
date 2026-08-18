# -*- coding: utf-8 -*-

"""模组浏览页面的数据库业务服务。"""

from collections.abc import Iterable
from pathlib import Path

from shared.mods import ModCategory, ModInfo
from shared.persistence import BasePageService, VPKInfo
from shared.vpk import AnalysisVPK


class ModBrowserService(BasePageService):
    """Mod 页面数据库服务。"""

    def add_vpk_info(self, vpk_info: VPKInfo, commit: bool = True) -> VPKInfo:
        """添加 VPK 信息。

        Args:
            vpk_info：待添加的 VPK 信息。
            commit：是否立即提交，默认提交。
        """
        self.session.add(vpk_info)
        if commit:
            self.commit()
        return vpk_info

    def load_or_refresh_mod_infos(
        self,
        files: Iterable[Path],
        analyzer: AnalysisVPK,
        refresh: bool = False,
        commit: bool = True,
    ) -> list[ModInfo]:
        """批量加载或刷新 VPK 信息。

        Args:
            files：待处理的 VPK 文件。
            analyzer：VPK 信息解析器。
            refresh：是否重新解析已有缓存。
            commit：是否在批量处理完成后提交，默认提交一次。
        """
        results: list[ModInfo] = []
        try:
            for file in files:
                vpk_info: VPKInfo | None = (
                    self.session.query(VPKInfo)
                    .filter(VPKInfo.fileName == file.stem)
                    .first()
                )
                if vpk_info is None:
                    vpk_info = analyzer.getAddonInfo(file)
                    self.add_vpk_info(vpk_info, commit=False)
                elif refresh:
                    refreshed = analyzer.getAddonInfo(
                        file,
                        ModCategory(
                            category=vpk_info.category,
                            subCategory=vpk_info.subCategory,
                        ),
                    )
                    vpk_info.customAddonInfo = refreshed.addonInfo
                    vpk_info.customAddonInfoContent = refreshed.addonInfoContent

                results.append(ModInfo.from_vpk_info(vpk_info))

            if commit:
                self.commit()
        except Exception:
            self.rollback()
            raise
        return results

    def update_categories(
        self,
        filenames: list[str],
        category: ModCategory,
        commit: bool = True,
    ) -> None:
        """批量更新 VPK 分类。

        Args:
            filenames：待更新的 VPK 文件名。
            category：新的分类。
            commit：是否立即提交，默认提交。

        Raises:
            ValueError：一个或多个请求的 VPK 记录不存在。
        """
        if not filenames:
            return

        unique_filenames = list(dict.fromkeys(filenames))
        try:
            records = (
                self.session.query(VPKInfo)
                .filter(VPKInfo.fileName.in_(unique_filenames))
                .all()
            )
            records_by_name = {record.fileName: record for record in records}
            missing = [
                filename
                for filename in unique_filenames
                if filename not in records_by_name
            ]
            if missing:
                missing_names = ", ".join(missing)
                raise ValueError(f"未找到以下 VPK 记录: {missing_names}")

            for filename in unique_filenames:
                record = records_by_name[filename]
                record.category = category.category
                record.subCategory = category.subCategory

            if commit:
                self.commit()
        except Exception:
            self.rollback()
            raise


mod_browser_service = ModBrowserService()

__all__ = ["ModBrowserService", "mod_browser_service"]
