import serial
import serial.tools.list_ports
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .data_saver import DataSaver


class MultiSerialManager(QObject):
    """多串口管理器，负责管理多个串口连接"""
    
    # 定义信号
    data_received = pyqtSignal(str, str)  # 接收到数据信号 (port_name, data)
    connection_changed = pyqtSignal(str, bool)  # 连接状态改变信号 (port_name, connected)
    error_occurred = pyqtSignal(str, str)  # 错误信号 (port_name, error_message)
    port_list_updated = pyqtSignal(list)  # 串口列表更新信号
    statistics_updated = pyqtSignal(str, int, int)  # 统计信息更新信号 (port_name, receive_count, send_count)
    
    def __init__(self):
        super().__init__()
        self.serial_ports = {}  # 存储串口对象 {port_name: serial_object}
        self.receive_threads = {}  # 存储接收线程 {port_name: thread}
        self.auto_send_timers = {}  # 存储自动发送定时器 {port_name: timer}
        self.auto_send_data = {}  # 存储自动发送数据 {port_name: data}
        
        # 统计信息 {port_name: {'receive_count': 0, 'send_count': 0}}
        self.statistics = {}
        
        # 数据保存器
        self.data_saver = DataSaver()
        
        # 自动保存配置 {port_name: {'enabled': bool, 'baudrate': int}}
        self.auto_save_config = {}
        
        # 全局设置
        self.global_settings = {
            'auto_save_serial': True,  # 默认启用自动保存
            'file_size_limit': 500     # 默认500MB
        }
        
    def get_available_ports(self):
        """获取可用串口列表"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_list_updated.emit(ports)
            return ports
        except Exception as e:
            self.error_occurred.emit("", f"获取串口列表失败: {str(e)}")
            return []
    
    def connect_serial(self, config):
        """连接串口"""
        try:
            port_name = config['port']
            
            # 检查是否已经连接
            if port_name in self.serial_ports:
                # 如果已经连接，先断开旧连接
                print(f"串口 {port_name} 已经连接，先断开旧连接")
                self.disconnect_serial(port_name)
                # 等待一下确保资源完全释放
                time.sleep(0.2)
            
            # 设置默认参数
            baudrate = config.get('baudrate', 115200)
            bytesize = config.get('bytesize', 8)
            stopbits = config.get('stopbits', 1)
            parity = config.get('parity', 'N')
            auto_save = config.get('auto_save', self.global_settings['auto_save_serial'])
            
            # 创建串口对象
            serial_port = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
                timeout=1
            )
            
            if serial_port.is_open:
                # 存储串口对象
                self.serial_ports[port_name] = serial_port
                
                # 初始化统计信息
                self.statistics[port_name] = {'receive_count': 0, 'send_count': 0}
                
                # 存储自动保存配置
                self.auto_save_config[port_name] = {
                    'enabled': auto_save,
                    'baudrate': baudrate
                }
                
                # 如果启用自动保存，开始保存
                if auto_save:
                    # 如果之前有保存，先停止
                    if self.data_saver.is_saving(port_name):
                        self.data_saver.stop_saving(port_name)
                    # 开始新的保存（创建新文件）
                    self.data_saver.start_saving(port_name, baudrate)
                
                # 创建自动发送定时器
                auto_send_timer = QTimer()
                auto_send_timer.timeout.connect(lambda: self.auto_send_data_func(port_name))
                self.auto_send_timers[port_name] = auto_send_timer
                
                # 启动接收线程
                receive_thread = threading.Thread(
                    target=self.receive_data_loop, 
                    args=(port_name,), 
                    daemon=True
                )
                self.receive_threads[port_name] = receive_thread
                receive_thread.start()
                
                # 等待线程启动
                time.sleep(0.05)
                
                # 发送连接状态信号
                self.connection_changed.emit(port_name, True)
                
                return True
            else:
                self.error_occurred.emit(port_name, "串口打开失败")
                # 发送连接失败状态信号
                self.connection_changed.emit(port_name, False)
                return False
                
        except serial.SerialException as e:
            self.error_occurred.emit(port_name, f"串口连接失败: {str(e)}")
            # 发送连接失败状态信号
            self.connection_changed.emit(port_name, False)
            return False
        except Exception as e:
            self.error_occurred.emit(port_name, f"连接错误: {str(e)}")
            # 发送连接失败状态信号
            self.connection_changed.emit(port_name, False)
            return False
    
    def disconnect_serial(self, port_name):
        """断开串口连接"""
        try:
            if port_name not in self.serial_ports:
                print(f"串口 {port_name} 未连接，无需断开")
                return True
            
            print(f"开始断开串口 {port_name}")
            
            # 停止自动发送
            self.stop_auto_send(port_name)
            
            # 停止数据保存
            if port_name in self.auto_save_config and self.auto_save_config[port_name]['enabled']:
                self.data_saver.stop_saving(port_name)
            
            # 关闭串口
            serial_port = self.serial_ports[port_name]
            if serial_port.is_open:
                serial_port.close()
                print(f"串口 {port_name} 已关闭")
            
            # 等待接收线程结束
            if port_name in self.receive_threads:
                thread = self.receive_threads[port_name]
                if thread.is_alive():
                    print(f"等待接收线程 {port_name} 结束")
                    # 给线程一些时间来自然结束
                    thread.join(timeout=1.0)
                    if thread.is_alive():
                        print(f"警告：接收线程 {port_name} 未能正常结束")
            
            # 清理资源
            if port_name in self.serial_ports:
                del self.serial_ports[port_name]
                print(f"已清理串口对象 {port_name}")
            if port_name in self.receive_threads:
                del self.receive_threads[port_name]
                print(f"已清理接收线程 {port_name}")
            if port_name in self.auto_send_timers:
                del self.auto_send_timers[port_name]
                print(f"已清理自动发送定时器 {port_name}")
            if port_name in self.auto_send_data:
                del self.auto_send_data[port_name]
                print(f"已清理自动发送数据 {port_name}")
            if port_name in self.statistics:
                del self.statistics[port_name]
                print(f"已清理统计信息 {port_name}")
            if port_name in self.auto_save_config:
                del self.auto_save_config[port_name]
                print(f"已清理自动保存配置 {port_name}")
            
            # 发送连接状态信号
            self.connection_changed.emit(port_name, False)
            
            print(f"串口 {port_name} 断开完成")
            return True
            
        except Exception as e:
            error_msg = f"断开串口连接失败: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(port_name, error_msg)
            return False
    
    def send_data(self, port_name, data, hex_mode=False):
        """向指定串口发送数据"""
        try:
            if port_name not in self.serial_ports:
                self.error_occurred.emit(port_name, f"串口 {port_name} 未连接")
                return False
            
            serial_port = self.serial_ports[port_name]
            
            if hex_mode:
                # 十六进制发送
                try:
                    # 移除空格和换行符
                    hex_string = data.replace(' ', '').replace('\n', '').replace('\r', '')
                    # 转换为字节
                    data_bytes = bytes.fromhex(hex_string)
                except ValueError:
                    self.error_occurred.emit(port_name, "十六进制数据格式错误")
                    return False
            else:
                # 普通文本发送
                data_bytes = data.encode('utf-8')
            
            # 发送数据
            serial_port.write(data_bytes)
            serial_port.flush()
            
            # 更新统计信息
            if port_name in self.statistics:
                self.statistics[port_name]['send_count'] += len(data_bytes)
                self.statistics_updated.emit(
                    port_name, 
                    self.statistics[port_name]['receive_count'],
                    self.statistics[port_name]['send_count']
                )
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"发送数据失败: {str(e)}")
            return False
    
    def receive_data_loop(self, port_name):
        """接收数据循环"""
        try:
            serial_port = self.serial_ports[port_name]
            
            while port_name in self.serial_ports and serial_port.is_open:
                try:
                    # 检查串口是否仍然有效
                    if not serial_port.is_open:
                        break
                    
                    # 读取数据
                    data = serial_port.readline()
                    if data is not None and len(data) > 0:
                        # 转换为字符串
                        data_str = data.decode('utf-8', errors='ignore')
                        
                        # 更新统计信息
                        if port_name in self.statistics:
                            self.statistics[port_name]['receive_count'] += len(data)
                            self.statistics_updated.emit(
                                port_name,
                                self.statistics[port_name]['receive_count'],
                                self.statistics[port_name]['send_count']
                            )
                        
                        # 自动保存数据
                        if (port_name in self.auto_save_config and 
                            self.auto_save_config[port_name]['enabled']):
                            self.data_saver.save_data(port_name, data_str)
                        
                        # 发送接收数据信号
                        self.data_received.emit(port_name, data_str)
                    
                    # 添加短暂延时避免CPU占用过高
                    import time
                    time.sleep(0.01)
                        
                except Exception as e:
                    if port_name in self.serial_ports:
                        # 检查是否是串口关闭导致的错误
                        if "Port is closed" in str(e) or "Access denied" in str(e):
                            # 串口已关闭，正常退出
                            break
                        else:
                            self.error_occurred.emit(port_name, f"接收数据错误: {str(e)}")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(port_name, f"接收线程错误: {str(e)}")
    
    def start_auto_send(self, port_name, data, interval_ms, hex_mode=False):
        """开始自动发送"""
        try:
            if port_name not in self.serial_ports:
                self.error_occurred.emit(port_name, f"串口 {port_name} 未连接")
                return False
            
            # 存储自动发送数据
            self.auto_send_data[port_name] = {
                'data': data,
                'hex_mode': hex_mode
            }
            
            # 启动定时器
            if port_name in self.auto_send_timers:
                self.auto_send_timers[port_name].start(interval_ms)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"启动自动发送失败: {str(e)}")
            return False
    
    def stop_auto_send(self, port_name):
        """停止自动发送"""
        try:
            if port_name in self.auto_send_timers:
                self.auto_send_timers[port_name].stop()
            
            if port_name in self.auto_send_data:
                del self.auto_send_data[port_name]
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"停止自动发送失败: {str(e)}")
            return False
    
    def auto_send_data_func(self, port_name):
        """自动发送数据函数"""
        try:
            if port_name in self.auto_send_data:
                auto_data = self.auto_send_data[port_name]
                self.send_data(port_name, auto_data['data'], auto_data['hex_mode'])
        except Exception as e:
            self.error_occurred.emit(port_name, f"自动发送数据失败: {str(e)}")
    
    def clear_statistics(self, port_name=None):
        """清空统计信息"""
        if port_name:
            if port_name in self.statistics:
                self.statistics[port_name] = {'receive_count': 0, 'send_count': 0}
                self.statistics_updated.emit(port_name, 0, 0)
        else:
            # 清空所有统计信息
            for port in self.statistics:
                self.statistics[port] = {'receive_count': 0, 'send_count': 0}
                self.statistics_updated.emit(port, 0, 0)
    
    def get_connection_status(self, port_name):
        """获取连接状态"""
        return port_name in self.serial_ports and self.serial_ports[port_name].is_open
    
    def get_statistics(self, port_name):
        """获取统计信息"""
        if port_name in self.statistics:
            return self.statistics[port_name]
        return {'receive_count': 0, 'send_count': 0}
    
    def get_all_connected_ports(self):
        """获取所有已连接的串口"""
        return list(self.serial_ports.keys())
    
    def disconnect_all(self):
        """断开所有串口连接"""
        try:
            # 停止所有定时器
            for timer in self.auto_send_timers.values():
                try:
                    timer.stop()
                except Exception as e:
                    print(f"停止定时器时发生错误: {str(e)}")
            
            # 断开所有串口
            for port_name in list(self.serial_ports.keys()):
                try:
                    self.disconnect_serial(port_name)
                except Exception as e:
                    print(f"断开串口 {port_name} 时发生错误: {str(e)}")
            
            # 关闭所有数据保存
            try:
                self.data_saver.close_all()
            except Exception as e:
                print(f"关闭数据保存时发生错误: {str(e)}")
            
            return True
        except Exception as e:
            self.error_occurred.emit("", f"断开所有连接失败: {str(e)}")
            return False 

    def update_auto_save_config(self, port_name, auto_save_enabled):
        """更新自动保存配置"""
        try:
            if port_name not in self.serial_ports:
                return False
            
            # 更新配置
            if port_name in self.auto_save_config:
                self.auto_save_config[port_name]['enabled'] = auto_save_enabled
            else:
                # 如果配置不存在，创建新的配置
                baudrate = self.serial_ports[port_name].baudrate
                self.auto_save_config[port_name] = {
                    'enabled': auto_save_enabled,
                    'baudrate': baudrate
                }
            
            # 如果启用自动保存且当前没有在保存，开始保存
            if auto_save_enabled and not self.data_saver.is_saving(port_name):
                baudrate = self.auto_save_config[port_name]['baudrate']
                self.data_saver.start_saving(port_name, baudrate)
            elif not auto_save_enabled and self.data_saver.is_saving(port_name):
                # 如果禁用自动保存且当前在保存，停止保存
                self.data_saver.stop_saving(port_name)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"更新自动保存配置失败: {str(e)}")
            return False 

    def update_global_settings(self, settings):
        """更新全局设置"""
        try:
            if 'auto_save_serial' in settings:
                self.global_settings['auto_save_serial'] = settings['auto_save_serial']
            
            if 'file_size_limit' in settings:
                self.global_settings['file_size_limit'] = settings['file_size_limit']
                # 更新数据保存器的文件大小限制
                self.data_saver.update_max_file_size(settings['file_size_limit'])
            
            return True
        except Exception as e:
            self.error_occurred.emit("", f"更新全局设置失败: {str(e)}")
            return False 