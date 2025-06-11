#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频二维码管理上位机
作者: Audio QR Manager
版本: 1.0.0
功能: 连接腾讯云COS，获取音频文件，生成永久二维码
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import json
from datetime import datetime
import webbrowser

# 导入腾讯云和二维码相关库
try:
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
    import qrcode
    from PIL import Image, ImageTk
    import requests
except ImportError as e:
    print(f"请安装必要的依赖库: {e}")
    print("运行命令: pip install -r requirements.txt")
    exit(1)

class AudioQRManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎵 音频二维码管理上位机 v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 配置变量
        self.secret_id = tk.StringVar()
        self.secret_key = tk.StringVar()
        self.bucket_name = tk.StringVar(value="audio-qr-1361719303")
        self.region = tk.StringVar(value="ap-chengdu")
        
        # COS客户端
        self.cos_client = None
        self.audio_files = []
        self.qr_codes = []
        
        # 初始化界面
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建配置面板
        self.create_config_panel()
        
        # 创建文件列表面板
        self.create_file_panel()
        
        # 创建二维码生成面板
        self.create_qr_panel()
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="加载配置", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="批量生成二维码", command=self.batch_generate_qr)
        tools_menu.add_command(label="打开播放页面", command=self.open_player_page)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_config_panel(self):
        """创建配置面板"""
        config_frame = ttk.LabelFrame(self.main_frame, text="🔧 腾讯云COS配置", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SecretId
        ttk.Label(config_frame, text="SecretId:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        secret_id_entry = ttk.Entry(config_frame, textvariable=self.secret_id, width=50, show="*")
        secret_id_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # SecretKey
        ttk.Label(config_frame, text="SecretKey:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        secret_key_entry = ttk.Entry(config_frame, textvariable=self.secret_key, width=50, show="*")
        secret_key_entry.grid(row=0, column=3, sticky=tk.W)
        
        # 存储桶名称
        ttk.Label(config_frame, text="存储桶:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        bucket_entry = ttk.Entry(config_frame, textvariable=self.bucket_name, width=30)
        bucket_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0), padx=(0, 20))
        
        # 地域
        ttk.Label(config_frame, text="地域:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        region_entry = ttk.Entry(config_frame, textvariable=self.region, width=20)
        region_entry.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # 连接按钮
        connect_btn = ttk.Button(config_frame, text="🔗 连接COS", command=self.connect_cos)
        connect_btn.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # 刷新按钮
        refresh_btn = ttk.Button(config_frame, text="🔄 刷新文件列表", command=self.refresh_files)
        refresh_btn.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(15, 0), padx=(20, 0))
        
    def create_file_panel(self):
        """创建文件列表面板"""
        file_frame = ttk.LabelFrame(self.main_frame, text="📁 音频文件列表", padding=15)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ('文件名', '大小', '修改时间', '状态')
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=200)
        
        # 滚动条
        scrollbar_v = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar_h = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 布局
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        file_frame.grid_rowconfigure(0, weight=1)
        file_frame.grid_columnconfigure(0, weight=1)
        
        # 右键菜单
        self.create_context_menu()
        
    def create_qr_panel(self):
        """创建二维码生成面板"""
        qr_frame = ttk.LabelFrame(self.main_frame, text="🎯 二维码生成", padding=15)
        qr_frame.pack(fill=tk.X)
        
        # 生成方式选择
        ttk.Label(qr_frame, text="生成方式:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.qr_type = tk.StringVar(value="wechat")
        
        direct_radio = ttk.Radiobutton(qr_frame, text="直接链接", variable=self.qr_type, value="direct")
        direct_radio.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        player_radio = ttk.Radiobutton(qr_frame, text="本地播放页面", variable=self.qr_type, value="player")
        player_radio.grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        
        wechat_radio = ttk.Radiobutton(qr_frame, text="微信适配", variable=self.qr_type, value="wechat")
        wechat_radio.grid(row=0, column=3, sticky=tk.W)
        
        # 输出目录
        ttk.Label(qr_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "qr_codes"))
        output_entry = ttk.Entry(qr_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        
        browse_btn = ttk.Button(qr_frame, text="浏览", command=self.browse_output_dir)
        browse_btn.grid(row=1, column=3, pady=(10, 0))
        
        # 操作按钮
        btn_frame = ttk.Frame(qr_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))
        
        generate_selected_btn = ttk.Button(btn_frame, text="🎯 生成选中项", command=self.generate_selected_qr)
        generate_selected_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        generate_all_btn = ttk.Button(btn_frame, text="⚡ 批量生成", command=self.batch_generate_qr)
        generate_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        open_folder_btn = ttk.Button(btn_frame, text="📂 打开输出目录", command=self.open_output_folder)
        open_folder_btn.pack(side=tk.LEFT)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(self.status_bar, textvariable=self.status_text)
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.status_bar, length=200)
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
        
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="生成二维码", command=self.generate_selected_qr)
        self.context_menu.add_command(label="播放音频", command=self.play_selected_audio)
        self.context_menu.add_command(label="复制链接", command=self.copy_selected_url)
        
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass
            
    def connect_cos(self):
        """连接到腾讯云COS"""
        if not self.secret_id.get() or not self.secret_key.get():
            messagebox.showerror("错误", "请填写SecretId和SecretKey！")
            return
            
        try:
            print(f"正在连接COS...")
            print(f"Region: {self.region.get()}")
            print(f"Bucket: {self.bucket_name.get()}")
            print(f"SecretId: {self.secret_id.get()[:10]}...")
            
            config = CosConfig(
                Region=self.region.get(),
                SecretId=self.secret_id.get(),
                SecretKey=self.secret_key.get()
            )
            self.cos_client = CosS3Client(config)
            
            # 测试连接
            print("正在测试COS连接...")
            response = self.cos_client.list_objects(Bucket=self.bucket_name.get(), MaxKeys=1)
            print(f"COS连接测试响应: {response}")
            
            self.status_text.set("COS连接成功！")
            messagebox.showinfo("成功", "已成功连接到腾讯云COS！")
            
            # 自动刷新文件列表
            print("自动刷新文件列表...")
            self.refresh_files()
            
        except Exception as e:
            print(f"COS连接失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_text.set("COS连接失败")
            messagebox.showerror("连接失败", f"无法连接到COS：{str(e)}")
            
    def refresh_files(self):
        """刷新音频文件列表"""
        if not self.cos_client:
            messagebox.showwarning("警告", "请先连接到COS！")
            return
            
        def refresh_thread():
            try:
                self.root.after(0, lambda: self.status_text.set("正在获取文件列表..."))
                self.audio_files = []
                
                # 获取所有文件
                marker = ""
                audio_extensions = ('.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma')
                total_files_scanned = 0
                audio_files_found = 0
                
                print(f"开始扫描存储桶: {self.bucket_name.get()}")
                
                while True:
                    print(f"正在获取文件列表，marker: {marker}")
                    response = self.cos_client.list_objects(
                        Bucket=self.bucket_name.get(),
                        Marker=marker,
                        MaxKeys=1000
                    )
                    
                    print(f"API响应: {response}")
                    
                    if 'Contents' in response:
                        for obj in response['Contents']:
                            key = obj['Key']
                            total_files_scanned += 1
                            print(f"扫描文件: {key}")
                            
                            if key.lower().endswith(audio_extensions):
                                audio_files_found += 1
                                file_info = {
                                    'key': key,
                                    'name': os.path.basename(key),
                                    'size': int(obj['Size']),
                                    'last_modified': obj['LastModified'],
                                    'url': f"https://{self.bucket_name.get()}.cos.{self.region.get()}.myqcloud.com/{key}"
                                }
                                self.audio_files.append(file_info)
                                print(f"找到音频文件: {key}")
                    else:
                        print("响应中没有Contents字段")
                    
                    if response.get('IsTruncated') == 'false':
                        print("已获取所有文件")
                        break
                    
                    if 'NextMarker' in response:
                        marker = response['NextMarker']
                        print(f"继续获取，下一个marker: {marker}")
                    else:
                        print("没有NextMarker，停止获取")
                        break
                
                print(f"扫描完成！总文件数: {total_files_scanned}, 音频文件数: {audio_files_found}")
                
                # 更新界面
                self.root.after(0, self.update_file_list)
                
            except Exception as e:
                print(f"获取文件列表时发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: messagebox.showerror("错误", f"获取文件列表失败：{str(e)}"))
                self.root.after(0, lambda: self.status_text.set("获取文件列表失败"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
        
    def get_qr_content(self, file_info):
        """根据选择的模式生成二维码内容"""
        qr_mode = self.qr_type.get()
        audio_url = file_info['url']
        
        if qr_mode == "direct":
            # 直接链接模式
            return audio_url
        elif qr_mode == "player":
            # 本地播放页面模式
            return f"./player.html?url={audio_url}"
        elif qr_mode == "wechat":
            # 微信适配模式 - 使用在线播放器
            import urllib.parse
            encoded_url = urllib.parse.quote(audio_url, safe='')
            
            # 方案1: 使用Vercel（推荐，全球CDN，国内访问速度不错）
            # 注意：需要重新部署包含wechat_player.html的Vercel项目
            return f"https://audio-qr-system2-3lm6.vercel.app/wechat_player.html?url={encoded_url}"
            
            # 方案2: 使用GitHub Pages（备用方案，如果Vercel有问题）
            # return f"https://yourusername.github.io/audio-player/wechat_player.html?url={encoded_url}"
            
            # 方案3: 使用腾讯云静态网站托管（推荐，国内访问最快）
            # return f"https://你的腾讯云域名/wechat_player.html?url={encoded_url}"
        else:
            return audio_url

    def update_file_list(self):
        """更新文件列表界面"""
        print(f"开始更新文件列表界面，音频文件数: {len(self.audio_files)}")
        
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # 添加文件
        for i, file_info in enumerate(self.audio_files):
            try:
                size_mb = file_info['size'] / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
                
                self.file_tree.insert('', 'end', values=(
                    file_info['name'],
                    size_str,
                    file_info['last_modified'][:19],
                    "就绪"
                ))
                print(f"添加文件到列表: {file_info['name']}")
            except Exception as e:
                print(f"添加文件到列表时出错: {file_info}, 错误: {e}")
            
        status_msg = f"已获取 {len(self.audio_files)} 个音频文件"
        self.status_text.set(status_msg)
        print(f"文件列表更新完成: {status_msg}")
        
    def generate_selected_qr(self):
        """生成选中文件的二维码"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
            
        def generate_thread():
            try:
                os.makedirs(self.output_dir.get(), exist_ok=True)
                
                for item in selected_items:
                    values = self.file_tree.item(item, 'values')
                    file_name = values[0]
                    
                    # 找到对应的文件信息
                    file_info = next((f for f in self.audio_files if f['name'] == file_name), None)
                    if not file_info:
                        continue
                        
                    # 生成二维码
                    qr_content = self.get_qr_content(file_info)
                        
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(qr_content)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # 保存二维码
                    name_without_ext = os.path.splitext(file_name)[0]
                    qr_path = os.path.join(self.output_dir.get(), f"{name_without_ext}.png")
                    img.save(qr_path)
                    
                    # 更新状态
                    self.root.after(0, lambda item=item: self.file_tree.set(item, '状态', '已生成'))
                    
                self.root.after(0, lambda: self.status_text.set("二维码生成完成！"))
                self.root.after(0, lambda: messagebox.showinfo("成功", "二维码生成完成！"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"生成二维码失败：{str(e)}"))
                
        threading.Thread(target=generate_thread, daemon=True).start()
        
    def batch_generate_qr(self):
        """批量生成所有音频文件的二维码"""
        if not self.audio_files:
            messagebox.showwarning("警告", "没有音频文件，请先刷新文件列表！")
            return
            
        if not messagebox.askyesno("确认", f"将为 {len(self.audio_files)} 个音频文件生成二维码，是否继续？"):
            return
            
        def batch_thread():
            try:
                os.makedirs(self.output_dir.get(), exist_ok=True)
                total = len(self.audio_files)
                
                for i, file_info in enumerate(self.audio_files):
                    # 更新进度
                    progress = (i + 1) / total * 100
                    self.root.after(0, lambda p=progress: self.progress.configure(value=p))
                    self.root.after(0, lambda: self.status_text.set(f"正在生成: {file_info['name']} ({i+1}/{total})"))
                    
                    # 生成二维码
                    qr_content = self.get_qr_content(file_info)
                        
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(qr_content)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # 保存二维码
                    name_without_ext = os.path.splitext(file_info['name'])[0]
                    qr_path = os.path.join(self.output_dir.get(), f"{name_without_ext}.png")
                    img.save(qr_path)
                    
                # 重置进度条
                self.root.after(0, lambda: self.progress.configure(value=0))
                self.root.after(0, lambda: self.status_text.set("批量生成完成！"))
                self.root.after(0, lambda: messagebox.showinfo("成功", f"已为 {total} 个音频文件生成二维码！"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"批量生成失败：{str(e)}"))
                self.root.after(0, lambda: self.progress.configure(value=0))
                
        threading.Thread(target=batch_thread, daemon=True).start()
        
    def play_selected_audio(self):
        """播放选中的音频"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
            
        item = selected_items[0]
        values = self.file_tree.item(item, 'values')
        file_name = values[0]
        
        file_info = next((f for f in self.audio_files if f['name'] == file_name), None)
        if file_info:
            webbrowser.open(file_info['url'])
            
    def copy_selected_url(self):
        """复制选中文件的URL"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
            
        item = selected_items[0]
        values = self.file_tree.item(item, 'values')
        file_name = values[0]
        
        file_info = next((f for f in self.audio_files if f['name'] == file_name), None)
        if file_info:
            self.root.clipboard_clear()
            self.root.clipboard_append(file_info['url'])
            messagebox.showinfo("成功", "链接已复制到剪贴板！")
            
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            
    def open_output_folder(self):
        """打开输出文件夹"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{output_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{output_path}"')
        else:
            messagebox.showwarning("警告", "输出目录不存在！")
            
    def open_player_page(self):
        """打开播放页面"""
        player_path = os.path.join(os.getcwd(), "player.html")
        if os.path.exists(player_path):
            webbrowser.open(f"file://{player_path}")
        else:
            messagebox.showwarning("警告", "播放页面文件不存在！")
            
    def save_config(self):
        """保存配置"""
        config = {
            'secret_id': self.secret_id.get(),
            'secret_key': self.secret_key.get(),
            'bucket_name': self.bucket_name.get(),
            'region': self.region.get(),
            'output_dir': self.output_dir.get()
        }
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")
            
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.secret_id.set(config.get('secret_id', ''))
                self.secret_key.set(config.get('secret_key', ''))
                self.bucket_name.set(config.get('bucket_name', 'audio-qr-1361719303'))
                self.region.set(config.get('region', 'ap-chengdu'))
                self.output_dir.set(config.get('output_dir', os.path.join(os.getcwd(), "qr_codes")))
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败：{str(e)}")
            
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎵 音频二维码管理上位机使用说明

1. 配置腾讯云COS：
   - 填写您的SecretId和SecretKey
   - 确认存储桶名称和地域
   - 点击"连接COS"按钮

2. 获取音频文件：
   - 连接成功后自动获取文件列表
   - 或手动点击"刷新文件列表"

3. 生成二维码：
   - 选择生成方式（直接链接/播放页面）
   - 选择音频文件
   - 点击"生成选中项"或"批量生成"

4. 二维码说明：
   - 直接链接：扫码后在浏览器中播放（可能需要下载）
   - 本地播放页面：扫码后打开本地播放界面
   - 微信适配：专为微信扫码优化的播放页面

5. 输出文件：
   - 二维码保存在指定的输出目录
   - 文件名与音频文件名相同（PNG格式）
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state='disabled')
        
    def show_about(self):
        """显示关于信息"""
        about_text = """
🎵 音频二维码管理上位机 v1.0

作者: Audio QR Manager
功能: 连接腾讯云COS，获取音频文件，生成永久二维码

特性：
✅ 自动连接腾讯云COS
✅ 批量获取音频文件列表
✅ 支持多种音频格式
✅ 生成永久有效二维码
✅ 支持直接链接和播放页面两种模式
✅ 批量处理和导出

技术栈：
- Python 3.x
- Tkinter GUI
- 腾讯云COS SDK
- QRCode库
        """
        messagebox.showinfo("关于", about_text)
        
    def run(self):
        """启动应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = AudioQRManager()
    app.run()