import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import time
import keyboard
import sys
import configparser
import os
from tkinter import scrolledtext

class MCToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft工具箱")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # 设置窗口置顶
        self.root.attributes('-topmost', True)
        
        # 运行状态标志
        self.is_running = False
        self.stop_requested = False
        
        # 默认配置
        self.config = {
            'creature': 'minecraft:zombie',
            'command': '/summon',
            'count': 30,
            'position': '~ ~1 ~',
            'hotkey_start': 'f9',
            'hotkey_stop': 'f10',
            'start_delay': 3,
            'player_name': '@p',
            'quick_command': '/kill',
            'command_target': '@s'
        }
        
        # 生物列表
        self.creatures = {
            "僵尸": "minecraft:zombie",
            "骷髅": "minecraft:skeleton",
            "苦力怕": "minecraft:creeper",
            "末影人": "minecraft:enderman",
            "蜘蛛": "minecraft:spider",
            "洞穴蜘蛛": "minecraft:cave_spider",
            "女巫": "minecraft:witch",
            "史莱姆": "minecraft:slime",
            "岩浆怪": "minecraft:magma_cube",
            "僵尸猪人": "minecraft:zombified_piglin",
            "烈焰人": "minecraft:blaze",
            "恶魂": "minecraft:ghast",
            "末影龙": "minecraft:ender_dragon",
            "凋灵": "minecraft:wither",
            "村民": "minecraft:villager",
            "牛": "minecraft:cow",
            "猪": "minecraft:pig",
            "羊": "minecraft:sheep",
            "鸡": "minecraft:chicken",
            "狼": "minecraft:wolf",
            "猫": "minecraft:cat",
            "马": "minecraft:horse",
            "驴": "minecraft:donkey",
            "兔子": "minecraft:rabbit",
            "北极熊": "minecraft:polar_bear",
            "海豚": "minecraft:dolphin",
            "海龟": "minecraft:turtle",
            "鹦鹉": "minecraft:parrot",
            "熊猫": "minecraft:panda",
            "狐狸": "minecraft:fox"
        }
        
        # 加载配置
        self.config_file = "mctool.ini"
        self.load_config()
        
        # 创建标签页
        self.create_notebook()
        
        # 注册全局快捷键
        self.register_hotkeys()
        
        # 退出时清理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_notebook(self):
        # 创建标签页框架
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 召唤生物标签页
        self.summon_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summon_tab, text='召唤生物')
        self.create_summon_tab()
        
        # 玩家管理标签页
        self.player_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.player_tab, text='玩家管理')
        self.create_player_tab()
        
        # 快捷命令标签页
        self.command_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.command_tab, text='快捷命令')
        self.create_command_tab()
        
        # 配置标签页
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text='配置设置')
        self.create_config_tab()
        
        # 关于标签页
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text='关于')
        self.create_about_tab()
    
    def create_summon_tab(self):
        # 召唤配置框架
        config_frame = ttk.LabelFrame(self.summon_tab, text="召唤设置")
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # 生物类型选择
        creature_frame = ttk.Frame(config_frame)
        creature_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(creature_frame, text="生物类型:").pack(side='left', padx=5)
        
        self.creature_var = tk.StringVar(value=self.config['creature'])
        creature_names = list(self.creatures.keys())
        self.creature_combo = ttk.Combobox(
            creature_frame, 
            textvariable=self.creature_var, 
            values=creature_names,
            state="readonly",
            width=20
        )
        self.creature_combo.pack(side='left', padx=5)
        self.creature_combo.bind("<<ComboboxSelected>>", self.update_creature_id)
        
        # 显示生物ID
        self.creature_id_var = tk.StringVar(value=self.config['creature'])
        ttk.Label(creature_frame, text="生物ID:").pack(side='left', padx=(20,5))
        ttk.Label(creature_frame, textvariable=self.creature_id_var).pack(side='left')
        
        # 召唤位置
        pos_frame = ttk.Frame(config_frame)
        pos_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(pos_frame, text="生成位置:").pack(side='left', padx=5)
        
        self.pos_var = tk.StringVar(value=self.config['position'])
        pos_entry = ttk.Entry(pos_frame, textvariable=self.pos_var, width=30)
        pos_entry.pack(side='left', padx=5)
        
        # 召唤次数
        count_frame = ttk.Frame(config_frame)
        count_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(count_frame, text="召唤次数:").pack(side='left', padx=5)
        
        self.count_var = tk.IntVar(value=self.config['count'])
        count_spin = ttk.Spinbox(count_frame, from_=1, to=1000, textvariable=self.count_var, width=5)
        count_spin.pack(side='left', padx=5)
        
        # 快捷键说明
        hotkey_frame = ttk.Frame(config_frame)
        hotkey_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(hotkey_frame, text="快捷键:").pack(side='left', padx=5)
        ttk.Label(hotkey_frame, text=f"开始: {self.config['hotkey_start']}  停止: {self.config['hotkey_stop']}").pack(side='left')
        
        # 开始按钮
        btn_frame = ttk.Frame(self.summon_tab)
        btn_frame.pack(pady=10)
        
        self.summon_start_btn = ttk.Button(
            btn_frame,
            text="开始召唤",
            command=lambda: self.start_action("summon"),
            width=15
        )
        self.summon_start_btn.pack(side='left', padx=10)
        
        self.summon_stop_btn = ttk.Button(
            btn_frame,
            text="停止召唤",
            command=self.stop_action,
            width=15,
            state=tk.DISABLED
        )
        self.summon_stop_btn.pack(side='left', padx=10)
        
        # 进度条框架
        progress_frame = ttk.LabelFrame(self.summon_tab, text="召唤进度")
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        # 进度条
        self.summon_progress_bar = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=650, 
            mode="determinate"
        )
        self.summon_progress_bar.pack(pady=10, padx=10)
        
        # 进度文本
        self.summon_progress_text = ttk.Label(
            progress_frame,
            text="等待开始召唤...",
            font=("Arial", 9)
        )
        self.summon_progress_text.pack(pady=5)
        
        # 状态标签
        self.summon_status = ttk.Label(
            self.summon_tab,
            text="状态: 就绪",
            font=("Arial", 10)
        )
        self.summon_status.pack(pady=5)
    
    def create_player_tab(self):
        # 玩家命令框架
        command_frame = ttk.LabelFrame(self.player_tab, text="玩家命令")
        command_frame.pack(fill='x', padx=10, pady=5)
        
        # 命令选择
        cmd_frame = ttk.Frame(command_frame)
        cmd_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(cmd_frame, text="选择命令:").pack(side='left', padx=5)
        
        self.player_cmd_var = tk.StringVar(value="踢出玩家")
        player_commands = ["踢出玩家", "杀死玩家", "传送到玩家", "传送到位置", "给予物品", "赋予效果"]
        player_cmd_combo = ttk.Combobox(
            cmd_frame, 
            textvariable=self.player_cmd_var, 
            values=player_commands,
            state="readonly",
            width=15
        )
        player_cmd_combo.pack(side='left', padx=5)
        player_cmd_combo.bind("<<ComboboxSelected>>", self.update_player_command)
        
        # 目标选择
        target_frame = ttk.Frame(command_frame)
        target_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(target_frame, text="目标选择:").pack(side='left', padx=5)
        
        self.target_var = tk.StringVar(value=self.config['player_name'])
        target_options = ["@p (最近的玩家)", "@a (所有玩家)", "@r (随机玩家)", "@s (自己)", "手动输入"]
        target_combo = ttk.Combobox(
            target_frame, 
            textvariable=self.target_var, 
            values=target_options,
            state="readonly",
            width=20
        )
        target_combo.pack(side='left', padx=5)
        target_combo.bind("<<ComboboxSelected>>", self.update_target_input)
        
        # 目标输入框
        self.target_input_frame = ttk.Frame(command_frame)
        self.target_input_frame.pack(fill='x', pady=5, padx=10)
        
        self.target_input_var = tk.StringVar()
        self.target_input_label = ttk.Label(self.target_input_frame, text="玩家名称:")
        self.target_input_label.pack(side='left', padx=5)
        self.target_input_entry = ttk.Entry(self.target_input_frame, textvariable=self.target_input_var, width=25)
        self.target_input_entry.pack(side='left', padx=5)
        self.target_input_frame.pack_forget()  # 默认隐藏
        
        # 命令预览
        preview_frame = ttk.Frame(command_frame)
        preview_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(preview_frame, text="命令预览:").pack(side='left', padx=5)
        
        self.cmd_preview_var = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.cmd_preview_var, foreground="blue").pack(side='left', padx=5)
        
        # 开始按钮
        btn_frame = ttk.Frame(self.player_tab)
        btn_frame.pack(pady=10)
        
        self.player_start_btn = ttk.Button(
            btn_frame,
            text="执行命令",
            command=lambda: self.start_action("player"),
            width=15
        )
        self.player_start_btn.pack(side='left', padx=10)
        
        # 状态标签
        self.player_status = ttk.Label(
            self.player_tab,
            text="状态: 就绪",
            font=("Arial", 10)
        )
        self.player_status.pack(pady=5)
        
        # 初始化命令预览
        self.update_player_command()
    
    def create_command_tab(self):
        # 快捷命令框架
        command_frame = ttk.LabelFrame(self.command_tab, text="快捷命令")
        command_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 命令选择
        cmd_frame = ttk.Frame(command_frame)
        cmd_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(cmd_frame, text="选择命令:").pack(side='left', padx=5)
        
        self.quick_cmd_var = tk.StringVar(value=self.config['quick_command'])
        quick_commands = [
            "/kill @s", 
            "/gamemode creative", 
            "/gamemode survival", 
            "/time set day", 
            "/time set night",
            "/weather clear",
            "/weather rain",
            "/weather thunder",
            "/give @s minecraft:diamond 64",
            "/effect give @s minecraft:speed 300 1"
        ]
        quick_cmd_combo = ttk.Combobox(
            cmd_frame, 
            textvariable=self.quick_cmd_var, 
            values=quick_commands,
            width=40
        )
        quick_cmd_combo.pack(side='left', padx=5)
        
        # 自定义命令
        custom_frame = ttk.Frame(command_frame)
        custom_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(custom_frame, text="自定义命令:").pack(side='left', padx=5)
        
        self.custom_cmd_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_cmd_var, width=40)
        custom_entry.pack(side='left', padx=5)
        
        # 开始按钮
        btn_frame = ttk.Frame(self.command_tab)
        btn_frame.pack(pady=10)
        
        self.command_start_btn = ttk.Button(
            btn_frame,
            text="执行命令",
            command=lambda: self.start_action("command"),
            width=15
        )
        self.command_start_btn.pack(side='left', padx=10)
        
        # 快捷键说明
        hotkey_frame = ttk.Frame(self.command_tab)
        hotkey_frame.pack(pady=5)
        ttk.Label(hotkey_frame, text=f"快捷键: {self.config['hotkey_start']} 执行命令").pack()
        
        # 状态标签
        self.command_status = ttk.Label(
            self.command_tab,
            text="状态: 就绪",
            font=("Arial", 10)
        )
        self.command_status.pack(pady=5)
    
    def create_config_tab(self):
        # 配置框架
        config_frame = ttk.LabelFrame(self.config_tab, text="全局配置")
        config_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 快捷键设置
        hotkey_frame = ttk.Frame(config_frame)
        hotkey_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(hotkey_frame, text="开始快捷键:").pack(side='left', padx=5)
        
        self.start_hk_var = tk.StringVar(value=self.config['hotkey_start'])
        start_hk_entry = ttk.Entry(hotkey_frame, textvariable=self.start_hk_var, width=10)
        start_hk_entry.pack(side='left', padx=5)
        
        ttk.Label(hotkey_frame, text="停止快捷键:").pack(side='left', padx=(20,5))
        
        self.stop_hk_var = tk.StringVar(value=self.config['hotkey_stop'])
        stop_hk_entry = ttk.Entry(hotkey_frame, textvariable=self.stop_hk_var, width=10)
        stop_hk_entry.pack(side='left', padx=5)
        
        # 开始延迟
        delay_frame = ttk.Frame(config_frame)
        delay_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(delay_frame, text="开始延迟(秒):").pack(side='left', padx=5)
        
        self.delay_var = tk.IntVar(value=self.config['start_delay'])
        delay_spin = ttk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=5)
        delay_spin.pack(side='left', padx=5)
        
        # 保存按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(pady=20)
        
        save_btn = ttk.Button(
            btn_frame,
            text="保存配置",
            command=self.save_config,
            width=15
        )
        save_btn.pack(side='left', padx=10)
        
        # 状态标签
        self.config_status = ttk.Label(
            config_frame,
            text="配置修改后请点击保存",
            font=("Arial", 9),
            foreground="green"
        )
        self.config_status.pack(pady=5)
    
    def create_about_tab(self):
        # 关于框架
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题
        title = ttk.Label(
            about_frame, 
            text="Minecraft工具箱", 
            font=("Arial", 16, "bold"),
            foreground="dark green"
        )
        title.pack(pady=10)
        
        # 版本信息
        version = ttk.Label(
            about_frame, 
            text="版本: 3.0",
            font=("Arial", 12)
        )
        version.pack(pady=5)
        
        # 作者信息
        author = ttk.Label(
            about_frame, 
            text="作者: Damian2012",
            font=("Arial", 12)
        )
        author.pack(pady=5)
        
        # 功能说明
        features = ttk.Label(
            about_frame, 
            text=(
                "功能说明:\n"
                "1. 召唤生物 - 快速生成各种生物\n"
                "2. 玩家管理 - 踢出、杀死、传送玩家等\n"
                "3. 快捷命令 - 常用命令一键执行\n"
                "4. 配置设置 - 自定义快捷键和延迟\n\n"
                "所有配置自动保存到 mctool.ini 文件"
            ),
            font=("Arial", 10),
            justify="left"
        )
        features.pack(pady=10, padx=20, anchor='w')
        
        # 使用提示
        tips = ttk.Label(
            about_frame, 
            text=(
                "使用提示:\n"
                "- 确保游戏在创造模式或开启作弊\n"
                "- 执行前切换到Minecraft窗口\n"
                "- 快捷键可自定义\n"
                "- 命令执行有延迟，请勿频繁操作"
            ),
            font=("Arial", 9),
            justify="left",
            foreground="blue"
        )
        tips.pack(pady=10, padx=20, anchor='w')
        
        # 版权信息
        copyright = ttk.Label(
            about_frame, 
            text="© 2023 Damian2012 - 版权所有",
            font=("Arial", 9),
            foreground="gray"
        )
        copyright.pack(side='bottom', pady=10)
    
    def update_creature_id(self, event=None):
        creature_name = self.creature_var.get()
        if creature_name in self.creatures:
            self.creature_id_var.set(self.creatures[creature_name])
    
    def update_player_command(self, event=None):
        cmd = self.player_cmd_var.get()
        target = self.get_target()
        
        if cmd == "踢出玩家":
            self.cmd_preview_var.set(f"/kick {target}")
        elif cmd == "杀死玩家":
            self.cmd_preview_var.set(f"/kill {target}")
        elif cmd == "传送到玩家":
            self.cmd_preview_var.set(f"/tp {target} @p")
        elif cmd == "传送到位置":
            self.cmd_preview_var.set(f"/tp {target} ~ ~ ~")
        elif cmd == "给予物品":
            self.cmd_preview_var.set(f"/give {target} minecraft:diamond 1")
        elif cmd == "赋予效果":
            self.cmd_preview_var.set(f"/effect give {target} minecraft:speed 30 1")
    
    def update_target_input(self, event=None):
        target = self.target_var.get()
        if "手动输入" in target:
            self.target_input_frame.pack(fill='x', pady=5, padx=10)
        else:
            self.target_input_frame.pack_forget()
        self.update_player_command()
    
    def get_target(self):
        target = self.target_var.get()
        if "手动输入" in target:
            return self.target_input_var.get() or "@p"
        elif "@p" in target:
            return "@p"
        elif "@a" in target:
            return "@a"
        elif "@r" in target:
            return "@r"
        elif "@s" in target:
            return "@s"
        return "@p"
    
    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
                if 'DEFAULT' in config:
                    for key in self.config:
                        if key in config['DEFAULT']:
                            if key in ['count', 'start_delay']:
                                self.config[key] = config['DEFAULT'].getint(key)
                            else:
                                self.config[key] = config['DEFAULT'][key]
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")
    
    def save_config(self):
        try:
            config = configparser.ConfigParser()
            config['DEFAULT'] = self.config.copy()
            
            # 更新当前配置
            self.config['hotkey_start'] = self.start_hk_var.get()
            self.config['hotkey_stop'] = self.stop_hk_var.get()
            self.config['start_delay'] = self.delay_var.get()
            
            config['DEFAULT'] = self.config
            
            with open(self.config_file, 'w') as f:
                config.write(f)
            
            # 重新注册热键
            self.register_hotkeys()
            
            self.config_status.config(text="配置保存成功!")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def register_hotkeys(self):
        try:
            keyboard.unhook_all()
            
            # 注册开始热键
            keyboard.add_hotkey(
                self.config['hotkey_start'], 
                lambda: self.start_action("hotkey")
            )
            
            # 注册停止热键
            keyboard.add_hotkey(
                self.config['hotkey_stop'], 
                self.stop_action
            )
            
            # 更新状态
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 0:  # 召唤生物标签页
                self.summon_status.config(text=f"状态: 就绪 - 快捷键已注册 ({self.config['hotkey_start']}/{self.config['hotkey_stop']})")
            elif current_tab == 2:  # 快捷命令标签页
                self.command_status.config(text=f"状态: 就绪 - 快捷键 {self.config['hotkey_start']} 可用")
        except Exception as e:
            messagebox.showerror("错误", f"注册热键失败: {str(e)}\n\n请尝试以管理员权限运行程序")
    
    def start_action(self, action_type):
        if self.is_running:
            return
            
        self.is_running = True
        self.stop_requested = False
        
        # 根据动作类型设置UI状态
        if action_type == "summon":
            self.summon_start_btn.config(state=tk.DISABLED)
            self.summon_stop_btn.config(state=tk.NORMAL)
            self.summon_progress_bar['value'] = 0
            self.summon_progress_bar['maximum'] = self.count_var.get()
            self.summon_progress_text.config(text="准备开始召唤...")
            self.summon_status.config(text=f"状态: {self.config['start_delay']}秒后开始召唤 - 请切换到游戏窗口!", foreground="red")
            threading.Thread(target=self.summon_creatures, daemon=True).start()
        
        elif action_type == "player":
            self.player_start_btn.config(state=tk.DISABLED)
            self.player_status.config(text=f"状态: {self.config['start_delay']}秒后执行命令 - 请切换到游戏窗口!", foreground="red")
            threading.Thread(target=self.execute_player_command, daemon=True).start()
        
        elif action_type == "command":
            self.command_start_btn.config(state=tk.DISABLED)
            self.command_status.config(text=f"状态: {self.config['start_delay']}秒后执行命令 - 请切换到游戏窗口!", foreground="red")
            threading.Thread(target=self.execute_quick_command, daemon=True).start()
        
        elif action_type == "hotkey":
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 0:  # 召唤生物标签页
                self.start_action("summon")
            elif current_tab == 2:  # 快捷命令标签页
                self.start_action("command")
    
    def stop_action(self):
        if not self.is_running:
            return
            
        self.stop_requested = True
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # 召唤生物标签页
            self.summon_status.config(text="状态: 停止请求已发送...", foreground="orange")
    
    def summon_creatures(self):
        try:
            # 倒计时
            for i in range(self.config['start_delay'], 0, -1):
                self.summon_status.config(text=f"状态: {i}秒后开始召唤 - 请切换到游戏窗口!")
                time.sleep(1)
                if self.stop_requested:
                    break
            
            if self.stop_requested:
                self.summon_status.config(text="状态: 召唤已取消", foreground="orange")
                self.summon_progress_text.config(text="操作被用户取消")
                return
                
            total = self.count_var.get()
            self.summon_status.config(text=f"状态: 正在召唤生物... (0/{total})", foreground="red")
            
            # 获取生物ID
            creature_name = self.creature_var.get()
            creature_id = self.creatures.get(creature_name, "minecraft:zombie")
            
            for i in range(total):
                if self.stop_requested:
                    break
                
                # 模拟按键序列
                keyboard.press_and_release('t')  # 打开聊天框
                time.sleep(0.2)
                
                # 输入命令
                command = f"/summon {creature_id} {self.pos_var.get()}"
                keyboard.write(command)
                time.sleep(0.2)
                
                keyboard.press_and_release('enter')  # 发送命令
                time.sleep(0.2)
                
                # 更新进度
                current = i + 1
                self.summon_progress_bar['value'] = current
                self.summon_progress_text.config(text=f"已召唤: {current}/{total} 只生物")
                self.summon_status.config(text=f"状态: 正在召唤生物... ({current}/{total})")
                
                time.sleep(0.1)  # 短暂延迟
                
            if self.stop_requested:
                self.summon_status.config(text=f"状态: 召唤已停止! 已生成 {i} 只生物", foreground="orange")
                self.summon_progress_text.config(text=f"已停止 - 完成 {i}/{total}")
            else:
                self.summon_status.config(text=f"状态: 召唤完成! {total}只生物已生成", foreground="green")
                self.summon_progress_text.config(text=f"完成! {total}只生物已召唤")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错: {str(e)}")
        finally:
            self.is_running = False
            self.stop_requested = False
            self.summon_start_btn.config(state=tk.NORMAL)
            self.summon_stop_btn.config(state=tk.DISABLED)
    
    def execute_player_command(self):
        try:
            # 倒计时
            for i in range(self.config['start_delay'], 0, -1):
                self.player_status.config(text=f"状态: {i}秒后执行命令 - 请切换到游戏窗口!")
                time.sleep(1)
                if self.stop_requested:
                    break
            
            if self.stop_requested:
                self.player_status.config(text="状态: 命令执行已取消", foreground="orange")
                return
                
            # 获取命令
            cmd = self.player_cmd_var.get()
            target = self.get_target()
            full_command = ""
            
            if cmd == "踢出玩家":
                full_command = f"/kick {target}"
            elif cmd == "杀死玩家":
                full_command = f"/kill {target}"
            elif cmd == "传送到玩家":
                full_command = f"/tp {target} @p"
            elif cmd == "传送到位置":
                full_command = f"/tp {target} ~ ~ ~"
            elif cmd == "给予物品":
                full_command = f"/give {target} minecraft:diamond 1"
            elif cmd == "赋予效果":
                full_command = f"/effect give {target} minecraft:speed 30 1"
            
            # 执行命令
            keyboard.press_and_release('t')  # 打开聊天框
            time.sleep(0.3)
            keyboard.write(full_command)
            time.sleep(0.2)
            keyboard.press_and_release('enter')  # 发送命令
            
            self.player_status.config(text=f"状态: 命令执行完成!", foreground="green")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错: {str(e)}")
        finally:
            self.is_running = False
            self.stop_requested = False
            self.player_start_btn.config(state=tk.NORMAL)
    
    def execute_quick_command(self):
        try:
            # 倒计时
            for i in range(self.config['start_delay'], 0, -1):
                self.command_status.config(text=f"状态: {i}秒后执行命令 - 请切换到游戏窗口!")
                time.sleep(1)
                if self.stop_requested:
                    break
            
            if self.stop_requested:
                self.command_status.config(text="状态: 命令执行已取消", foreground="orange")
                return
                
            # 获取命令
            command = self.quick_cmd_var.get()
            if not command.startswith('/'):
                command = '/' + command
            
            # 执行命令
            keyboard.press_and_release('t')  # 打开聊天框
            time.sleep(0.3)
            keyboard.write(command)
            time.sleep(0.2)
            keyboard.press_and_release('enter')  # 发送命令
            
            self.command_status.config(text=f"状态: 命令执行完成!", foreground="green")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错: {str(e)}")
        finally:
            self.is_running = False
            self.stop_requested = False
            self.command_start_btn.config(state=tk.NORMAL)
    
    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出工具箱吗？"):
            try:
                keyboard.unhook_all()
            except:
                pass
            self.root.destroy()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MCToolbox(root)
    root.mainloop()
