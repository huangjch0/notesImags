import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QCheckBox, QGroupBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from data_processor import DataCut, parse_opt
import argparse

class LogProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UFP 日志裁剪工具')
        self.setGeometry(700, 300, 600, 400)

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

        main_layout = QHBoxLayout()

        # Create the left and right vertical layouts
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # layout = QVBoxLayout()
        # left_layout.setSpacing(10)
        # right_layout.setSpacing(10)
        
        # 创建输入框和标签
        self.files_label = QLabel('文件选择:')
        self.files_input = QLineEdit('./ldp.log')
        self.keyword_label = QLabel('初始化关键词:')
        self.keyword_input = QLineEdit('vpnnh, key:7')
        self.sort_input = QCheckBox('按时间排序')
        self.delimiter_label = QLabel('日志分割符:')
        self.delimiter_input = QLineEdit('-----------------end------------------')
        self.table_nameP_label = QLabel('表头名:')
        self.table_nameP_input = QLineEdit('HwTblID')
        self.notion_label = QLabel('标识符:')
        self.notion_input = QLineEdit(':')
        self.prompt_label = QLabel('文件的最终结果将会保存在当前文件夹下的output.log文件中')
        
        # 创建按钮
        self.browse_button = QPushButton('请选择您的文件夹')
        self.browse_button.clicked.connect(self.browse_files)
        self.start_button = QPushButton('开始处理')
        self.start_button.clicked.connect(self.start_processing)
        
        # 创建输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # 添加组件到布局
        left_layout.addWidget(self.files_label)
        left_layout.addWidget(self.files_input)
        left_layout.addWidget(self.browse_button)
        left_layout.addWidget(self.keyword_label)
        left_layout.addWidget(self.keyword_input)
        right_layout.addWidget(self.sort_input)
        # layout.addWidget(self.delimiter_label)
        # layout.addWidget(self.delimiter_input)
        
        # 创建可折叠区域的组件
        self.collapsible_box = QGroupBox("高级选项")
        self.collapsible_box_layout = QVBoxLayout()

        # 向可折叠区域的布局添加组件
        self.collapsible_box_layout.addWidget(self.delimiter_label)
        self.collapsible_box_layout.addWidget(self.delimiter_input)
        self.collapsible_box_layout.addWidget(self.table_nameP_label)
        self.collapsible_box_layout.addWidget(self.table_nameP_input)
        self.collapsible_box_layout.addWidget(self.notion_label)
        self.collapsible_box_layout.addWidget(self.notion_input)

        # 设置可折叠区域的布局
        self.collapsible_box.setLayout(self.collapsible_box_layout)

        # 创建控制折叠的按钮
        self.toggle_button = QPushButton("展开/收起高级选项")
        self.toggle_button.clicked.connect(self.toggle_collapsible_box)

        # 向主布局添加控制折叠的按钮和可折叠区域
        left_layout.addWidget(self.toggle_button)
        left_layout.addWidget(self.collapsible_box)
        self.collapsible_box.hide()
        # layout.addWidget(self.table_nameP_label)
        # layout.addWidget(self.table_nameP_input)
        # layout.addWidget(self.notion_label)
        # layout.addWidget(self.notion_input)
        right_layout.addWidget(self.start_button)
        right_layout.addWidget(self.prompt_label)
        self.prompt_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.output_text)
        
        left_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # self.setLayout(layout)
        left_layout.addItem(left_spacer)
        right_layout.addItem(right_spacer)
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        # Set the main layout to the QWidget
        self.setLayout(main_layout)



    def toggle_collapsible_box(self):
        self.collapsible_box.setHidden(not self.collapsible_box.isHidden())

    # def browse_files(self):
    #     file_dialog = QFileDialog()
    #     files, _ = file_dialog.getOpenFileNames(self, "Select log files", "", "Log Files (*.log)")
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
        table_nameP = self.table_nameP_input.text()  # 如果有GUI字段，则替换为相应的
        notion = self.notion_input.text()  # 如果有GUI字段，则替换为相应的
    
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
        # result = data_processor.process_data_from_gui(files, initKeyword, sort, delimiter, table_nameP, notion)
    
        # 将结果显示在GUI的文本区域
        from data_processor import print_by_format, save_to_txt
        # 获取DataCut实例的处理结果
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
