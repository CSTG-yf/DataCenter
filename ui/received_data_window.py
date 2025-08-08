from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor


class ReceivedDataWindow(QMainWindow):
    """接收信息显示窗口"""
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"串口 {self.port_name} - 接收信息")
        self.setGeometry(200, 200, 800, 600)
        
        # 连接窗口显示事件
        self.showEvent = self.on_show_event
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f"串口 {self.port_name} 接收信息")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 控制按钮
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        self.pause_btn.clicked.connect(self.toggle_pause)
        title_layout.addWidget(self.pause_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
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
        self.clear_btn.clicked.connect(self.clear_data)
        title_layout.addWidget(self.clear_btn)
        
        layout.addLayout(title_layout)
        
        # 接收数据显示区域
        data_frame = QFrame()
        data_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(15, 15, 15, 15)
        
        # 数据显示文本框
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333333;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        data_layout.addWidget(self.text_display)
        
        layout.addWidget(data_frame)
        
        # 统计信息区域
        stats_layout = QHBoxLayout()
        
        self.receive_count_label = QLabel("接收字节数: 0")
        self.receive_count_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background-color: transparent;
                border: none;
            }
        """)
        stats_layout.addWidget(self.receive_count_label)
        
        # 添加缓冲区状态显示
        self.buffer_status_label = QLabel("缓冲区: 0/10000 行")
        self.buffer_status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background-color: transparent;
                border: none;
            }
        """)
        stats_layout.addWidget(self.buffer_status_label)
        
        stats_layout.addStretch()
        
        # 自动滚动按钮
        self.auto_scroll_btn = QPushButton("自动滚动: 开启")
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        stats_layout.addWidget(self.auto_scroll_btn)
        
        layout.addLayout(stats_layout)
        
        # 初始化数据
        self.receive_count = 0
        self.auto_scroll = True
        self.data_buffer = []  # 数据缓冲区，存储未显示的数据
        self.is_paused = False  # 暂停状态
        self.pause_buffer = []  # 暂停时的数据缓冲区
        self.is_disconnected = False  # 断开连接状态
        
        # 循环缓冲区设置
        self.max_display_lines = 10000  # 最大显示行数
        self.max_display_chars = 1000000  # 最大显示字符数
        self.display_lines = []  # 存储显示的行
        self.current_chars = 0  # 当前字符数
    
    def append_data(self, data):
        """添加接收数据"""
        if self.is_disconnected:
            # 如果已断开连接，不处理新数据
            return
            
        if self.is_paused:
            # 如果暂停，将数据存储到暂停缓冲区
            self.pause_buffer.append(data)
            self.receive_count += len(data.encode('utf-8'))
            self.receive_count_label.setText(f"接收字节数: {self.receive_count} (已暂停)")
            return
        
        # 将数据按行分割
        lines = data.split('\n')
        
        for line in lines:
            if line:  # 跳过空行
                # 添加到显示行列表
                self.display_lines.append(line)
                self.current_chars += len(line)
                
                # 检查是否需要删除最老的数据
                self._manage_buffer_size()
        
        # 更新显示
        self._update_display()
        
        self.receive_count += len(data.encode('utf-8'))
        self.receive_count_label.setText(f"接收字节数: {self.receive_count}")
        
        # 只有在非暂停状态且启用自动滚动时才滚动到底部
        if self.auto_scroll and not self.is_paused:
            cursor = self.text_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_display.setTextCursor(cursor)
    
    def _update_buffer_status(self):
        """更新缓冲区状态显示"""
        current_lines = len(self.display_lines)
        max_lines = self.max_display_lines
        self.buffer_status_label.setText(f"缓冲区: {current_lines}/{max_lines} 行")
    
    def _manage_buffer_size(self):
        """管理缓冲区大小，删除最老的数据"""
        # 检查行数限制
        while len(self.display_lines) > self.max_display_lines:
            removed_line = self.display_lines.pop(0)
            self.current_chars -= len(removed_line)
        
        # 检查字符数限制
        while self.current_chars > self.max_display_chars and len(self.display_lines) > 1:
            removed_line = self.display_lines.pop(0)
            self.current_chars -= len(removed_line)
        
        # 更新缓冲区状态显示
        self._update_buffer_status()
    
    def _update_display(self):
        """更新显示内容"""
        # 检查是否需要更新显示
        current_content = self.text_display.toPlainText()
        new_content = '\n'.join(self.display_lines)
        
        # 只有当内容真正改变时才更新
        if current_content != new_content:
            # 清空当前显示
            self.text_display.clear()
            
            # 重新构建显示内容
            if self.display_lines:
                self.text_display.setPlainText(new_content)
    
    def add_to_buffer(self, data):
        """添加数据到缓冲区（窗口未打开时）"""
        # 将数据按行分割并添加到缓冲区
        lines = data.split('\n')
        for line in lines:
            if line:  # 跳过空行
                self.data_buffer.append(line)
        
        self.receive_count += len(data.encode('utf-8'))
    
    def show_buffered_data(self):
        """显示缓冲区中的数据"""
        if self.data_buffer:
            for line in self.data_buffer:
                # 添加到显示行列表
                self.display_lines.append(line)
                self.current_chars += len(line)
                
                # 检查是否需要删除最老的数据
                self._manage_buffer_size()
            
            # 更新显示
            self._update_display()
            
            # 只有在非暂停状态且启用自动滚动时才滚动到底部
            if self.auto_scroll and not self.is_paused:
                cursor = self.text_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.text_display.setTextCursor(cursor)
            
            # 清空缓冲区
            self.data_buffer.clear()
    
    def clear_data(self):
        """清空数据"""
        self.text_display.clear()
        self.receive_count = 0
        self.receive_count_label.setText("接收字节数: 0")
        self.data_buffer.clear()  # 同时清空缓冲区
        self.pause_buffer.clear()  # 清空暂停缓冲区
        
        # 清空循环缓冲区
        self.display_lines.clear()
        self.current_chars = 0
        
        # 更新缓冲区状态显示
        self._update_buffer_status()
    
    def toggle_auto_scroll(self):
        """切换自动滚动"""
        self.auto_scroll = not self.auto_scroll
        status = "开启" if self.auto_scroll else "关闭"
        
        if self.auto_scroll:
            # 开启状态
            self.auto_scroll_btn.setText("自动滚动: 开启")
            self.auto_scroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e7e34;
                }
            """)
        else:
            # 关闭状态
            self.auto_scroll_btn.setText("自动滚动: 关闭")
            self.auto_scroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
    
    def toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # 暂停状态
            self.pause_btn.setText("恢复")
            self.pause_btn.setStyleSheet("""
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
            self.receive_count_label.setText(f"接收字节数: {self.receive_count} (已暂停)")
        else:
            # 恢复状态
            self.pause_btn.setText("暂停")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: #212529;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
                QPushButton:pressed {
                    background-color: #d39e00;
                }
            """)
            self.receive_count_label.setText(f"接收字节数: {self.receive_count}")
            
            # 恢复时显示暂停期间的数据
            if self.pause_buffer:
                for data in self.pause_buffer:
                    # 将数据按行分割
                    lines = data.split('\n')
                    for line in lines:
                        if line:  # 跳过空行
                            # 添加到显示行列表
                            self.display_lines.append(line)
                            self.current_chars += len(line)
                            
                            # 检查是否需要删除最老的数据
                            self._manage_buffer_size()
                
                # 更新显示
                self._update_display()
                
                # 只有在启用自动滚动时才滚动到底部
                if self.auto_scroll:
                    cursor = self.text_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.text_display.setTextCursor(cursor)
                
                self.pause_buffer.clear()
    
    def get_data(self):
        """获取当前数据"""
        return self.text_display.toPlainText()
    
    def set_data(self, data):
        """设置数据"""
        self.text_display.setPlainText(data)
        self.receive_count = len(data.encode('utf-8'))
        self.receive_count_label.setText(f"接收字节数: {self.receive_count}")
    
    def set_disconnected(self, disconnected=True):
        """设置断开连接状态"""
        self.is_disconnected = disconnected
        if disconnected:
            self.receive_count_label.setText(f"接收字节数: {self.receive_count} (已断开)")
            # 禁用暂停按钮
            if hasattr(self, 'pause_btn'):
                self.pause_btn.setEnabled(False)
        else:
            self.receive_count_label.setText(f"接收字节数: {self.receive_count}")
            # 启用暂停按钮
            if hasattr(self, 'pause_btn'):
                self.pause_btn.setEnabled(True)
    
    def on_show_event(self, event):
        """窗口显示事件"""
        # 显示缓冲的数据
        self.show_buffered_data()
        event.accept()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 清理资源
        self.is_paused = False
        self.is_disconnected = False
        event.accept() 