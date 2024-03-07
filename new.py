import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QComboBox,
    QProgressBar,
    QWizard,
    QWizardPage,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from data_processor import DataCut
import argparse
import subprocess
import shutil

class LogProcessorApp(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UFP 日志裁剪工具")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setPixmap(QWizard.LogoPixmap, QPixmap("logo.png"))  # 替换为您自己的logo
        self.addPage(FilesPage())
        self.addPage(KeywordPage())
        self.addPage(OptionsPage())
        self.addPage(ResultPage())
        self.setButtonText(QWizard.NextButton, "下一步")
        self.setButtonText(QWizard.BackButton, "上一步")
        self.setButtonText(QWizard.FinishButton, "完成")
        self.setWindowIcon(QIcon("icon.png"))  # 替换为您自己的图标
        self.resize(800, 600)

class FilesPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("选择日志文件")
        self.setSubTitle("请选择需要处理的日志文件。")

        layout = QVBoxLayout()
        self.files_input = QLineEdit()
        self.files_input.setPlaceholderText("输入日志文件路径或单击下方按钮选择")
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(self.browse_files)
        layout.addWidget(self.files_input)
        layout.addWidget(browse_button)
        self.setLayout(layout)

    def browse_files(self):
        file_dialog = QFileDialog()
        directory = file_dialog.getExistingDirectory(self, "请选择包含 Log 文件的文件夹")
        if directory:
            files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".log")]
            self.files_input.setText(", ".join(files))

    def validatePage(self):
        if not self.files_input.text():
            QMessageBox.warning(self, "警告", "请选择日志文件。")
            return False
        return True

class KeywordPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("设置关键词")
        self.setSubTitle("请输入用于初始化的关键词。")

        layout = QVBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入关键词，多个关键词用逗号分隔")
        layout.addWidget(self.keyword_input)
        self.setLayout(layout)

    def validatePage(self):
        if not self.keyword_input.text():
            QMessageBox.warning(self, "警告", "请输入关键词。")
            return False
        return True

class OptionsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("高级选项")
        self.setSubTitle("设置高级选项（可选）。")

        main_layout = QVBoxLayout()

        # 排序选项
        sort_layout = QHBoxLayout()
        self.sort_input = QCheckBox("按时间排序")
        sort_layout.addWidget(self.sort_input)
        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

        # 分隔符、表头名称、标识符
        options_layout = QGridLayout()
        delimiter_label = QLabel("日志分割符:")
        self.delimiter_input = QLineEdit("-----------------end------------------")
        options_layout.addWidget(delimiter_label, 0, 0)
        options_layout.addWidget(self.delimiter_input, 0, 1)

        table_nameP_label = QLabel("表头名:")
        self.table_nameP_input = QLineEdit("HwTblID")
        options_layout.addWidget(table_nameP_label, 1, 0)
        options_layout.addWidget(self.table_nameP_input, 1, 1)

        notion_label = QLabel("标识符:")
        self.notion_input = QLineEdit(":")
        options_layout.addWidget(notion_label, 2, 0)
        options_layout.addWidget(self.notion_input, 2, 1)

        main_layout.addLayout(options_layout)
        self.setLayout(main_layout)

class ResultPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("处理结果")
        self.setSubTitle("日志处理结果将显示在下面的文本区域中。")

        layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.save_button = QPushButton("保存结果")
        self.save_button.clicked.connect(self.save_result)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def initializePage(self):
        self.start_processing()

    def start_processing(self):
        # 从上一页获取输入值
        files_page = self.wizard().page(0)
        files = files_page.files_input.text().split(", ")

        keyword_page = self.wizard().page(1)
        initKeyword = keyword_page.keyword_input.text().split(", ")

        options_page = self.wizard().page(2)
        sort = options_page.sort_input.isChecked()
        delimiter = options_page.delimiter_input.text()
        table_nameP = options_page.table_nameP_input.text()
        notion = options_page.notion_input.text()

        # 构建配置对象
        config = argparse.Namespace(
            files=files,
            initKeyword=initKeyword,
            sort=sort,
            delimiter=delimiter,
            table_nameP=table_nameP,
            notion=notion,
        )

        # 创建DataCut实例并处理数据
        self.data_processor = DataCut(config)
        self.progress_bar.setMaximum(len(files))

        # 处理数据并显示结果
        from data_processor import print_by_format, save_to_txt

        output_str = ""
        for i, file in enumerate(files):
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()  # 确保进度条能够及时更新
            output_str += f"处理文件: {file}\n\n"
            output_str += print_by_format(self.data_processor, file)
            output_str += "\n\n"

        self.output_text.setText(output_str)

    def save_result(self):
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(
            self, "保存文件", "output.log", "Log Files (*.log)"
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.output_text.toPlainText())
                QMessageBox.information(self, "成功", "结果已保存到文件。")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存文件发生错误：{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LogProcessorApp()
    ex.show()
    sys.exit(app.exec_())