from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGroupBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class SerialInfoWidget(QWidget):
    """单个串口信息组件"""
    
    # 定义信号
    view_received_signal = pyqtSignal(str)  # 查看接收信息信号
    send_data_signal = pyqtSignal(str)      # 发送数据信号
    delete_serial_signal = pyqtSignal(str)  # 删除串口信号
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 创建串口信息组框
        group_box = QGroupBox(f"串口: {self.port_name}")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
        """)
        
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(10)
        
        # 串口状态信息
        status_layout = QHBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("状态: 已连接")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #28a745;
                background-color: transparent;
                border: none;
            }
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        group_layout.addLayout(status_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 查看接收信息按钮
        self.view_btn = QPushButton("查看接收信息")
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.view_btn.clicked.connect(self.view_received_data)
        button_layout.addWidget(self.view_btn)
        
        # 发送数据按钮
        self.send_btn = QPushButton("发送数据")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
        """)
        self.send_btn.clicked.connect(self.open_send_dialog)
        button_layout.addWidget(self.send_btn)
        
        # 删除串口按钮
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_serial)
        button_layout.addWidget(self.delete_btn)
        
        group_layout.addLayout(button_layout)
        
        layout.addWidget(group_box)
        
    def view_received_data(self):
        """查看接收信息"""
        self.view_received_signal.emit(self.port_name)
        
    def open_send_dialog(self):
        """打开发送数据对话框"""
        self.send_data_signal.emit(self.port_name)
    
    def delete_serial(self):
        """删除串口"""
        self.delete_serial_signal.emit(self.port_name)
        
    def update_status(self, connected):
        """更新连接状态"""
        if connected:
            self.status_label.setText("状态: 已连接")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #28a745;
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.status_label.setText("状态: 未连接")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #dc3545;
                    background-color: transparent;
                    border: none;
                }
            """) 