import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt
from data_processor import DataCut, parse_opt
import argparse
import os

class LogProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UFP日志裁剪工具')
        self.setGeometry(100, 100, 600, 800) #参数分别为窗口的x轴位置，y轴位置，宽，高，

        layout = QVBoxLayout()
        # 创建输入框和标签
        self.files_label = QLabel('文件:')
        self.files_input = QLineEdit('./datalab/')
        self.keyword_label = QLabel('初始化关键词:')
        self.keyword_input = QLineEdit('vpnnh, key:7')
        self.sort_label = QLabel('按时间排序:')
        self.sort_input = QCheckBox() 
        self.delimiter_label = QLabel('日志分割符:')
        self.delimiter_input = QLineEdit('-----------------end------------------')
        self.table_nameP_label = QLabel('表头名:')
        self.table_nameP_input = QLineEdit('HwTblID')
        self.notion_label = QLabel('标识符:')
        self.notion_input = QLineEdit(':')
        
        # 创建按钮
        self.browse_button = QPushButton('选择您的文件夹')
        self.browse_button.clicked.connect(self.browse_files)
        self.start_button = QPushButton('日志裁剪')
        self.start_button.clicked.connect(self.start_processing)
        
        # 创建输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        self.prompt = QLabel('日志结果输出于 "output.log" ')

        # 创建一个水平布局
        hbox = QHBoxLayout()

        # 将sort_label和sort_input添加到这个布局中
        hbox.addWidget(self.sort_label)
        hbox.addWidget(self.sort_input)

        # 添加组件到布局
        layout.addWidget(self.files_label)
        layout.addWidget(self.files_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.keyword_label)
        layout.addWidget(self.keyword_input)

        # 将这个水平布局添加到你的主布局中
        layout.addLayout(hbox)

        layout.addWidget(self.delimiter_label)
        layout.addWidget(self.delimiter_input)
        layout.addWidget(self.table_nameP_label)
        layout.addWidget(self.table_nameP_input)
        layout.addWidget(self.notion_label)
        layout.addWidget(self.notion_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.prompt)
        self.prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.output_text)
        self.setLayout(layout)

    # def browse_files(self):
    #     file_dialog = QFileDialog()
    #     files, _ = file_dialog.getOpenFileNames(self, "请选择 Log 文件", "", "Log 文件 (*.log)")
    #     self.files_input.setText(", ".join(files))

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
