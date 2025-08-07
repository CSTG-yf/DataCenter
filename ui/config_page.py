from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel, QComboBox, QPushButton, QFrame,
                             QCheckBox, QLineEdit, QDialog, QMessageBox, QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import serial.tools.list_ports

# 导入新创建的组件
from .serial_info_widget import SerialInfoWidget
from .received_data_window import ReceivedDataWindow
from .send_data_window import SendDataWindow


class SerialConnectionDialog(QDialog):
    """串口连接对话框"""
    
    connection_requested = pyqtSignal(dict)  # 连接请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接新串口")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 移除重复的标题，因为窗口标题栏已经显示了
        # 直接开始串口配置部分
        
        # 串口选择
        port_layout = QHBoxLayout()
        port_label = QLabel("串口:")
        port_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                min-width: 60px;
                background-color: transparent;
                border: none;
            }
        """)
        port_layout.addWidget(port_label)
        
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
            }
        """)
        port_layout.addWidget(self.port_combo)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 波特率选择
        baud_layout = QHBoxLayout()
        baud_label = QLabel("波特率:")
        baud_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                min-width: 60px;
                background-color: transparent;
                border: none;
            }
        """)
        baud_layout.addWidget(baud_label)
        
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'])
        self.baud_combo.setCurrentText('115200')
        self.baud_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
            }
        """)
        baud_layout.addWidget(self.baud_combo)
        baud_layout.addStretch()
        layout.addLayout(baud_layout)
        
        # 刷新按钮（放在最底下）
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                color: #495057;
                border: 2px solid #6c757d;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border: 2px solid #495057;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #dee2e6, stop:1 #ced4da);
                border: 3px solid #343a40;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.connect_serial)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #198754, stop:1 #157347);
                color: white;
                border: 2px solid #146c43;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #157347, stop:1 #0f5132);
                border: 2px solid #0f5132;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0f5132, stop:1 #0d4529);
                border: 3px solid #0a3622;
            }
        """)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_ports(self):
        """刷新串口列表"""
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
    
    def connect_serial(self):
        """连接串口"""
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "警告", "请选择串口")
            return
            
        config = {
            'port': port,
            'baudrate': int(self.baud_combo.currentText())
        }
        self.connection_requested.emit(config)
        self.accept()


class ConfigPage(QWidget):
    """串口配置页面 - 重新设计为Data sources面板"""
    
    # 定义信号
    connect_signal = pyqtSignal(dict)  # 连接信号
    disconnect_signal = pyqtSignal()   # 断开连接信号
    refresh_ports_signal = pyqtSignal()  # 刷新串口信号
    view_received_signal = pyqtSignal(str)  # 查看接收信息信号
    send_data_signal = pyqtSignal(str, str, bool, bool, int)  # 发送数据信号
    delete_serial_signal = pyqtSignal(str)  # 删除串口信号
    
    def __init__(self):
        super().__init__()
        self.serial_widgets = {}  # 存储串口信息组件
        self.received_windows = {}  # 存储接收信息窗口
        self.send_windows = {}  # 存储发送数据窗口
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面 - 优化后的设计"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # 创建滚动区域的内容部件
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        
        # 直接创建内容区域（移除独立的标题栏）
        self.create_content_area(self.scroll_layout)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
    def create_content_area(self, parent_layout):
        """创建内容区域 - 优化后的设计"""
        # 提示文本
        self.hint_label = QLabel("您还没有添加任何数据源。")
        self.hint_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333333;
                text-align: center;
                background-color: transparent;
                border: none;
                padding: 20px 0;
            }
        """)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.action_label = QLabel("点击标题栏上方的 <b>+</b> 按钮添加数据源。")
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                text-align: center;
                background-color: transparent;
                border: none;
                padding: 15px 0;
            }
        """)
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(self.hint_label)
        parent_layout.addWidget(self.action_label)
        parent_layout.addStretch()
    
    def show_connection_dialog(self):
        """显示串口连接对话框"""
        dialog = SerialConnectionDialog(self)
        dialog.connection_requested.connect(self.handle_connection_request)
        dialog.exec()
    
    def handle_connection_request(self, config):
        """处理连接请求"""
        port_name = config['port']
        
        # 检查是否已经存在该串口
        if port_name in self.serial_widgets:
            QMessageBox.warning(self, "警告", f"串口 {port_name} 已经存在！")
            return
        
        # 创建串口信息组件
        serial_widget = SerialInfoWidget(port_name)
        serial_widget.view_received_signal.connect(self.view_received_data)
        serial_widget.send_data_signal.connect(self.open_send_dialog)
        serial_widget.delete_serial_signal.connect(self.handle_delete_serial)
        
        # 添加到布局中
        self.scroll_layout.insertWidget(len(self.serial_widgets), serial_widget)
        self.serial_widgets[port_name] = serial_widget
        
        # 隐藏提示文本
        self.hint_label.hide()
        self.action_label.hide()
        
        # 发送连接信号
        self.connect_signal.emit(config)
        
        # 更新界面显示
        self.update_connection_status(True, port_name)
    
    def view_received_data(self, port_name):
        """查看接收信息"""
        if port_name not in self.received_windows:
            # 创建新的接收信息窗口
            window = ReceivedDataWindow(port_name, self)
            self.received_windows[port_name] = window
        
        window = self.received_windows[port_name]
        
        # 显示窗口（会自动显示缓冲区中的数据）
        window.show()
        window.raise_()
        window.activateWindow()
    
    def open_send_dialog(self, port_name):
        """打开发送数据对话框"""
        if port_name not in self.send_windows:
            # 创建新的发送数据窗口
            window = SendDataWindow(port_name, self)
            window.send_data_signal.connect(self.handle_send_data)
            self.send_windows[port_name] = window
        else:
            window = self.send_windows[port_name]
        
        window.show()
        window.raise_()
        window.activateWindow()
    
    def handle_send_data(self, port_name, data, hex_mode, auto_mode, interval):
        """处理发送数据"""
        self.send_data_signal.emit(port_name, data, hex_mode, auto_mode, interval)
    
    def handle_delete_serial(self, port_name):
        """处理删除串口"""
        # 发送删除串口信号
        self.delete_serial_signal.emit(port_name)
        
        # 移除串口组件
        self.remove_serial_widget(port_name)
    
    def append_received_data(self, port_name, data):
        """添加接收数据到指定串口"""
        if port_name in self.received_windows:
            # 如果窗口已打开，直接显示数据
            self.received_windows[port_name].append_data(data)
        else:
            # 如果窗口未打开，创建窗口但不显示，只存储数据
            window = ReceivedDataWindow(port_name, self)
            window.add_to_buffer(data)  # 添加到缓冲区
            self.received_windows[port_name] = window
            # 不调用show()，窗口保持隐藏状态
    
    def remove_serial_widget(self, port_name):
        """移除串口组件"""
        if port_name in self.serial_widgets:
            # 移除组件
            widget = self.serial_widgets[port_name]
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()
            del self.serial_widgets[port_name]
            
            # 关闭相关窗口
            if port_name in self.received_windows:
                self.received_windows[port_name].close()
                del self.received_windows[port_name]
            
            if port_name in self.send_windows:
                self.send_windows[port_name].close()
                del self.send_windows[port_name]
            
            # 如果没有串口了，显示提示文本
            if not self.serial_widgets:
                self.hint_label.show()
                self.action_label.show()
    
    def show_settings(self):
        """显示设置"""
        QMessageBox.information(self, "设置", "串口设置功能")
    
    def close_panel(self):
        """关闭面板 - 此方法不再需要，功能已移到主窗口"""
        pass
    
    def update_connection_status(self, connected, port_name=None):
        """更新连接状态"""
        if port_name and port_name in self.serial_widgets:
            self.serial_widgets[port_name].update_status(connected)
    
    def update_port_list(self, ports):
        """更新串口列表 - 保留接口兼容性"""
        pass 