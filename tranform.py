import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLineEdit, QLabel, QComboBox, QTextEdit,
                             QCheckBox, QSplitter, QStyleFactory)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UFP 日志裁剪工具')
        self.setWindowIcon(QIcon('app_icon.png'))
        self.setGeometry(700, 300, 800, 600)
        self.center()

        # 配置文件
        self.logs_path = './datalab/'

        # 创建主布局
        main_layout = QHBoxLayout()

        # 创建左侧选项区域
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 文件选择
        files_layout = QHBoxLayout()
        files_label = QLabel('文件选择:')
        files_input = QLineEdit('./datalab/ldp.log')
        browse_button = QPushButton('浏览')
        browse_button.setIcon(QIcon('folder.png'))
        files_layout.addWidget(files_label)
        files_layout.addWidget(files_input)
        files_layout.addWidget(browse_button)

        # 关键词输入
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel('初始化关键词:')
        keyword_input = QLineEdit('vpnnh, key:7')
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(keyword_input)

        # 排序选项
        sort_input = QCheckBox('按时间排序')

        # 分割符输入
        delimiter_layout = QHBoxLayout()
        delimiter_label = QLabel('日志分割符:')
        delimiter_input = QLineEdit('-----------------end------------------')
        delimiter_layout.addWidget(delimiter_label)
        delimiter_layout.addWidget(delimiter_input)

        # 表头名输入
        table_name_layout = QHBoxLayout()
        table_nameP_label = QLabel('表头名:')
        table_nameP_input = QLineEdit('HwTblID')
        table_name_layout.addWidget(table_nameP_label)
        table_name_layout.addWidget(table_nameP_input)

        # 标识符输入
        notion_layout = QHBoxLayout()
        notion_label = QLabel('标识符:')
        notion_input = QLineEdit(':')
        notion_layout.addWidget(notion_label)
        notion_layout.addWidget(notion_input)

        # 创建按钮
        start_button = QPushButton('开始处理')
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        download_button = QPushButton('另存为')
        download_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        # 添加组件到左侧布局
        left_layout.addLayout(files_layout)
        left_layout.addLayout(keyword_layout)
        left_layout.addWidget(sort_input)
        left_layout.addLayout(delimiter_layout)
        left_layout.addLayout(table_name_layout)
        left_layout.addLayout(notion_layout)
        left_layout.addStretch()
        left_layout.addWidget(start_button)
        left_layout.addWidget(download_button)

        left_widget.setLayout(left_layout)

        # 创建右侧输出区域
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 工具选择
        tools_layout = QHBoxLayout()
        tools_label = QLabel('选择工具:')
        self.combo = QComboBox()
        for tool in self.find_tools():
            self.combo.addItem(tool)
        run_tools_button = QPushButton('运行工具')
        run_tools_button.setIcon(QIcon('run.png'))
        tools_layout.addWidget(tools_label)
        tools_layout.addWidget(self.combo)
        tools_layout.addWidget(run_tools_button)

        # 删除旧日志按钮
        delete_old_logs_button = QPushButton('删除旧日志数据')
        delete_old_logs_button.setIcon(QIcon('delete.png'))

        # 输出区域
        output_text = QTextEdit()
        output_text.setReadOnly(True)
        output_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        right_layout.addLayout(tools_layout)
        right_layout.addWidget(delete_old_logs_button)
        right_layout.addWidget(output_text)

        right_widget.setLayout(right_layout)

        # 将左右两个组件添加到主布局中
        main_layout.addWidget(left_widget)
        main_layout.addWidget(QSplitter())  # 添加一个分割线
        main_layout.addWidget(right_widget)

        # 设置主布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QGroupBox {
                font-weight: bold;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)

    