# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'first_use.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from qfluentwidgets_pro import (
    BodyLabel,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    SubtitleLabel,
)


class Ui_firstUse(object):
    def setupUi(self, firstUse):
        if not firstUse.objectName():
            firstUse.setObjectName("firstUse")
        firstUse.resize(289, 223)
        self.verticalLayout = QVBoxLayout(firstUse)
        self.verticalLayout.setObjectName("verticalLayout")
        self.SubtitleLabel = SubtitleLabel(firstUse)
        self.SubtitleLabel.setObjectName("SubtitleLabel")

        self.verticalLayout.addWidget(self.SubtitleLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.BodyLabel = BodyLabel(firstUse)
        self.BodyLabel.setObjectName("BodyLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.BodyLabel)

        self.gamePathEdit = LineEdit(firstUse)
        self.gamePathEdit.setObjectName("gamePathEdit")
        self.gamePathEdit.setProperty("transparent", False)
        self.gamePathEdit.setProperty(
            "lightCustomQss", 'LineEdit[type="error"] {\n' "    color: red;\n" "}"
        )
        self.gamePathEdit.setProperty(
            "darkCustomQss", 'LineEdit[type="error"] {\n' "    color: red;\n" "}"
        )

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.gamePathEdit)

        self.BodyLabel_2 = BodyLabel(firstUse)
        self.BodyLabel_2.setObjectName("BodyLabel_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.BodyLabel_2)

        self.disablePathEdit = LineEdit(firstUse)
        self.disablePathEdit.setObjectName("disablePathEdit")

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.disablePathEdit
        )

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.sureBtn = PrimaryPushButton(firstUse)
        self.sureBtn.setObjectName("sureBtn")
        self.sureBtn.setEnabled(False)

        self.horizontalLayout.addWidget(self.sureBtn)

        self.quitBtn = PushButton(firstUse)
        self.quitBtn.setObjectName("quitBtn")

        self.horizontalLayout.addWidget(self.quitBtn)

        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(firstUse)
        self.gamePathEdit.textChanged.connect(firstUse.verify)
        self.disablePathEdit.textChanged.connect(firstUse.verify)

        QMetaObject.connectSlotsByName(firstUse)

    # setupUi

    def retranslateUi(self, firstUse):
        firstUse.setWindowTitle(
            QCoreApplication.translate("firstUse", "\u9996\u6b21\u914d\u7f6e", None)
        )
        self.SubtitleLabel.setText(
            QCoreApplication.translate(
                "firstUse", "\u8bbe\u7f6e\u914d\u7f6e\u8def\u5f84", None
            )
        )
        self.BodyLabel.setText(
            QCoreApplication.translate(
                "firstUse", "\u6e38\u620f\u6587\u4ef6\u5939", None
            )
        )
        self.gamePathEdit.setPlaceholderText(
            QCoreApplication.translate(
                "firstUse", "\u6e38\u620f\u6839\u76ee\u5f55", None
            )
        )
        self.BodyLabel_2.setText(
            QCoreApplication.translate(
                "firstUse", "\u7981\u7528mod\u6587\u4ef6\u5939", None
            )
        )
        self.disablePathEdit.setPlaceholderText(
            QCoreApplication.translate(
                "firstUse",
                "\u7981\u7528mod\u8def\u5f84(\u4e0d\u5b58\u5728\u4f1a\u81ea\u52a8\u521b\u5efa\u6587\u4ef6)",
                None,
            )
        )
        self.sureBtn.setText(
            QCoreApplication.translate("firstUse", "\u786e\u5b9a", None)
        )
        self.quitBtn.setText(
            QCoreApplication.translate("firstUse", "\u9000\u51fa", None)
        )

    # retranslateUi
