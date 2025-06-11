#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频二维码管理上位机 - 一键安装脚本
"""

import subprocess
import sys
import os

def install_requirements():
    """安装必要的依赖库"""
    print("🚀 正在安装必要的依赖库...")
    
    requirements = [
        "cos-python-sdk-v5==1.9.24",
        "qrcode[pil]==7.4.2", 
        "Pillow==10.1.0",
        "requests==2.31.0"
    ]
    
    for requirement in requirements:
        try:
            print(f"📦 安装 {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✅ {requirement} 安装成功！")
        except subprocess.CalledProcessError as e:
            print(f"❌ {requirement} 安装失败: {e}")
            return False
    
    return True

def create_directories():
    """创建必要的目录"""
    print("📁 创建输出目录...")
    
    directories = ["qr_codes", "logs"]
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ 创建目录: {dir_name}")

def main():
    """主安装流程"""
    print("🎵 音频二维码管理上位机 - 安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 需要Python 3.6或更高版本！")
        return
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖
    if not install_requirements():
        print("❌ 依赖安装失败，请检查网络连接或手动安装！")
        return
    
    # 创建目录
    create_directories()
    
    print("\n🎉 安装完成！")
    print("\n📋 使用说明:")
    print("1. 编辑 config.json 文件，填入您的腾讯云密钥")
    print("2. 运行命令: python audio_qr_manager.py")
    print("3. 在界面中连接COS并生成二维码")
    
    print("\n💡 提示:")
    print("- 确保您的腾讯云存储桶设置为公有读权限")
    print("- 二维码将保存在 qr_codes 目录中")
    print("- 配置文件会自动保存您的设置")

if __name__ == "__main__":
    main()