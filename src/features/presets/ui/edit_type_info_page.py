# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_type_info_page.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QListWidgetItem,
    QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)

from qfluentwidgets import (CheckBox, DropDownPushButton, LineEdit, ListWidget,
    PrimaryPushButton, ProgressBar, PushButton, SearchLineEdit,
    SubtitleLabel)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1200, 1000)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.saveNameEdit = LineEdit(Form)
        self.saveNameEdit.setObjectName(u"saveNameEdit")
        self.saveNameEdit.setMaximumSize(QSize(300, 33))

        self.horizontalLayout.addWidget(self.saveNameEdit)

        self.typeBox = DropDownPushButton(Form)
        self.typeBox.setObjectName(u"typeBox")
        self.typeBox.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.typeBox)

        self.syncType = CheckBox(Form)
        self.syncType.setObjectName(u"syncType")

        self.horizontalLayout.addWidget(self.syncType)

        self.searchLineEdit = SearchLineEdit(Form)
        self.searchLineEdit.setObjectName(u"searchLineEdit")
        self.searchLineEdit.setMaximumSize(QSize(400, 33))

        self.horizontalLayout.addWidget(self.searchLineEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(3, 4)
        self.horizontalLayout.setStretch(4, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.horizontalLayout_7 = QHBoxLayout(self.page_2)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer_5 = QSpacerItem(396, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_5)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_5)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.ProgressBar = ProgressBar(self.page_2)
        self.ProgressBar.setObjectName(u"ProgressBar")
        self.ProgressBar.setMaximumSize(QSize(16777215, 10))
        self.ProgressBar.setOrientation(Qt.Horizontal)

        self.horizontalLayout_5.addWidget(self.ProgressBar)

        self.horizontalLayout_5.setStretch(0, 6)

        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.SubtitleLabel = SubtitleLabel(self.page_2)
        self.SubtitleLabel.setObjectName(u"SubtitleLabel")

        self.horizontalLayout_6.addWidget(self.SubtitleLabel)

        self.loadingModText = SubtitleLabel(self.page_2)
        self.loadingModText.setObjectName(u"loadingModText")

        self.horizontalLayout_6.addWidget(self.loadingModText)

        self.horizontalLayout_6.setStretch(0, 2)
        self.horizontalLayout_6.setStretch(1, 7)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_6)


        self.horizontalLayout_7.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_6 = QSpacerItem(396, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_7.setStretch(0, 3)
        self.horizontalLayout_7.setStretch(1, 4)
        self.horizontalLayout_7.setStretch(2, 3)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.horizontalLayout_4 = QHBoxLayout(self.page_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.disabledWdiget = ListWidget(self.page_3)
        self.disabledWdiget.setObjectName(u"disabledWdiget")
        self.disabledWdiget.setMinimumSize(QSize(50, 0))
        self.disabledWdiget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.horizontalLayout_4.addWidget(self.disabledWdiget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.enabledBtn = PushButton(self.page_3)
        self.enabledBtn.setObjectName(u"enabledBtn")
        self.enabledBtn.setEnabled(False)

        self.verticalLayout.addWidget(self.enabledBtn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.disabledBtn = PushButton(self.page_3)
        self.disabledBtn.setObjectName(u"disabledBtn")
        self.disabledBtn.setEnabled(False)

        self.verticalLayout.addWidget(self.disabledBtn)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.disableAllBtn = PushButton(self.page_3)
        self.disableAllBtn.setObjectName(u"disableAllBtn")
        self.disableAllBtn.setEnabled(False)

        self.verticalLayout.addWidget(self.disableAllBtn)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(3, 1)
        self.verticalLayout.setStretch(5, 1)
        self.verticalLayout.setStretch(6, 3)

        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.enabledWidget = ListWidget(self.page_3)
        self.enabledWidget.setObjectName(u"enabledWidget")
        self.enabledWidget.setEnabled(True)
        self.enabledWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.horizontalLayout_4.addWidget(self.enabledWidget)

        self.stackedWidget.addWidget(self.page_3)

        self.horizontalLayout_3.addWidget(self.stackedWidget)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.saveBtn = PrimaryPushButton(Form)
        self.saveBtn.setObjectName(u"saveBtn")
        self.saveBtn.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.saveBtn)

        self.closeBtn = PushButton(Form)
        self.closeBtn.setObjectName(u"closeBtn")

        self.horizontalLayout_2.addWidget(self.closeBtn)

        self.horizontalLayout_2.setStretch(0, 8)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)
        self.searchLineEdit.textChanged.connect(Form.searchChange)
        self.searchLineEdit.clearSignal.connect(Form.searchChange)
        self.searchLineEdit.searchSignal.connect(Form.searchChange)
        self.enabledBtn.clicked.connect(Form.enableMod)
        self.disableAllBtn.clicked.connect(Form.disableAllMod)
        self.disabledBtn.clicked.connect(Form.disableMod)
        self.disabledWdiget.doubleClicked.connect(Form.copyFileTitle)
        self.enabledWidget.doubleClicked.connect(Form.copyFileTitle)
        self.saveBtn.clicked.connect(Form.savePage)
        self.closeBtn.clicked.connect(Form.close)
        self.saveNameEdit.textChanged.connect(Form.fileNameChanged)
        self.syncType.toggled.connect(Form.syncTypeBtnChanged)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.saveNameEdit.setInputMask("")
        self.saveNameEdit.setText("")
        self.saveNameEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u540d\u79f0", None))
        self.typeBox.setText(QCoreApplication.translate("Form", u"\u5168\u90e8", None))
        self.syncType.setText(QCoreApplication.translate("Form", u"\u5206\u7c7b\u7b5b\u9009\u4e24\u4fa7", None))
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u641c\u7d22", None))
        self.SubtitleLabel.setText(QCoreApplication.translate("Form", u"\u6b63\u5728\u52a0\u8f7d:", None))
        self.loadingModText.setText(QCoreApplication.translate("Form", u"\u52a0\u8f7d\u4e2d...", None))
#if QT_CONFIG(tooltip)
        self.disabledWdiget.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.disabledWdiget.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.enabledBtn.setText(QCoreApplication.translate("Form", u"\u542f\u7528", None))
        self.disabledBtn.setText(QCoreApplication.translate("Form", u"\u7981\u7528", None))
        self.disableAllBtn.setText(QCoreApplication.translate("Form", u"\u5168\u90e8\u7981\u7528", None))
        self.saveBtn.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58", None))
        self.closeBtn.setText(QCoreApplication.translate("Form", u"\u5173\u95ed", None))
    # retranslateUi
