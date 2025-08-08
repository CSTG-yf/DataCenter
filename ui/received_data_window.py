from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from ui.settings_utils import parse_update_interval


class ReceivedDataWindow(QMainWindow):
    """接收信息显示窗口"""
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.is_window_open = False  # 添加窗口状态跟踪
        self.init_ui()
        
        # 更新间隔相关
        self.update_interval_ms = 100  # 默认100ms
        self.pending_update = False  # 是否有待更新的数据
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._perform_update)
        self.update_timer.start(self.update_interval_ms)
        
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
        self.data_buffer = ""  # 数据缓冲区，存储未显示的数据（字符串）
        self.is_paused = False  # 暂停状态
        self.pause_buffer = []  # 暂停时的数据缓冲区
        self.is_disconnected = False  # 断开连接状态
        
        # 循环缓冲区设置
        self.max_display_lines = 10000  # 最大显示行数
        self.max_display_chars = 1000000  # 最大显示字符数
        self.display_lines = []  # 存储显示的行
        self.current_chars = 0  # 当前字符数
        
        # 新增：整合main1.py的缓冲区机制
        self.max_buffer_length = 500000  # 最大缓冲区长度
        self.max_display_length = 200000  # 最大显示长度
        self.parsed_data_buffer = ""  # 解析数据缓冲区
        
        # 新增：滚动轴控制变量
        self.scroll_at_bottom = True  # 是否在底部
        self.scroll_position = 0  # 滚动位置
        
        # 初始化缓冲区状态显示
        self._update_buffer_status()
    
    def append_data(self, data):
        """添加接收数据（优化版本，减少闪烁）"""
        if self.is_disconnected:
            # 如果已断开连接，不处理新数据
            print(f"窗口 {self.port_name} 已断开连接，忽略数据")
            return
            
        # 只有在窗口打开时才处理数据
        if not self.is_window_open:
            # 窗口未打开时，不处理数据
            print(f"窗口 {self.port_name} 未打开，忽略数据")
            return
            
        print(f"窗口 {self.port_name} 接收到数据: {len(data)} 字节")
        
        if self.is_paused:
            # 如果暂停，将数据存储到暂停缓冲区，但不更新显示
            self.pause_buffer.append(data)
            self.receive_count += len(data.encode('utf-8'))
            self.receive_count_label.setText(f"接收字节数: {self.receive_count} (已暂停)")
            return
        
        # 更新数据缓冲区
        self.data_buffer += data
        if len(self.data_buffer) > self.max_buffer_length:
            self.data_buffer = self.data_buffer[-self.max_buffer_length:]
        
        # 将数据按行分割
        lines = data.split('\n')
        
        # 批量添加新行
        new_lines = []
        for line in lines:
            if line:  # 跳过空行
                new_lines.append(line)
                self.current_chars += len(line)
        
        # 批量添加到显示行列表
        if new_lines:
            self.display_lines.extend(new_lines)
            
            # 检查是否需要删除最老的数据
            self._manage_buffer_size()
            
            # 标记有待更新的数据
            self.pending_update = True
            
            print(f"窗口 {self.port_name} 添加了 {len(new_lines)} 行数据，当前缓冲区: {len(self.display_lines)} 行")
        
        self.receive_count += len(data.encode('utf-8'))
        self.receive_count_label.setText(f"接收字节数: {self.receive_count}")
    
    def _perform_update(self):
        """执行定时更新显示"""
        if self.pending_update and not self.is_paused:
            print(f"窗口 {self.port_name} 执行更新显示")
            self._update_display()
            self.pending_update = False
    
    def set_update_interval(self, interval_text):
        """设置更新间隔
        
        Args:
            interval_text (str): 更新间隔设置文本，如 "标准更新 (100ms)"
        """
        new_interval = parse_update_interval(interval_text)
        if new_interval != self.update_interval_ms:
            self.update_interval_ms = new_interval
            self.update_timer.setInterval(new_interval)
            # 如果间隔为0，立即执行一次更新
            if new_interval == 0 and self.pending_update:
                self._perform_update()
    
    def _update_scroll_position(self):
        """更新滚动位置（优化版本，避免闪烁）"""
        if not self.auto_scroll or self.is_paused:
            return
            
        # 记录当前滚动条位置
        scroll_bar = self.text_display.verticalScrollBar()
        if scroll_bar is None:
            return
            
        self.scroll_position = scroll_bar.value()
        self.scroll_at_bottom = (self.scroll_position == scroll_bar.maximum())
        
        # 如果自动滚动开启，则滚动到底部
        if self.auto_scroll:
            try:
                scroll_bar.setUpdatesEnabled(False)
                cursor = self.text_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.text_display.setTextCursor(cursor)
                # 确保滚动条也在底部
                scroll_bar.setValue(scroll_bar.maximum())
            except Exception as e:
                # 如果滚动失败，忽略错误
                print(f"滚动位置更新失败: {e}")
                pass
            finally:
                scroll_bar.setUpdatesEnabled(True)
    
    def _update_buffer_status(self):
        """更新缓冲区状态显示"""
        current_lines = len(self.display_lines)
        max_lines = self.max_display_lines
        self.buffer_status_label.setText(f"缓冲区: {current_lines}/{max_lines} 行")
    
    def _manage_buffer_size(self):
        """管理缓冲区大小，删除最老的数据"""
        # 检查行数限制
        removed_count = 0
        while len(self.display_lines) > self.max_display_lines:
            removed_line = self.display_lines.pop(0)
            self.current_chars -= len(removed_line)
            removed_count += 1
        
        # 检查字符数限制
        while self.current_chars > self.max_display_chars and len(self.display_lines) > 1:
            removed_line = self.display_lines.pop(0)
            self.current_chars -= len(removed_line)
            removed_count += 1
        
        # 更新缓冲区状态显示（无论是否删除了数据）
        self._update_buffer_status()
    
    def _update_display(self):
        """更新显示内容（重新设计，避免闪烁）"""
        # 检查是否需要更新显示
        current_content = self.text_display.toPlainText()
        new_content = '\n'.join(self.display_lines)
        
        # 只有当内容真正改变时才更新
        if current_content != new_content:
            # 记录当前滚动条位置
            scroll_bar = self.text_display.verticalScrollBar()
            at_bottom = scroll_bar.value() == scroll_bar.maximum()
            current_value = scroll_bar.value()
            
            # 使用更稳定的更新方式
            try:
                # 暂时禁用滚动条更新和文本显示更新，避免闪烁
                scroll_bar.setUpdatesEnabled(False)
                self.text_display.setUpdatesEnabled(False)
                
                # 直接设置新内容，避免增量更新
                self.text_display.setPlainText(new_content)
                
                # 恢复滚动条位置
                if self.auto_scroll and not self.is_paused:
                    # 如果自动滚动开启，则滚动到底部
                    scroll_bar.setValue(scroll_bar.maximum())
                    cursor = self.text_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.text_display.setTextCursor(cursor)
                else:
                    # 如果自动滚动关闭，保持原来的位置
                    if at_bottom:
                        scroll_bar.setValue(scroll_bar.maximum())
                    else:
                        scroll_bar.setValue(current_value)
                        
            finally:
                # 重新启用滚动条更新和文本显示更新
                scroll_bar.setUpdatesEnabled(True)
                self.text_display.setUpdatesEnabled(True)
    
    def show_buffered_data(self):
        """显示缓冲区中的数据（窗口重新打开时调用）"""
        # 由于窗口关闭时会清空缓冲区，这个方法主要用于窗口重新打开时的初始化
        # 如果有缓冲数据，则显示
        if self.data_buffer:
            # 将字符串缓冲区按行分割并添加到显示行列表
            lines = self.data_buffer.split('\n')
            new_lines = []
            for line in lines:
                if line:  # 跳过空行
                    new_lines.append(line)
                    self.current_chars += len(line)
            
            # 批量添加到显示行列表
            if new_lines:
                self.display_lines.extend(new_lines)
                
                # 检查是否需要删除最老的数据
                self._manage_buffer_size()
                
                # 标记有待更新的数据
                self.pending_update = True
            
            # 清空缓冲区
            self.data_buffer = ""
        
        # 确保缓冲区状态显示正确
        self._update_buffer_status()
    
    def clear_data(self):
        """清空数据"""
        self.text_display.clear()
        self.receive_count = 0
        self.receive_count_label.setText("接收字节数: 0")
        self.data_buffer = ""  # 同时清空缓冲区
        self.pause_buffer.clear()  # 清空暂停缓冲区
        
        # 清空循环缓冲区
        self.display_lines.clear()
        self.current_chars = 0
        
        # 清空解析数据缓冲区
        self.parsed_data_buffer = ""
        
        # 更新缓冲区状态显示
        self._update_buffer_status()
    
    def toggle_auto_scroll(self):
        """切换自动滚动（优化版本，避免闪烁）"""
        self.auto_scroll = not self.auto_scroll
        
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
            # 如果开启自动滚动，立即滚动到底部
            if not self.is_paused:
                try:
                    scroll_bar = self.text_display.verticalScrollBar()
                    scroll_bar.setUpdatesEnabled(False)
                    scroll_bar.setValue(scroll_bar.maximum())
                    cursor = self.text_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.text_display.setTextCursor(cursor)
                finally:
                    scroll_bar.setUpdatesEnabled(True)
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
            # 如果关闭自动滚动，保持当前滚动位置
            try:
                scroll_bar = self.text_display.verticalScrollBar()
                current_value = scroll_bar.value()
                scroll_bar.setUpdatesEnabled(False)
                scroll_bar.setValue(current_value)
            finally:
                scroll_bar.setUpdatesEnabled(True)
    
    def toggle_pause(self):
        """切换暂停状态（优化版本，避免闪烁）"""
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
                # 批量处理暂停期间的数据
                all_new_lines = []
                for data in self.pause_buffer:
                    lines = data.split('\n')
                    for line in lines:
                        if line:  # 跳过空行
                            all_new_lines.append(line)
                            self.current_chars += len(line)
                
                # 批量添加到显示行列表
                if all_new_lines:
                    self.display_lines.extend(all_new_lines)
                    
                    # 检查是否需要删除最老的数据
                    self._manage_buffer_size()
                    
                    # 更新显示（使用稳定的更新方式，避免闪烁）
                    self._update_display()
                
                # 清空暂停缓冲区
                self.pause_buffer.clear()
            
            # 恢复时立即执行一次更新
            if self.pending_update:
                self._perform_update()
    
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
        self.is_window_open = True
        
        # 重新启动定时器
        if not self.update_timer.isActive():
            self.update_timer.start(self.update_interval_ms)
        
        # 显示缓冲的数据（如果有的话）
        self.show_buffered_data()
        
        # 确保缓冲区状态显示正确
        self._update_buffer_status()
        
        # 打印调试信息
        print(f"窗口 {self.port_name} 已打开，is_window_open = {self.is_window_open}")
        
        event.accept()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止定时器
        self.update_timer.stop()
        
        # 设置窗口关闭状态
        self.is_window_open = False
        
        # 清空显示内容
        self.text_display.clear()
        
        # 清空所有缓冲区
        self.data_buffer = ""
        self.pause_buffer.clear()
        self.display_lines.clear()
        self.current_chars = 0
        self.parsed_data_buffer = ""
        
        # 重置状态
        self.is_paused = False
        self.is_disconnected = False
        self.pending_update = False
        
        # 重置接收计数
        self.receive_count = 0
        self.receive_count_label.setText("接收字节数: 0")
        
        # 更新缓冲区状态显示
        self._update_buffer_status()
        
        event.accept() 