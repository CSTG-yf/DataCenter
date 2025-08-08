import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QFrame, QStackedWidget, QToolButton, QApplication,
                             QScrollArea, QLabel, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

# 导入页面模块
from .config_page import ConfigPage
from .data_page import DataPage
from .history_page import HistoryPage
from .settings_page import SettingsPage


class RightSideMenu(QWidget):
    """右侧弹出菜单组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.current_page = None
        self.is_visible = False
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedWidth(450)  # 增加宽度以确保内容完全显示
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-left: 3px solid #495057;
                border-right: 2px solid #6c757d;
                border-top: 2px solid #6c757d;
            }
            QLineEdit, QTextEdit {
                border: none;
                background-color: transparent;
                padding: 8px 12px;
            }
        """)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标题栏
        self.create_title_bar(layout)
        
        # 创建内容区域
        self.create_content_area(layout)
        
        # 创建各个页面
        self.pages = {}
        self.pages['config'] = ConfigPage()
        self.pages['data'] = DataPage()
        self.pages['history'] = HistoryPage()
        self.pages['settings'] = SettingsPage()
        
        # 默认隐藏
        self.hide()
        
    def create_title_bar(self, parent_layout):
        """创建标题栏"""
        title_frame = QFrame()
        title_frame.setFixedHeight(48)  # 稍微增加高度
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 3px solid #495057;
                border-top: 2px solid #6c757d;
            }
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(12, 0, 12, 0)  # 减小边距
        
        self.title_label = QLabel("菜单")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        
        # 按钮区域（仅在config页面显示）
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(8)
        
        # + 按钮
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #6c757d;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 18px;
                font-weight: bold;
                color: #495057;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                border: 2px solid #0d6efd;
                color: #0d6efd;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #bbdefb, stop:1 #90caf9);
                border: 3px solid #0b5ed7;
                color: #0b5ed7;
            }
        """)
        self.add_btn.hide()  # 默认隐藏
        
        # 设置按钮
        self.settings_btn = QPushButton("📁")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #6c757d;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 16px;
                color: #495057;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fff3cd, stop:1 #ffeaa7);
                border: 2px solid #ffc107;
                color: #b8860b;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffeaa7, stop:1 #fdcb6e);
                border: 3px solid #e0a800;
                color: #b8860b;
            }
        """)
        self.settings_btn.hide()  # 默认隐藏
        
        # X 按钮
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(32, 32)
        self.close_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #6c757d;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 18px;
                font-weight: bold;
                color: #495057;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8d7da, stop:1 #f5c2c7);
                border: 2px solid #dc3545;
                color: #dc3545;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f5c2c7, stop:1 #ea868f);
                border: 3px solid #b02a37;
                color: #b02a37;
            }
        """)
        self.close_button.clicked.connect(self.hide_menu)
        
        self.button_layout.addWidget(self.add_btn)
        self.button_layout.addWidget(self.settings_btn)
        self.button_layout.addWidget(self.close_button)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addLayout(self.button_layout)
        
        parent_layout.addWidget(title_frame)
        
    def create_content_area(self, parent_layout):
        """创建内容区域"""
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距以确保内容不被截断
        
        self.content_area.setWidget(self.content_widget)
        parent_layout.addWidget(self.content_area)
        
    def show_page(self, page_name, page_title):
        """显示指定页面"""
        if page_name in self.pages:
            # 清除当前内容
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            
            # 添加新页面
            self.content_layout.addWidget(self.pages[page_name])
            self.current_page = page_name
            self.title_label.setText(page_title)
            
            # 根据页面类型显示/隐藏按钮
            if page_name == 'config':
                self.add_btn.show()
                self.settings_btn.show()
                # 连接config页面的信号到标题栏按钮
                self.add_btn.clicked.connect(self.pages[page_name].show_connection_dialog)
                self.settings_btn.clicked.connect(self.open_serial_logs_folder)
            else:
                self.add_btn.hide()
                self.settings_btn.hide()
                # 断开之前的连接
                try:
                    self.add_btn.clicked.disconnect()
                    self.settings_btn.clicked.disconnect()
                except TypeError:
                    pass  # 如果没有连接就忽略
            
            # 显示菜单
            self.show()
            self.is_visible = True
            
    def hide_menu(self):
        """隐藏菜单"""
        self.hide()
        self.is_visible = False
        
    def get_current_page(self):
        """获取当前页面"""
        return self.current_page
        
    def get_page(self, page_name):
        """获取指定页面"""
        return self.pages.get(page_name)
    
    def open_serial_logs_folder(self):
        """打开serial_logs文件夹"""
        import os
        import subprocess
        import platform
        
        try:
            # 获取软件根目录（main.py所在目录）
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 构建serial_logs文件夹路径
            serial_logs_dir = os.path.join(current_dir, 'serial_logs')
            
            # 如果文件夹不存在，创建它
            if not os.path.exists(serial_logs_dir):
                os.makedirs(serial_logs_dir)
                print(f"已创建serial_logs文件夹: {serial_logs_dir}")
            
            # 根据操作系统打开文件夹
            if platform.system() == "Windows":
                # 在Windows中，使用os.startfile来打开文件夹
                os.startfile(serial_logs_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', serial_logs_dir], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', serial_logs_dir], check=True)
                
            print(f"已打开serial_logs文件夹: {serial_logs_dir}")
            
        except Exception as e:
            print(f"打开serial_logs文件夹失败: {str(e)}")
            # 可以在这里添加错误提示对话框
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"打开serial_logs文件夹失败: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口类，负责UI界面的显示和用户交互"""
    
    # 定义信号
    connect_signal = pyqtSignal(dict)  # 连接信号
    disconnect_signal = pyqtSignal()   # 断开连接信号
    send_data_signal = pyqtSignal(str) # 发送数据信号
    clear_signal = pyqtSignal()        # 清空信号
    refresh_ports_signal = pyqtSignal() # 刷新串口信号
    clear_history_signal = pyqtSignal() # 清空历史记录信号
    save_history_signal = pyqtSignal()  # 保存历史记录信号
    settings_changed_signal = pyqtSignal(dict) # 设置变更信号
    reset_settings_signal = pyqtSignal() # 重置设置信号
    view_received_signal = pyqtSignal(str)  # 查看接收信息信号
    send_data_to_port_signal = pyqtSignal(str, str, bool, bool, int)  # 向指定串口发送数据信号
    delete_serial_signal = pyqtSignal(str)  # 删除串口信号
    disconnect_serial_signal = pyqtSignal(str)  # 断开指定串口连接信号
    connect_serial_signal = pyqtSignal(str)  # 连接指定串口信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("串口通信工具")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧区域（包含菜单栏和右侧菜单）
        left_area = self.create_left_area()
        main_layout.addWidget(left_area)
        
        # 创建主内容区域（始终显示数据页面）
        self.main_content = self.create_main_content()
        main_layout.addWidget(self.main_content)
        
        # 设置布局比例
        main_layout.setStretch(0, 0)  # 左侧区域不拉伸
        main_layout.setStretch(1, 1)  # 主内容区域拉伸
        
        # 添加快捷键
        self.setup_shortcuts()
        
        # 设置窗口最大化显示（在所有UI组件创建完成后）
        self.show()
        # 使用QTimer延迟设置最大化状态，确保窗口完全显示后再最大化
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.showMaximized)
    
    def center_window(self):
        """将窗口移动到屏幕中央"""
        # 获取屏幕几何信息
        screen = QApplication.primaryScreen().geometry()
        # 获取窗口几何信息
        window_geometry = self.geometry()
        # 计算居中位置
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        # 移动窗口到中央位置
        self.move(x, y)
        
    def create_left_area(self):
        """创建左侧区域（包含菜单栏和右侧菜单）"""
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 创建左侧菜单栏
        left_menu = self.create_left_menu()
        left_layout.addWidget(left_menu)
        
        # 创建右侧弹出菜单
        self.right_menu = RightSideMenu(self)
        left_layout.addWidget(self.right_menu)
        
        # 设置布局比例
        left_layout.setStretch(0, 0)  # 左侧菜单不拉伸
        left_layout.setStretch(1, 0)  # 右侧菜单不拉伸
        
        return left_widget
    
    def create_left_menu(self):
        """创建左侧菜单栏"""
        menu_frame = QFrame()
        menu_frame.setFixedWidth(80)
        menu_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-right: 3px solid #495057;
                border-top: 2px solid #6c757d;
            }
        """)
        
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(8, 15, 8, 15)
        menu_layout.setSpacing(8)
        
        # 创建菜单按钮
        self.menu_buttons = {}
        
        # 数据源菜单
        self.menu_buttons['config'] = self.create_menu_button("数据源", "🔌")
        self.menu_buttons['config'].clicked.connect(lambda: self.toggle_right_menu('config', 'Data sources'))
        menu_layout.addWidget(self.menu_buttons['config'])
        
        # 数据收发菜单
        self.menu_buttons['data'] = self.create_menu_button("收发", "📡")
        self.menu_buttons['data'].clicked.connect(lambda: self.toggle_right_menu('data', '数据收发'))
        menu_layout.addWidget(self.menu_buttons['data'])
        
        # 历史记录菜单
        self.menu_buttons['history'] = self.create_menu_button("历史", "📋")
        self.menu_buttons['history'].clicked.connect(lambda: self.toggle_right_menu('history', '历史记录'))
        menu_layout.addWidget(self.menu_buttons['history'])
        
        # 设置菜单
        self.menu_buttons['settings'] = self.create_menu_button("设置", "🔧")
        self.menu_buttons['settings'].clicked.connect(lambda: self.toggle_right_menu('settings', '系统设置'))
        menu_layout.addWidget(self.menu_buttons['settings'])
        
        # 添加弹性空间
        menu_layout.addStretch()
        
        return menu_frame
    
    def create_main_content(self):
        """创建主内容区域（显示空白背景）"""
        # 创建空白的主内容区域
        self.main_content_widget = QWidget()
        self.main_content_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #6c757d;
                border-left: none;
            }
        """)
        
        # 创建主数据页面（用于功能，但不显示在主界面）
        self.main_data_page = DataPage()
        
        return self.main_content_widget
    
    def toggle_right_menu(self, page_name, page_title):
        """切换右侧菜单显示"""
        current_page = self.right_menu.get_current_page()
        
        if self.right_menu.is_visible and current_page == page_name:
            # 如果当前菜单已显示且是同一个页面，则隐藏
            self.right_menu.hide_menu()
            self.update_menu_button_states(None)
        else:
            # 显示指定页面
            self.right_menu.show_page(page_name, page_title)
            self.update_menu_button_states(page_name)
    
    def update_menu_button_states(self, active_page):
        """更新菜单按钮状态"""
        for name, button in self.menu_buttons.items():
            if name == active_page:
                button.setStyleSheet("""
                    QToolButton {
                        border: 3px solid #0d6efd;
                        border-radius: 10px;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #0d6efd, stop:1 #0b5ed7);
                        color: white;
                        font-size: 12px;
                        font-weight: 600;
                        padding: 8px 4px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QToolButton {
                        border: 2px solid transparent;
                        border-radius: 10px;
                        background-color: transparent;
                        font-size: 12px;
                        color: #495057;
                        font-weight: 500;
                        padding: 8px 4px;
                    }
                    QToolButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #ffffff, stop:1 #f8f9fa);
                        border: 2px solid #6c757d;
                        color: #212529;
                    }
                    QToolButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #e9ecef, stop:1 #dee2e6);
                        border: 3px solid #495057;
                    }
                """)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # ESC键退出全屏
        exit_fullscreen_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        exit_fullscreen_shortcut.activated.connect(self.exit_fullscreen)
        
        # F11键切换全屏
        toggle_fullscreen_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        toggle_fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
    
    def exit_fullscreen(self):
        """退出全屏模式"""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showNormal()
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()
    
    def create_menu_button(self, text, icon_text):
        """创建菜单按钮"""
        button = QToolButton()
        button.setText(f"{icon_text}\n{text}")
        button.setFixedSize(70, 80)
        button.setStyleSheet("""
            QToolButton {
                border: 2px solid transparent;
                border-radius: 10px;
                background-color: transparent;
                font-size: 12px;
                color: #495057;
                font-weight: 500;
                padding: 8px 4px;
            }
            QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #6c757d;
                color: #212529;
            }
            QToolButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border: 3px solid #495057;
            }
        """)
        return button
    
    def connect_signals(self):
        """连接页面信号"""
        # 主数据页面信号（虽然不显示在主界面，但仍需要处理信号）
        self.main_data_page.send_data_signal.connect(self.send_data_signal.emit)
        self.main_data_page.clear_signal.connect(self.clear_signal.emit)
        
        # 右侧菜单页面信号
        right_pages = self.right_menu.pages
        
        # 配置页面信号
        right_pages['config'].connect_signal.connect(self.connect_signal.emit)
        right_pages['config'].disconnect_signal.connect(self.disconnect_signal.emit)
        right_pages['config'].refresh_ports_signal.connect(self.refresh_ports_signal.emit)
        right_pages['config'].view_received_signal.connect(self.view_received_signal.emit)
        right_pages['config'].send_data_signal.connect(self.send_data_to_port_signal.emit)
        right_pages['config'].delete_serial_signal.connect(self.delete_serial_signal.emit)
        right_pages['config'].disconnect_serial_signal.connect(self.disconnect_serial_signal.emit)
        right_pages['config'].connect_serial_signal.connect(self.connect_serial_signal.emit)
        
        # 数据页面信号（右侧菜单中的）
        right_pages['data'].send_data_signal.connect(self.send_data_signal.emit)
        right_pages['data'].clear_signal.connect(self.clear_signal.emit)
        
        # 历史记录页面信号
        right_pages['history'].clear_history_signal.connect(self.clear_history_signal.emit)
        right_pages['history'].save_history_signal.connect(self.save_history_signal.emit)
        
        # 设置页面信号
        right_pages['settings'].settings_changed_signal.connect(self.settings_changed_signal.emit)
        right_pages['settings'].reset_settings_signal.connect(self.reset_settings_signal.emit)
    
    # 公共接口方法，用于外部调用
    def update_connection_status(self, connected):
        """更新连接状态（兼容旧接口）"""
        self.main_data_page.update_connection_status(connected)
        # 同时更新右侧菜单中的页面
        right_pages = self.right_menu.pages
        right_pages['data'].update_connection_status(connected)
    
    def update_port_list(self, ports):
        """更新串口列表"""
        right_pages = self.right_menu.pages
        right_pages['config'].update_port_list(ports)
    
    def append_receive_data(self, data):
        """添加接收数据到显示区域"""
        self.main_data_page.append_receive_data(data)
        # 同时更新右侧菜单中的数据页面
        right_pages = self.right_menu.pages
        right_pages['data'].append_receive_data(data)
    
    def update_statistics(self, receive_count, send_count):
        """更新统计信息"""
        self.main_data_page.update_statistics(receive_count, send_count)
        # 同时更新右侧菜单中的数据页面
        right_pages = self.right_menu.pages
        right_pages['data'].update_statistics(receive_count, send_count)
    
    def append_history(self, text):
        """添加历史记录"""
        right_pages = self.right_menu.pages
        right_pages['history'].append_history(text)
    
    def set_history_content(self, content):
        """设置历史记录内容"""
        right_pages = self.right_menu.pages
        right_pages['history'].set_history_content(content)
    
    def get_history_content(self):
        """获取历史记录内容"""
        right_pages = self.right_menu.pages
        return right_pages['history'].get_history_content()
    
    def update_history_statistics(self, count, size_kb):
        """更新历史记录统计信息"""
        right_pages = self.right_menu.pages
        right_pages['history'].update_statistics(count, size_kb)
    
    def set_settings(self, settings):
        """设置配置项"""
        right_pages = self.right_menu.pages
        right_pages['settings'].set_settings(settings)
    
    def get_settings(self):
        """获取当前设置"""
        right_pages = self.right_menu.pages
        return right_pages['settings'].get_settings()
    
    # 数据页面特定方法
    def is_hex_send(self):
        """是否十六进制发送"""
        return self.main_data_page.is_hex_send()
    
    def is_auto_send(self):
        """是否自动发送"""
        return self.main_data_page.is_auto_send()
    
    def get_auto_send_interval(self):
        """获取自动发送间隔"""
        return self.main_data_page.get_auto_send_interval()
    
    def is_hex_display(self):
        """获取是否十六进制显示"""
        return self.right_menu.pages['data'].is_hex_display()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 关闭所有子窗口
            for page in self.right_menu.pages.values():
                if hasattr(page, 'received_windows'):
                    for window in page.received_windows.values():
                        if window.isVisible():
                            window.close()
                if hasattr(page, 'send_windows'):
                    for window in page.send_windows.values():
                        if window.isVisible():
                            window.close()
            
            # 隐藏右侧菜单
            if self.right_menu.isVisible():
                self.right_menu.hide()
            
            # 接受关闭事件
            event.accept()
        except Exception as e:
            print(f"窗口关闭时发生错误: {str(e)}")
            event.accept()
