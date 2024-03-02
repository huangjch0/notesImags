import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from data_processor import DataCut, parse_opt
import argparse

class LogProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Log Processor')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        
        # 创建输入框和标签
        self.files_label = QLabel('Files:')
        self.files_input = QLineEdit('./ldp.log')
        self.keyword_label = QLabel('Initial Keywords:')
        self.keyword_input = QLineEdit('vpnnh, key:7')
        self.sort_label = QLabel('Sort by Time:')
        self.sort_input = QLineEdit('False')
        self.delimiter_label = QLabel('Delimiter:')
        self.delimiter_input = QLineEdit('-----------------end------------------')
        
        # 创建按钮
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_files)
        self.start_button = QPushButton('Start Processing')
        self.start_button.clicked.connect(self.start_processing)
        
        # 创建输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # 添加组件到布局
        layout.addWidget(self.files_label)
        layout.addWidget(self.files_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.keyword_label)
        layout.addWidget(self.keyword_input)
        layout.addWidget(self.sort_label)
        layout.addWidget(self.sort_input)
        layout.addWidget(self.delimiter_label)
        layout.addWidget(self.delimiter_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def browse_files(self):
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(self, "Select log files", "", "Log Files (*.log)")
        self.files_input.setText(", ".join(files))

    def start_processing(self):
        # 从GUI获取输入值
        files = self.files_input.text()
        initKeyword = self.keyword_input.text()
        sort = self.sort_input.text()
        delimiter = self.delimiter_input.text()
        table_nameP = "HwTblID"  # 如果有GUI字段，则替换为相应的self.table_nameP_input.text()
        notion = ":"  # 如果有GUI字段，则替换为相应的self.notion_input.text()
    
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
        result = data_processor.process_data_from_gui(files, initKeyword, sort, delimiter, table_nameP, notion)
    
        # 将结果显示在GUI的文本区域
        formatted_result = "\n".join(result)
        self.output_text.setText(formatted_result)
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LogProcessorApp()
    ex.show()
    sys.exit(app.exec_())