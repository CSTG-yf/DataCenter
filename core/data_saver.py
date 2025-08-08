import os
import time
from datetime import datetime
from pathlib import Path


class DataSaver:
    """数据保存管理器，负责将串口数据保存到文件"""
    
    def __init__(self, base_dir="serial_logs"):
        """
        初始化数据保存管理器
        
        Args:
            base_dir: 保存目录，默认为当前目录下的serial_logs文件夹
        """
        self.base_dir = Path(base_dir)
        self.current_files = {}  # 当前打开的文件 {port_name: file_object}
        self.file_sizes = {}     # 文件大小 {port_name: current_size}
        self.port_baudrates = {} # 串口波特率 {port_name: baudrate}
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        
        # 确保保存目录存在
        self.base_dir.mkdir(exist_ok=True)
    
    def update_max_file_size(self, max_size_mb):
        """
        更新最大文件大小
        
        Args:
            max_size_mb: 最大文件大小（MB）
        """
        self.max_file_size = max_size_mb * 1024 * 1024
    
    def _generate_filename(self, port_name, baudrate):
        """
        生成文件名
        
        Args:
            port_name: 串口名称
            baudrate: 波特率
            
        Returns:
            str: 生成的文件名
        """
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        return f"{port_name}_{baudrate}_{date_str}_{time_str}.txt"
    
    def _get_new_file_path(self, port_name, baudrate):
        """
        获取新的文件路径
        
        Args:
            port_name: 串口名称
            baudrate: 波特率
            
        Returns:
            Path: 文件路径
        """
        filename = self._generate_filename(port_name, baudrate)
        return self.base_dir / filename
    
    def start_saving(self, port_name, baudrate):
        """
        开始保存数据
        
        Args:
            port_name: 串口名称
            baudrate: 波特率
            
        Returns:
            bool: 是否成功开始保存
        """
        try:
            # 如果已经有文件在保存，先关闭
            if port_name in self.current_files:
                self.stop_saving(port_name)
            
            # 创建新文件
            file_path = self._get_new_file_path(port_name, baudrate)
            file_obj = open(file_path, 'w', encoding='utf-8')
            
            # 写入文件头信息
            header = f"# 串口数据记录文件\n"
            header += f"# 串口: {port_name}\n"
            header += f"# 波特率: {baudrate}\n"
            header += f"# 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"# {'='*50}\n\n"
            
            file_obj.write(header)
            file_obj.flush()
            
            # 保存文件对象和大小
            self.current_files[port_name] = file_obj
            self.file_sizes[port_name] = len(header.encode('utf-8'))
            self.port_baudrates[port_name] = baudrate
            
            return True
            
        except Exception as e:
            print(f"开始保存数据失败: {str(e)}")
            return False
    
    def save_data(self, port_name, data):
        """
        保存数据到文件
        
        Args:
            port_name: 串口名称
            data: 要保存的数据
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if port_name not in self.current_files:
                return False
            
            file_obj = self.current_files[port_name]
            current_size = self.file_sizes[port_name]
            
            # 检查文件大小是否超过限制
            if current_size >= self.max_file_size:
                # 关闭当前文件
                file_obj.close()
                del self.current_files[port_name]
                del self.file_sizes[port_name]
                
                # 获取波特率信息
                baudrate = self.port_baudrates.get(port_name, 115200)
                
                # 重新创建文件
                new_file_path = self._get_new_file_path(port_name, baudrate)
                new_file_obj = open(new_file_path, 'w', encoding='utf-8')
                
                # 写入新文件头信息
                header = f"# 串口数据记录文件（续）\n"
                header += f"# 串口: {port_name}\n"
                header += f"# 波特率: {baudrate}\n"
                header += f"# 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += f"# 文件大小超过500MB，创建新文件\n"
                header += f"# {'='*50}\n\n"
                
                new_file_obj.write(header)
                new_file_obj.flush()
                
                # 保存新文件对象和大小
                self.current_files[port_name] = new_file_obj
                self.file_sizes[port_name] = len(header.encode('utf-8'))
                self.port_baudrates[port_name] = baudrate
                
                print(f"文件大小超过500MB，创建新文件: {port_name} -> {new_file_path}")
            
            # 添加时间戳
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            data_with_timestamp = f"[{timestamp}] {data}"
            
            # 写入数据
            file_obj = self.current_files[port_name]
            file_obj.write(data_with_timestamp)
            file_obj.flush()
            
            # 更新文件大小
            data_size = len(data_with_timestamp.encode('utf-8'))
            self.file_sizes[port_name] += data_size
            
            return True
            
        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            return False
    
    def stop_saving(self, port_name):
        """
        停止保存数据
        
        Args:
            port_name: 串口名称
        """
        try:
            if port_name in self.current_files:
                file_obj = self.current_files[port_name]
                
                # 写入结束信息
                footer = f"\n# {'='*50}\n"
                footer += f"# 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                footer += f"# 文件结束\n"
                
                file_obj.write(footer)
                file_obj.close()
                
                del self.current_files[port_name]
                if port_name in self.file_sizes:
                    del self.file_sizes[port_name]
                if port_name in self.port_baudrates:
                    del self.port_baudrates[port_name]
                    
        except Exception as e:
            print(f"停止保存数据失败: {str(e)}")
    
    def is_saving(self, port_name):
        """
        检查是否正在保存数据
        
        Args:
            port_name: 串口名称
            
        Returns:
            bool: 是否正在保存
        """
        return port_name in self.current_files
    
    def get_save_status(self, port_name):
        """
        获取保存状态
        
        Args:
            port_name: 串口名称
            
        Returns:
            dict: 保存状态信息
        """
        if port_name not in self.current_files:
            return {'saving': False, 'file_size': 0, 'file_path': None}
        
        file_obj = self.current_files[port_name]
        current_size = self.file_sizes.get(port_name, 0)
        
        return {
            'saving': True,
            'file_size': current_size,
            'file_path': str(file_obj.name)
        }
    
    def close_all(self):
        """关闭所有保存的文件"""
        try:
            for port_name in list(self.current_files.keys()):
                try:
                    self.stop_saving(port_name)
                except Exception as e:
                    print(f"关闭串口 {port_name} 的数据保存时发生错误: {str(e)}")
        except Exception as e:
            print(f"关闭所有数据保存时发生错误: {str(e)}")
