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
                background-color: white;
                border-left: 1px solid #d0d0d0;
                border-right: 1px solid #d0d0d0;
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
        title_frame.setFixedHeight(45)  # 稍微减小高度
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #d0d0d0;
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
        
        close_button = QPushButton("×")
        close_button.setFixedSize(28, 28)  # 稍微减小按钮大小
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
                color: #666666;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
        """)
        close_button.clicked.connect(self.hide_menu)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        
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
                background-color: #f0f0f0;
                border-right: 1px solid #d0d0d0;
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
                background-color: white;
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
                        border: none;
                        border-radius: 8px;
                        background-color: #0078d4;
                        color: white;
                        font-size: 12px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QToolButton {
                        border: none;
                        border-radius: 8px;
                        background-color: transparent;
                        font-size: 12px;
                        color: #666666;
                    }
                    QToolButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QToolButton:pressed {
                        background-color: #d0d0d0;
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
                border: none;
                border-radius: 8px;
                background-color: transparent;
                font-size: 12px;
                color: #666666;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
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
        """更新连接状态"""
        self.main_data_page.update_connection_status(connected)
        # 同时更新右侧菜单中的页面
        right_pages = self.right_menu.pages
        right_pages['config'].update_connection_status(connected)
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
        """是否十六进制显示"""
        return self.main_data_page.is_hex_display()
