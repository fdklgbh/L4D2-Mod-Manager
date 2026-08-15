# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'update_page.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import QVBoxLayout

from qfluentwidgets import TextBrowser


class Ui_updateView(object):
    def setupUi(self, updateView):
        if not updateView.objectName():
            updateView.setObjectName("updateView")
        updateView.resize(629, 560)
        self.verticalLayout = QVBoxLayout(updateView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.update_info = TextBrowser(updateView)
        self.update_info.setObjectName("update_info")
        self.update_info.setContextMenuPolicy(Qt.NoContextMenu)
        self.update_info.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.update_info.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.verticalLayout.addWidget(self.update_info)

        self.retranslateUi(updateView)

        QMetaObject.connectSlotsByName(updateView)

    # setupUi

    def retranslateUi(self, updateView):
        updateView.setWindowTitle(
            QCoreApplication.translate("updateView", "Form", None)
        )

    # retranslateUi
