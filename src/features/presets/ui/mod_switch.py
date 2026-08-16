# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mod_switch.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidgetItem, QSizePolicy,
    QWidget)

from qfluentwidgets import ListWidget

class Ui_ModSwitchInterface(object):
    def setupUi(self, ModSwitchInterface):
        if not ModSwitchInterface.objectName():
            ModSwitchInterface.setObjectName(u"ModSwitchInterface")
        ModSwitchInterface.resize(944, 624)
        self.horizontalLayout = QHBoxLayout(ModSwitchInterface)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.switch_type_info = ListWidget(ModSwitchInterface)
        self.switch_type_info.setObjectName(u"switch_type_info")
        self.switch_type_info.setContextMenuPolicy(Qt.CustomContextMenu)

        self.horizontalLayout.addWidget(self.switch_type_info)

        self.switch_type_show = ListWidget(ModSwitchInterface)
        self.switch_type_show.setObjectName(u"switch_type_show")
        self.switch_type_show.setContextMenuPolicy(Qt.NoContextMenu)

        self.horizontalLayout.addWidget(self.switch_type_show)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 7)

        self.retranslateUi(ModSwitchInterface)

        QMetaObject.connectSlotsByName(ModSwitchInterface)
    # setupUi

    def retranslateUi(self, ModSwitchInterface):
        ModSwitchInterface.setWindowTitle(QCoreApplication.translate("ModSwitchInterface", u"Form", None))
    # retranslateUi
