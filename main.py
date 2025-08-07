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
from core.multi_serial_manager import MultiSerialManager


class SerialCommunicationApp:
    """串口通信应用程序主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("串口通信工具")
        self.app.setApplicationVersion("1.0.0")
        
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 创建多串口管理器
        self.serial_manager = MultiSerialManager()
        
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
        # UI信号连接到多串口管理器
        self.main_window.connect_signal.connect(self.serial_manager.connect_serial)
        self.main_window.disconnect_signal.connect(self.handle_disconnect)
        self.main_window.send_data_signal.connect(self.handle_send_data)
        self.main_window.clear_signal.connect(self.serial_manager.clear_statistics)
        self.main_window.refresh_ports_signal.connect(self.refresh_ports)
        self.main_window.view_received_signal.connect(self.handle_view_received)
        self.main_window.send_data_to_port_signal.connect(self.handle_send_data_to_port)
        self.main_window.delete_serial_signal.connect(self.handle_delete_serial)
        self.main_window.disconnect_serial_signal.connect(self.handle_disconnect_serial)
        self.main_window.connect_serial_signal.connect(self.handle_connect_serial)
        
        # 多串口管理器信号连接到UI
        self.serial_manager.connection_changed.connect(self.handle_connection_changed)
        self.serial_manager.data_received.connect(self.handle_received_data)
        self.serial_manager.error_occurred.connect(self.show_error)
        self.serial_manager.port_list_updated.connect(self.main_window.update_port_list)
        self.serial_manager.statistics_updated.connect(self.handle_statistics_updated)
        
    def handle_send_data(self, data):
        """处理发送数据（兼容旧接口）"""
        if not data:
            return
        
        # 获取当前连接的串口
        connected_ports = self.serial_manager.get_all_connected_ports()
        if not connected_ports:
            QMessageBox.warning(self.main_window, "警告", "没有连接的串口")
            return
        
        # 向第一个连接的串口发送数据
        port_name = connected_ports[0]
        self.handle_send_data_to_port(port_name, data, False, False, 1000)
    
    def handle_send_data_to_port(self, port_name, data, hex_mode, auto_mode, interval):
        """处理向指定串口发送数据"""
        if not data:
            return
        
        if auto_mode:
            # 开始自动发送
            success = self.serial_manager.start_auto_send(port_name, data, interval, hex_mode)
            if success:
                # 更新发送窗口的自动发送状态
                config_page = self.main_window.right_menu.pages['config']
                if port_name in config_page.send_windows:
                    config_page.send_windows[port_name].update_auto_send_status(True)
        else:
            # 停止自动发送
            self.serial_manager.stop_auto_send(port_name)
            # 发送单次数据
            success = self.serial_manager.send_data(port_name, data, hex_mode)
            
            # 更新发送窗口的自动发送状态
            config_page = self.main_window.right_menu.pages['config']
            if port_name in config_page.send_windows:
                config_page.send_windows[port_name].update_auto_send_status(False)
    
    def handle_received_data(self, port_name, data):
        """处理接收到的数据"""
        # 将数据转发到配置页面的接收窗口
        config_page = self.main_window.right_menu.pages['config']
        config_page.append_received_data(port_name, data)
    
    def handle_connection_changed(self, port_name, connected):
        """处理连接状态变化"""
        # 更新配置页面的连接状态
        config_page = self.main_window.right_menu.pages['config']
        config_page.update_connection_status(connected, port_name)
        
        # 注意：不要在这里删除串口组件，让用户手动选择是否删除
    
    def handle_view_received(self, port_name):
        """处理查看接收信息"""
        # 这个信号已经由配置页面处理，这里不需要额外处理
        pass
    
    def handle_statistics_updated(self, port_name, receive_count, send_count):
        """处理统计信息更新"""
        # 这里可以添加统计信息的处理逻辑
        pass
    
    def handle_disconnect(self):
        """处理断开连接"""
        # 断开所有串口连接
        self.serial_manager.disconnect_all()
    
    def handle_delete_serial(self, port_name):
        """处理删除串口"""
        # 断开指定串口连接
        success = self.serial_manager.disconnect_serial(port_name)
        if success:
            print(f"已删除串口: {port_name}")
        else:
            print(f"删除串口失败: {port_name}")
    
    def handle_disconnect_serial(self, port_name):
        """处理断开串口连接"""
        # 断开指定串口连接
        success = self.serial_manager.disconnect_serial(port_name)
        if success:
            print(f"已断开串口连接: {port_name}")
            # 更新配置页面的连接状态
            config_page = self.main_window.right_menu.pages['config']
            config_page.update_connection_status(False, port_name)
        else:
            print(f"断开串口连接失败: {port_name}")
    
    def handle_connect_serial(self, port_name):
        """处理连接串口"""
        # 这里需要重新连接串口，使用默认配置
        config = {
            'port': port_name,
            'baudrate': 115200
        }
        success = self.serial_manager.connect_serial(config)
        if success:
            print(f"已重新连接串口: {port_name}")
            # 更新配置页面的连接状态
            config_page = self.main_window.right_menu.pages['config']
            config_page.update_connection_status(True, port_name)
        else:
            print(f"重新连接串口失败: {port_name}")
    
    def refresh_ports(self):
        """刷新串口列表"""
        self.serial_manager.get_available_ports()
    
    def show_error(self, port_name, error_message):
        """显示错误信息"""
        if port_name:
            QMessageBox.critical(self.main_window, f"串口 {port_name} 错误", error_message)
        else:
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
