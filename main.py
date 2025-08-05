#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
串口通信工具主程序
作者: AI Assistant
功能: 实现串口数据的接收和发送
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.serial_handler import SerialHandler


class SerialCommunicationApp:
    """串口通信应用程序主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("串口通信工具")
        self.app.setApplicationVersion("1.0.0")
        
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 创建串口处理器
        self.serial_handler = SerialHandler()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化串口列表
        self.refresh_ports()
        
        # 创建定时器用于定期刷新串口列表
        self.port_refresh_timer = QTimer()
        self.port_refresh_timer.timeout.connect(self.refresh_ports)
        self.port_refresh_timer.start(5000)  # 每5秒刷新一次
        
    def connect_signals(self):
        """连接信号和槽"""
        # UI信号连接到串口处理器
        self.main_window.connect_signal.connect(self.serial_handler.connect_serial)
        self.main_window.disconnect_signal.connect(self.serial_handler.disconnect_serial)
        self.main_window.send_data_signal.connect(self.handle_send_data)
        self.main_window.clear_signal.connect(self.serial_handler.clear_statistics)
        self.main_window.refresh_ports_signal.connect(self.refresh_ports)
        
        # 串口处理器信号连接到UI
        self.serial_handler.connection_changed.connect(self.main_window.update_connection_status)
        self.serial_handler.data_received.connect(self.handle_received_data)
        self.serial_handler.error_occurred.connect(self.show_error)
        self.serial_handler.port_list_updated.connect(self.main_window.update_port_list)
        self.serial_handler.statistics_updated.connect(self.main_window.update_statistics)
        
    def handle_send_data(self, data):
        """处理发送数据"""
        if not data:
            return
            
        # 检查是否启用十六进制发送
        hex_mode = self.main_window.is_hex_send()
        
        # 检查是否启用自动发送
        if self.main_window.is_auto_send():
            interval = self.main_window.get_auto_send_interval()
            self.serial_handler.start_auto_send(data, interval, hex_mode)
        else:
            # 停止自动发送
            self.serial_handler.stop_auto_send()
            # 发送单次数据
            self.serial_handler.send_data(data, hex_mode)
    
    def handle_received_data(self, data):
        """处理接收到的数据"""
        # 检查是否启用十六进制显示
        if self.main_window.is_hex_display():
            # 转换为十六进制显示
            hex_data = self.serial_handler.bytes_to_hex_string(data.encode('utf-8'))
            self.main_window.append_receive_data(hex_data + ' ')
        else:
            # 普通文本显示
            self.main_window.append_receive_data(data)
    
    def refresh_ports(self):
        """刷新串口列表"""
        self.serial_handler.get_available_ports()
    
    def show_error(self, error_message):
        """显示错误信息"""
        QMessageBox.critical(self.main_window, "错误", error_message)
    
    def run(self):
        """运行应用程序"""
        # 主窗口已经在初始化时设置了最大化状态并显示
        return self.app.exec()


def main():
    """主函数"""
    try:
        app = SerialCommunicationApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
