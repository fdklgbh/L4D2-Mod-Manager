# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modules_page.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    CheckBox,
    DropDownPushButton,
    PixmapLabel,
    PlainTextEdit,
    SearchLineEdit,
    SplitPushButton,
)
from views.components import ModShowTableView


class Ui_modShowView(object):
    def setupUi(self, modShowView):
        if not modShowView.objectName():
            modShowView.setObjectName("modShowView")
        modShowView.resize(882, 876)
        modShowView.setTabletTracking(False)
        self.verticalLayout = QVBoxLayout(modShowView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.search_edit = SearchLineEdit(modShowView)
        self.search_edit.setObjectName("search_edit")
        self.search_edit.setProperty("transparent", False)
        self.search_edit.setProperty(
            "lightCustomQss", 'LineEdit[type="error"] {\n' "    color: red;\n" "}"
        )
        self.search_edit.setProperty(
            "darkCustomQss", 'LineEdit[type="error"] {\n' "    color: red;\n" "}"
        )

        self.horizontalLayout.addWidget(self.search_edit)

        self.regexBtn = CheckBox(modShowView)
        self.regexBtn.setObjectName("regexBtn")

        self.horizontalLayout.addWidget(self.regexBtn)

        self.refresh_btn = SplitPushButton(modShowView)
        self.refresh_btn.setObjectName("refresh_btn")

        self.horizontalLayout.addWidget(self.refresh_btn)

        self.menu_btn = DropDownPushButton(modShowView)
        self.menu_btn.setObjectName("menu_btn")
        self.menu_btn.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.menu_btn)

        self.autoRaise = CheckBox(modShowView)
        self.autoRaise.setObjectName("autoRaise")

        self.horizontalLayout.addWidget(self.autoRaise)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(modShowView)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(6)
        self.splitter.setChildrenCollapsible(True)
        self.tableView = ModShowTableView(self.splitter)
        self.tableView.setObjectName("tableView")
        self.splitter.addWidget(self.tableView)
        self.vkp_info = QWidget(self.splitter)
        self.vkp_info.setObjectName("vkp_info")
        self.verticalLayout_2 = QVBoxLayout(self.vkp_info)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_2 = QSpacerItem(
            286, 37, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.file_pic = PixmapLabel(self.vkp_info)
        self.file_pic.setObjectName("file_pic")

        self.verticalLayout_2.addWidget(self.file_pic)

        self.addons_info = PlainTextEdit(self.vkp_info)
        self.addons_info.setObjectName("addons_info")
        self.addons_info.setTabletTracking(False)
        self.addons_info.setTabChangesFocus(True)
        self.addons_info.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.addons_info.setReadOnly(True)
        self.addons_info.setBackgroundVisible(False)

        self.verticalLayout_2.addWidget(self.addons_info)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(2, 5)
        self.splitter.addWidget(self.vkp_info)

        self.verticalLayout.addWidget(self.splitter)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 9)
        QWidget.setTabOrder(self.search_edit, self.tableView)

        self.retranslateUi(modShowView)
        self.search_edit.searchSignal.connect(modShowView.perform_search)
        self.search_edit.textChanged.connect(modShowView.perform_search)
        self.search_edit.clearSignal.connect(modShowView.perform_search)
        self.splitter.splitterMoved.connect(modShowView.handleSplitterMoved)
        self.regexBtn.clicked["bool"].connect(modShowView.changePlaceholderText)
        self.tableView.doubleClicked.connect(modShowView.onDoubleClicked)

        QMetaObject.connectSlotsByName(modShowView)

    # setupUi

    def retranslateUi(self, modShowView):
        modShowView.setWindowTitle(
            QCoreApplication.translate("modShowView", "Frame", None)
        )
        self.search_edit.setPlaceholderText("")
        self.regexBtn.setText(
            QCoreApplication.translate("modShowView", "\u6b63\u5219", None)
        )
        self.refresh_btn.setProperty(
            "text_", QCoreApplication.translate("modShowView", "\u5237\u65b0", None)
        )
        self.menu_btn.setText(
            QCoreApplication.translate("modShowView", "\u5168\u90e8", None)
        )
        self.autoRaise.setText(
            QCoreApplication.translate("modShowView", "\u81ea\u8c03\u6574", None)
        )

    # retranslateUi
