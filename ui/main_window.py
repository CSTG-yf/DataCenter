import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QFrame, QStackedWidget, QToolButton, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut

# 导入页面模块
from .config_page import ConfigPage
from .data_page import DataPage
from .history_page import HistoryPage
from .settings_page import SettingsPage


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
        
        # 创建左侧菜单栏
        left_menu = self.create_left_menu()
        main_layout.addWidget(left_menu)
        
        # 创建右侧内容区域
        self.right_content = self.create_right_content()
        main_layout.addWidget(self.right_content)
        
        # 设置布局比例
        main_layout.setStretch(0, 0)  # 左侧菜单不拉伸
        main_layout.setStretch(1, 1)  # 右侧内容区域拉伸
        
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
        
        # 串口配置菜单
        self.menu_buttons['config'] = self.create_menu_button("配置", "⚙️")
        self.menu_buttons['config'].clicked.connect(lambda: self.show_page('config'))
        menu_layout.addWidget(self.menu_buttons['config'])
        
        # 数据收发菜单
        self.menu_buttons['data'] = self.create_menu_button("收发", "📡")
        self.menu_buttons['data'].clicked.connect(lambda: self.show_page('data'))
        menu_layout.addWidget(self.menu_buttons['data'])
        
        # 历史记录菜单
        self.menu_buttons['history'] = self.create_menu_button("历史", "📋")
        self.menu_buttons['history'].clicked.connect(lambda: self.show_page('history'))
        menu_layout.addWidget(self.menu_buttons['history'])
        
        # 设置菜单
        self.menu_buttons['settings'] = self.create_menu_button("设置", "🔧")
        self.menu_buttons['settings'].clicked.connect(lambda: self.show_page('settings'))
        menu_layout.addWidget(self.menu_buttons['settings'])
        
        # 添加弹性空间
        menu_layout.addStretch()
        
        return menu_frame
    
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
    
    def create_right_content(self):
        """创建右侧内容区域"""
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: white;
            }
        """)
        
        # 创建各个页面
        self.pages = {}
        
        # 串口配置页面
        self.pages['config'] = ConfigPage()
        self.stacked_widget.addWidget(self.pages['config'])
        
        # 数据收发页面
        self.pages['data'] = DataPage()
        self.stacked_widget.addWidget(self.pages['data'])
        
        # 历史记录页面
        self.pages['history'] = HistoryPage()
        self.stacked_widget.addWidget(self.pages['history'])
        
        # 设置页面
        self.pages['settings'] = SettingsPage()
        self.stacked_widget.addWidget(self.pages['settings'])
        
        # 默认显示配置页面
        self.stacked_widget.setCurrentWidget(self.pages['config'])
        
        return self.stacked_widget
    
    def connect_signals(self):
        """连接页面信号"""
        # 配置页面信号
        self.pages['config'].connect_signal.connect(self.connect_signal.emit)
        self.pages['config'].disconnect_signal.connect(self.disconnect_signal.emit)
        self.pages['config'].refresh_ports_signal.connect(self.refresh_ports_signal.emit)
        
        # 数据页面信号
        self.pages['data'].send_data_signal.connect(self.send_data_signal.emit)
        self.pages['data'].clear_signal.connect(self.clear_signal.emit)
        
        # 历史记录页面信号
        self.pages['history'].clear_history_signal.connect(self.clear_history_signal.emit)
        self.pages['history'].save_history_signal.connect(self.save_history_signal.emit)
        
        # 设置页面信号
        self.pages['settings'].settings_changed_signal.connect(self.settings_changed_signal.emit)
        self.pages['settings'].reset_settings_signal.connect(self.reset_settings_signal.emit)
    
    def show_page(self, page_name):
        """显示指定页面"""
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            # 更新菜单按钮状态
            for name, button in self.menu_buttons.items():
                if name == page_name:
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
    
    # 公共接口方法，用于外部调用
    def update_connection_status(self, connected):
        """更新连接状态"""
        self.pages['config'].update_connection_status(connected)
        self.pages['data'].update_connection_status(connected)
    
    def update_port_list(self, ports):
        """更新串口列表"""
        self.pages['config'].update_port_list(ports)
    
    def append_receive_data(self, data):
        """添加接收数据到显示区域"""
        self.pages['data'].append_receive_data(data)
    
    def update_statistics(self, receive_count, send_count):
        """更新统计信息"""
        self.pages['data'].update_statistics(receive_count, send_count)
    
    def append_history(self, text):
        """添加历史记录"""
        self.pages['history'].append_history(text)
    
    def set_history_content(self, content):
        """设置历史记录内容"""
        self.pages['history'].set_history_content(content)
    
    def get_history_content(self):
        """获取历史记录内容"""
        return self.pages['history'].get_history_content()
    
    def update_history_statistics(self, count, size_kb):
        """更新历史记录统计信息"""
        self.pages['history'].update_statistics(count, size_kb)
    
    def set_settings(self, settings):
        """设置配置项"""
        self.pages['settings'].set_settings(settings)
    
    def get_settings(self):
        """获取当前设置"""
        return self.pages['settings'].get_settings()
    
    # 数据页面特定方法
    def is_hex_send(self):
        """是否十六进制发送"""
        return self.pages['data'].is_hex_send()
    
    def is_auto_send(self):
        """是否自动发送"""
        return self.pages['data'].is_auto_send()
    
    def get_auto_send_interval(self):
        """获取自动发送间隔"""
        return self.pages['data'].get_auto_send_interval()
    
    def is_hex_display(self):
        """是否十六进制显示"""
        return self.pages['data'].is_hex_display()
