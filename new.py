import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QCheckBox, QGroupBox, QHBoxLayout
from PyQt5.QtCore import Qt
from data_processor import DataCut
import argparse

class LogProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UFP日志裁剪工具')
        self.setGeometry(100, 100, 600, 400)  # 窗口的x轴位置，y轴位置，宽，高

        # 使用样式表改善视觉效果
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QLabel, QCheckBox {
                padding: 2px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        self.files_input = QLineEdit('./datalab/')
        self.browse_button = QPushButton('选择您的文件夹')
        self.browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(self.files_input)
        file_layout.addWidget(self.browse_button)
        file_group.setLayout(file_layout)

        # 设置组
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout()
        self.keyword_input = QLineEdit('vpnnh, key:7')
        self.sort_input = QCheckBox('按时间排序')
        self.delimiter_input = QLineEdit('-----------------end------------------')
        settings_layout.addWidget(QLabel('初始化关键词:'))
        settings_layout.addWidget(self.keyword_input)
        settings_layout.addWidget(self.sort_input)
        settings_layout.addWidget(QLabel('日志分割符:'))
        settings_layout.addWidget(self.delimiter_input)
        settings_group.setLayout(settings_layout)

        # 输出区域
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)

        # 开始按钮
        self.start_button = QPushButton('开始处理')
        self.start_button.clicked.connect(self.start_processing)

        layout.addWidget(file_group)
        layout.addWidget(settings_group)
        layout.addWidget(self.start_button)
        layout.addWidget(output_group)

        self.setLayout(layout)

    def browse_files(self):
        file_dialog = QFileDialog()
        directory = file_dialog.getExistingDirectory(self, "请选择包含 Log 文件的文件夹")
        if directory:
            files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.log')]
            self.files_input.setText(", ".join(files))

    def start_processing(self):
        # 从GUI获取输入值
        files = self.files_input.text()
        initKeyword = self.keyword_input.text()
        sort = str(self.sort_input.isChecked())
        delimiter = self.delimiter_input.text()
        table_nameP =  self.table_nameP_input.text()
        notion = self.notion_input.text()

        # 构建配置对象
        config = argparse.Namespace(
            files=files.split(', '),  # 假设文件名通过逗号分隔
            initKeyword=initKeyword.split(', '),  # 假设关键字通过逗号分隔
            sort=sort.lower() in ('true', 'yes', '1'),  # 将字符串转换为布尔值
            delimiter=delimiter,
            table_nameP=table_nameP,
            notion=notion
        )

        # 创建DataCut实例并处理数据
        data_processor = DataCut(config)

        # 将结果显示在GUI的文本区域
        from data_processor import print_by_format, save_to_txt
        output_str = print_by_format(data_processor, self.delimiter_input.text())
        
        # 显示结果在GUI的文本区域
        self.output_text.setText(output_str)
        
        # 保存结果到文件
        output_file = "output.log"  # 指定输出文件的名称和路径
        save_to_txt(output_str, output_file) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LogProcessorApp()
    ex.show()
    sys.exit(app.exec_())
