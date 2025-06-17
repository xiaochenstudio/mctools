import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import keyboard
import configparser
import os
import json
from tkinter import font as tkfont
import time
import sys

class MinecraftToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 工具箱")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # 设置窗口置顶
        self.root.attributes('-topmost', True)
        
        # 配置文件和名单路径
        self.config_file = "mc_toolbox.ini"
        self.player_lists_dir = "player_lists"
        
        # 创建玩家名单目录
        if not os.path.exists(self.player_lists_dir):
            os.makedirs(self.player_lists_dir)
        
        # 默认配置
        self.default_config = {
            'hotkey_start': 'shift+m',
            'hotkey_stop': 'shift+k',
            'last_player_list': '',
            'last_creature': 'minecraft:zombie',
            'last_command': '/summon',
            'last_position': '~ ~1 ~',
            'last_count': '10',
            'last_target': '@p'
        }
        
        # 加载配置
        self.config = self.default_config.copy()
        self.load_config()
        
        # 生物列表
        self.creatures = self.load_creature_list()
        
        # 玩家名单
        self.player_lists = {}
        self.current_player_list = []
        self.load_player_lists()
        
        # 运行状态
        self.is_running = False
        self.stop_requested = False
        
        # 创建界面
        self.create_widgets()
        
        # 注册热键
        self.register_hotkeys()
        
        # 退出处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_creature_list(self):
        # 加载Minecraft生物列表
        creatures = [
            'minecraft:zombie', 'minecraft:skeleton', 'minecraft:creeper', 
            'minecraft:spider', 'minecraft:enderman', 'minecraft:witch',
            'minecraft:blaze', 'minecraft:ghast', 'minecraft:slime',
            'minecraft:magma_cube', 'minecraft:bat', 'minecraft:chicken',
            'minecraft:cow', 'minecraft:pig', 'minecraft:sheep',
            'minecraft:wolf', 'minecraft:ocelot', 'minecraft:horse',
            'minecraft:donkey', 'minecraft:mule', 'minecraft:rabbit',
            'minecraft:polar_bear', 'minecraft:llama', 'minecraft:parrot',
            'minecraft:villager', 'minecraft:iron_golem', 'minecraft:snow_golem',
            'minecraft:ender_dragon', 'minecraft:wither', 'minecraft:shulker',
            'minecraft:guardian', 'minecraft:elder_guardian', 'minecraft:endermite',
            'minecraft:silverfish', 'minecraft:vex', 'minecraft:evoker',
            'minecraft:vindicator', 'minecraft:illusioner', 'minecraft:phantom',
            'minecraft:drowned', 'minecraft:husk', 'minecraft:stray',
            'minecraft:zombie_villager', 'minecraft:pillager', 'minecraft:ravager',
            'minecraft:trader_llama', 'minecraft:wandering_trader', 'minecraft:fox',
            'minecraft:panda', 'minecraft:bee', 'minecraft:hoglin',
            'minecraft:zoglin', 'minecraft:piglin', 'minecraft:piglin_brute',
            'minecraft:strider', 'minecraft:turtle', 'minecraft:dolphin',
            'minecraft:cod', 'minecraft:salmon', 'minecraft:pufferfish',
            'minecraft:tropical_fish', 'minecraft:squid', 'minecraft:glow_squid',
            'minecraft:axolotl', 'minecraft:goat', 'minecraft:warden',
            'minecraft:frog', 'minecraft:tadpole', 'minecraft:allay',
            'minecraft:camel', 'minecraft:sniffer'
        ]
        return sorted(creatures)
    
    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
                if 'DEFAULT' in config:
                    for key in self.default_config:
                        if key in config['DEFAULT']:
                            self.config[key] = config['DEFAULT'][key]
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")
    
    def save_config(self):
        try:
            config = configparser.ConfigParser()
            config['DEFAULT'] = self.config
            
            with open(self.config_file, 'w') as f:
                config.write(f)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            return False
    
    def load_player_lists(self):
        self.player_lists = {}
        if os.path.exists(self.player_lists_dir):
            for filename in os.listdir(self.player_lists_dir):
                if filename.endswith('.json'):
                    list_name = filename[:-5]
                    try:
                        with open(os.path.join(self.player_lists_dir, filename), 'r') as f:
                            self.player_lists[list_name] = json.load(f)
                    except:
                        pass
        
        # 加载上次使用的名单
        if self.config['last_player_list'] and self.config['last_player_list'] in self.player_lists:
            self.current_player_list = self.player_lists[self.config['last_player_list']]
        else:
            self.current_player_list = []
    
    def save_player_list(self, list_name):
        try:
            if not list_name:
                return False
                
            self.player_lists[list_name] = self.current_player_list
            with open(os.path.join(self.player_lists_dir, f"{list_name}.json"), 'w') as f:
                json.dump(self.current_player_list, f)
            
            self.config['last_player_list'] = list_name
            self.save_config()
            self.update_player_list_menu()
            
            messagebox.showinfo("成功", f"玩家名单 '{list_name}' 已保存!")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存玩家名单失败: {str(e)}")
            return False
    
    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        title_frame = tk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_font = tkfont.Font(size=16, weight='bold')
        tk.Label(
            title_frame, 
            text="Minecraft 工具箱", 
            font=title_font,
            fg="dark green"
        ).pack(side=tk.LEFT)
        
        tk.Button(
            title_frame,
            text="关于",
            command=self.show_about,
            width=8
        ).pack(side=tk.RIGHT)
        
        # 选项卡
        tab_control = ttk.Notebook(main_frame)
        
        # 召唤生物选项卡
        summon_tab = ttk.Frame(tab_control)
        self.create_summon_tab(summon_tab)
        tab_control.add(summon_tab, text="召唤生物")
        
        # 玩家管理选项卡
        player_tab = ttk.Frame(tab_control)
        self.create_player_tab(player_tab)
        tab_control.add(player_tab, text="玩家管理")
        
        # 命令选项卡
        command_tab = ttk.Frame(tab_control)
        self.create_command_tab(command_tab)
        tab_control.add(command_tab, text="快捷命令")
        
        tab_control.pack(expand=1, fill="both")
        
        # 状态栏
        self.status = tk.Label(
            main_frame,
            text="状态: 就绪",
            font=('Arial', 10, 'bold'),
            fg="blue",
            anchor="w"
        )
        self.status.pack(fill=tk.X, pady=(5, 0))
    
    def create_summon_tab(self, parent):
        # 召唤生物选项卡内容
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 生物选择
        creature_frame = ttk.LabelFrame(frame, text="生物选择")
        creature_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(creature_frame, text="生物类型:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.creature_var = tk.StringVar(value=self.config['last_creature'])
        self.creature_combo = ttk.Combobox(
            creature_frame, 
            textvariable=self.creature_var,
            values=self.creatures,
            state="readonly",
            width=30
        )
        self.creature_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 命令设置
        command_frame = ttk.LabelFrame(frame, text="召唤设置")
        command_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(command_frame, text="命令:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.command_var = tk.StringVar(value=self.config['last_command'])
        command_options = ['/summon']
        self.command_menu = ttk.Combobox(
            command_frame,
            textvariable=self.command_var,
            values=command_options,
            state="readonly",
            width=15
        )
        self.command_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(command_frame, text="位置:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pos_var = tk.StringVar(value=self.config['last_position'])
        ttk.Entry(command_frame, textvariable=self.pos_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(command_frame, text="数量:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.count_var = tk.IntVar(value=int(self.config['last_count']))
        ttk.Spinbox(command_frame, from_=1, to=1000, textvariable=self.count_var, width=5).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # 快捷键设置
        hotkey_frame = ttk.LabelFrame(frame, text="快捷键设置")
        hotkey_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(hotkey_frame, text="开始召唤:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_hk_var = tk.StringVar(value=self.config['hotkey_start'])
        ttk.Entry(hotkey_frame, textvariable=self.start_hk_var, width=15).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(hotkey_frame, text="停止召唤:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.stop_hk_var = tk.StringVar(value=self.config['hotkey_stop'])
        ttk.Entry(hotkey_frame, textvariable=self.stop_hk_var, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 进度条
        progress_frame = ttk.LabelFrame(frame, text="进度")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=100, 
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_text = ttk.Label(
            progress_frame,
            text="等待开始...",
            anchor="center"
        )
        self.progress_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="开始召唤",
            command=self.start_summoning,
            style='Accent.TButton'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="停止召唤",
            command=self.stop_summoning,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="保存设置",
            command=self.save_summon_settings
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_player_tab(self, parent):
        # 玩家管理选项卡内容
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 玩家名单选择
        list_frame = ttk.LabelFrame(frame, text="玩家名单管理")
        list_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(list_frame, text="选择名单:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.player_list_var = tk.StringVar(value=self.config['last_player_list'])
        self.player_list_menu = ttk.Combobox(
            list_frame,
            textvariable=self.player_list_var,
            state="readonly",
            width=25
        )
        self.player_list_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.update_player_list_menu()
        
        ttk.Button(
            list_frame,
            text="加载名单",
            command=self.load_selected_player_list,
            width=10
        ).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(
            list_frame,
            text="新建名单",
            command=self.create_new_player_list,
            width=10
        ).grid(row=0, column=3, padx=5, pady=5)
        
        # 玩家列表
        player_list_frame = ttk.LabelFrame(frame, text="玩家列表")
        player_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 列表和滚动条
        scrollbar = ttk.Scrollbar(player_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.player_listbox = tk.Listbox(
            player_list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED,
            height=10
        )
        self.player_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.player_listbox.yview)
        
        # 更新列表显示
        self.update_player_listbox()
        
        # 玩家操作按钮
        player_btn_frame = ttk.Frame(player_list_frame)
        player_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            player_btn_frame,
            text="添加玩家",
            command=self.add_player,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            player_btn_frame,
            text="删除选中",
            command=self.remove_selected_players,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            player_btn_frame,
            text="清空列表",
            command=self.clear_player_list,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            player_btn_frame,
            text="保存名单",
            command=self.save_current_player_list,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_command_tab(self, parent):
        # 快捷命令选项卡内容
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 命令选择
        cmd_frame = ttk.LabelFrame(frame, text="选择命令")
        cmd_frame.pack(fill=tk.X, pady=5)
        
        self.cmd_var = tk.StringVar()
        self.cmd_selector = ttk.Combobox(
            cmd_frame,
            textvariable=self.cmd_var,
            values=['/kick', '/kill', '/tp', '/give', '/effect'],
            state="readonly",
            width=15
        )
        self.cmd_selector.pack(side=tk.LEFT, padx=5, pady=5)
        self.cmd_selector.bind("<<ComboboxSelected>>", self.update_command_ui)
        
        # 命令参数框架
        self.cmd_params_frame = ttk.Frame(frame)
        self.cmd_params_frame.pack(fill=tk.X, pady=5)
        
        # 默认显示kick命令UI
        self.create_kick_ui()
        
        # 执行按钮
        ttk.Button(
            frame,
            text="执行命令",
            command=self.execute_command,
            style='Accent.TButton'
        ).pack(pady=10)
    
    def create_kick_ui(self):
        # 清除现有控件
        for widget in self.cmd_params_frame.winfo_children():
            widget.destroy()
        
        # 创建kick命令UI
        ttk.Label(self.cmd_params_frame, text="踢出玩家:").pack(side=tk.LEFT, padx=5)
        
        self.target_var = tk.StringVar(value=self.config['last_target'])
        target_frame = ttk.Frame(self.cmd_params_frame)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            target_frame,
            text="@a (所有玩家)",
            variable=self.target_var,
            value="@a"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@p (最近玩家)",
            variable=self.target_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@r (随机玩家)",
            variable=self.target_var,
            value="@r"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="指定玩家",
            variable=self.target_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.player_select_var = tk.StringVar()
        self.player_select_combo = ttk.Combobox(
            target_frame,
            textvariable=self.player_select_var,
            width=20
        )
        self.player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
        
        ttk.Label(self.cmd_params_frame, text="原因:").pack(side=tk.LEFT, padx=5)
        self.reason_var = tk.StringVar(value="违反规则")
        ttk.Entry(self.cmd_params_frame, textvariable=self.reason_var, width=30).pack(side=tk.LEFT, padx=5)
    
    def create_kill_ui(self):
        # 清除现有控件
        for widget in self.cmd_params_frame.winfo_children():
            widget.destroy()
        
        # 创建kill命令UI
        ttk.Label(self.cmd_params_frame, text="杀死玩家:").pack(side=tk.LEFT, padx=5)
        
        self.target_var = tk.StringVar(value=self.config['last_target'])
        target_frame = ttk.Frame(self.cmd_params_frame)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            target_frame,
            text="@a (所有玩家)",
            variable=self.target_var,
            value="@a"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@p (最近玩家)",
            variable=self.target_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@r (随机玩家)",
            variable=self.target_var,
            value="@r"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="指定玩家",
            variable=self.target_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.player_select_var = tk.StringVar()
        self.player_select_combo = ttk.Combobox(
            target_frame,
            textvariable=self.player_select_var,
            width=20
        )
        self.player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
    
    def create_tp_ui(self):
        # 清除现有控件
        for widget in self.cmd_params_frame.winfo_children():
            widget.destroy()
        
        # 创建tp命令UI
        ttk.Label(self.cmd_params_frame, text="传送玩家:").pack(side=tk.LEFT, padx=5)
        
        self.tp_source_var = tk.StringVar(value=self.config['last_target'])
        source_frame = ttk.Frame(self.cmd_params_frame)
        source_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            source_frame,
            text="@p (自己)",
            variable=self.tp_source_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            source_frame,
            text="指定玩家",
            variable=self.tp_source_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.tp_player_select_var = tk.StringVar()
        self.tp_player_select_combo = ttk.Combobox(
            source_frame,
            textvariable=self.tp_player_select_var,
            width=20
        )
        self.tp_player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
        
        ttk.Label(self.cmd_params_frame, text="到:").pack(side=tk.LEFT, padx=5)
        
        self.tp_dest_var = tk.StringVar(value="@p")
        dest_frame = ttk.Frame(self.cmd_params_frame)
        dest_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            dest_frame,
            text="@p (最近玩家)",
            variable=self.tp_dest_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            dest_frame,
            text="指定玩家",
            variable=self.tp_dest_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.tp_dest_player_select_var = tk.StringVar()
        self.tp_dest_player_select_combo = ttk.Combobox(
            dest_frame,
            textvariable=self.tp_dest_player_select_var,
            width=20
        )
        self.tp_dest_player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
        
        ttk.Radiobutton(
            dest_frame,
            text="坐标",
            variable=self.tp_dest_var,
            value="coords"
        ).pack(side=tk.LEFT, padx=5)
        
        self.tp_coords_var = tk.StringVar(value="~ ~ ~")
        ttk.Entry(dest_frame, textvariable=self.tp_coords_var, width=20).pack(side=tk.LEFT, padx=5)
    
    def create_give_ui(self):
        # 清除现有控件
        for widget in self.cmd_params_frame.winfo_children():
            widget.destroy()
        
        # 创建give命令UI
        ttk.Label(self.cmd_params_frame, text="给予玩家:").pack(side=tk.LEFT, padx=5)
        
        self.give_target_var = tk.StringVar(value=self.config['last_target'])
        target_frame = ttk.Frame(self.cmd_params_frame)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            target_frame,
            text="@a (所有玩家)",
            variable=self.give_target_var,
            value="@a"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@p (最近玩家)",
            variable=self.give_target_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="指定玩家",
            variable=self.give_target_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.give_player_select_var = tk.StringVar()
        self.give_player_select_combo = ttk.Combobox(
            target_frame,
            textvariable=self.give_player_select_var,
            width=20
        )
        self.give_player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
        
        ttk.Label(self.cmd_params_frame, text="物品:").pack(side=tk.LEFT, padx=5)
        self.give_item_var = tk.StringVar(value="minecraft:diamond")
        ttk.Entry(self.cmd_params_frame, textvariable=self.give_item_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.cmd_params_frame, text="数量:").pack(side=tk.LEFT, padx=5)
        self.give_count_var = tk.IntVar(value=1)
        ttk.Spinbox(self.cmd_params_frame, from_=1, to=64, textvariable=self.give_count_var, width=5).pack(side=tk.LEFT, padx=5)
    
    def create_effect_ui(self):
        # 清除现有控件
        for widget in self.cmd_params_frame.winfo_children():
            widget.destroy()
        
        # 创建effect命令UI
        ttk.Label(self.cmd_params_frame, text="效果目标:").pack(side=tk.LEFT, padx=5)
        
        self.effect_target_var = tk.StringVar(value=self.config['last_target'])
        target_frame = ttk.Frame(self.cmd_params_frame)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Radiobutton(
            target_frame,
            text="@a (所有玩家)",
            variable=self.effect_target_var,
            value="@a"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="@p (最近玩家)",
            variable=self.effect_target_var,
            value="@p"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            target_frame,
            text="指定玩家",
            variable=self.effect_target_var,
            value="player"
        ).pack(side=tk.LEFT, padx=5)
        
        self.effect_player_select_var = tk.StringVar()
        self.effect_player_select_combo = ttk.Combobox(
            target_frame,
            textvariable=self.effect_player_select_var,
            width=20
        )
        self.effect_player_select_combo.pack(side=tk.LEFT, padx=5)
        self.update_player_select_combo()
        
        ttk.Label(self.cmd_params_frame, text="效果:").pack(side=tk.LEFT, padx=5)
        self.effect_type_var = tk.StringVar(value="minecraft:speed")
        effect_types = [
            'minecraft:speed', 'minecraft:slowness', 'minecraft:haste', 
            'minecraft:mining_fatigue', 'minecraft:strength', 'minecraft:instant_health',
            'minecraft:instant_damage', 'minecraft:jump_boost', 'minecraft:nausea',
            'minecraft:regeneration', 'minecraft:resistance', 'minecraft:fire_resistance',
            'minecraft:water_breathing', 'minecraft:invisibility', 'minecraft:blindness',
            'minecraft:night_vision', 'minecraft:hunger', 'minecraft:weakness',
            'minecraft:poison', 'minecraft:wither', 'minecraft:health_boost',
            'minecraft:absorption', 'minecraft:saturation', 'minecraft:glowing',
            'minecraft:levitation', 'minecraft:luck', 'minecraft:bad_luck',
            'minecraft:slow_falling', 'minecraft:conduit_power', 'minecraft:dolphins_grace',
            'minecraft:bad_omen', 'minecraft:hero_of_the_village'
        ]
        ttk.Combobox(
            self.cmd_params_frame,
            textvariable=self.effect_type_var,
            values=effect_types,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.cmd_params_frame, text="时间(秒):").pack(side=tk.LEFT, padx=5)
        self.effect_duration_var = tk.IntVar(value=30)
        ttk.Spinbox(self.cmd_params_frame, from_=1, to=1000000, textvariable=self.effect_duration_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.cmd_params_frame, text="强度:").pack(side=tk.LEFT, padx=5)
        self.effect_amplifier_var = tk.IntVar(value=0)
        ttk.Spinbox(self.cmd_params_frame, from_=0, to=255, textvariable=self.effect_amplifier_var, width=5).pack(side=tk.LEFT, padx=5)
    
    def update_command_ui(self, event=None):
        cmd = self.cmd_var.get()
        if cmd == '/kick':
            self.create_kick_ui()
        elif cmd == '/kill':
            self.create_kill_ui()
        elif cmd == '/tp':
            self.create_tp_ui()
        elif cmd == '/give':
            self.create_give_ui()
        elif cmd == '/effect':
            self.create_effect_ui()
    
    def update_player_list_menu(self):
        lists = list(self.player_lists.keys())
        self.player_list_menu['values'] = lists
        if lists and self.config['last_player_list'] in lists:
            self.player_list_var.set(self.config['last_player_list'])
        elif lists:
            self.player_list_var.set(lists[0])
    
    def update_player_listbox(self):
        self.player_listbox.delete(0, tk.END)
        for player in self.current_player_list:
            self.player_listbox.insert(tk.END, player)
    
    def update_player_select_combo(self):
        players = self.current_player_list.copy()
        players.extend(['@a', '@p', '@r'])
        
        # 安全地更新所有可能的下拉框
        comboboxes = [
            getattr(self, 'player_select_combo', None),
            getattr(self, 'tp_player_select_combo', None),
            getattr(self, 'tp_dest_player_select_combo', None),
            getattr(self, 'give_player_select_combo', None),
            getattr(self, 'effect_player_select_combo', None)
        ]
        
        for combo in comboboxes:
            if combo and combo.winfo_exists():  # 检查控件是否存在
                try:
                    combo['values'] = players
                except tk.TclError:
                    pass
    
    def load_selected_player_list(self):
        list_name = self.player_list_var.get()
        if list_name and list_name in self.player_lists:
            self.current_player_list = self.player_lists[list_name]
            self.update_player_listbox()
            self.update_player_select_combo()
            self.config['last_player_list'] = list_name
            self.save_config()
            self.status.config(text=f"状态: 已加载玩家名单 '{list_name}'", fg="green")
        else:
            self.status.config(text="状态: 无法加载玩家名单", fg="red")
    
    def create_new_player_list(self):
        list_name = simpledialog.askstring("新建玩家名单", "输入新名单名称:")
        if list_name:
            if list_name in self.player_lists:
                messagebox.showwarning("警告", "名单已存在!")
            else:
                self.player_lists[list_name] = []
                self.current_player_list = []
                self.update_player_listbox()
                self.update_player_list_menu()
                self.player_list_var.set(list_name)
                self.save_player_list(list_name)
                self.status.config(text=f"状态: 已创建新名单 '{list_name}'", fg="green")
    
    def save_current_player_list(self):
        list_name = self.player_list_var.get()
        if list_name:
            if self.save_player_list(list_name):
                self.status.config(text=f"状态: 已保存玩家名单 '{list_name}'", fg="green")
        else:
            self.create_new_player_list()
    
    def add_player(self):
        player = simpledialog.askstring("添加玩家", "输入玩家名称:")
        if player:
            if player not in self.current_player_list:
                self.current_player_list.append(player)
                self.update_player_listbox()
                self.update_player_select_combo()
                self.status.config(text=f"状态: 已添加玩家 '{player}'", fg="green")
            else:
                self.status.config(text=f"状态: 玩家 '{player}' 已存在", fg="orange")
    
    def remove_selected_players(self):
        selected = self.player_listbox.curselection()
        if selected:
            players_removed = []
            for index in reversed(selected):
                player = self.current_player_list.pop(index)
                players_removed.append(player)
            self.update_player_listbox()
            self.update_player_select_combo()
            self.status.config(text=f"状态: 已移除 {len(players_removed)} 名玩家", fg="green")
    
    def clear_player_list(self):
        if messagebox.askyesno("确认", "确定要清空当前玩家名单吗?"):
            self.current_player_list = []
            self.update_player_listbox()
            self.update_player_select_combo()
            self.status.config(text="状态: 玩家名单已清空", fg="green")
    
    def register_hotkeys(self):
        try:
            keyboard.unhook_all()
            
            # 注册开始热键
            keyboard.add_hotkey(
                self.config['hotkey_start'], 
                self.start_summoning
            )
            
            # 注册停止热键
            keyboard.add_hotkey(
                self.config['hotkey_stop'], 
                self.stop_summoning
            )
            
            self.status.config(text="状态: 就绪 - 快捷键已注册", fg="blue")
        except Exception as e:
            messagebox.showerror("错误", f"注册热键失败: {str(e)}\n\n请尝试以管理员权限运行程序")
            self.status.config(text="状态: 快捷键注册失败", fg="red")
    
    def save_summon_settings(self):
        self.config['hotkey_start'] = self.start_hk_var.get()
        self.config['hotkey_stop'] = self.stop_hk_var.get()
        self.config['last_creature'] = self.creature_var.get()
        self.config['last_command'] = self.command_var.get()
        self.config['last_position'] = self.pos_var.get()
        self.config['last_count'] = str(self.count_var.get())
        
        if self.save_config():
            self.register_hotkeys()
            self.status.config(text="状态: 召唤设置已保存", fg="green")
    
    def start_summoning(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.stop_requested = False
        self.status.config(text="状态: 开始召唤 - 请切换到Minecraft窗口!", fg="red")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = self.count_var.get()
        self.progress_text.config(text="等待开始...")
        
        # 在新线程中执行召唤操作
        threading.Thread(target=self.summon_creatures, daemon=True).start()
    
    def stop_summoning(self):
        if not self.is_running:
            return
            
        self.stop_requested = True
        self.status.config(text="状态: 停止请求已发送...", fg="orange")
    
    def summon_creatures(self):
        try:
            # 给用户3秒时间切换到游戏窗口
            for i in range(3, 0, -1):
                self.status.config(text=f"状态: {i}秒后开始召唤 - 请切换到Minecraft窗口!")
                time.sleep(1)
                if self.stop_requested:
                    break
            
            if self.stop_requested:
                self.status.config(text="状态: 召唤已取消", fg="orange")
                self.progress_text.config(text="操作被用户取消")
                return
                
            total = self.count_var.get()
            self.status.config(text=f"状态: 正在召唤生物... (0/{total})", fg="red")
            
            creature = self.creature_var.get()
            position = self.pos_var.get()
            
            for i in range(total):
                if self.stop_requested:
                    break
                
                # 模拟按键序列
                keyboard.press_and_release('t')  # 打开聊天框
                time.sleep(0.1)
                
                # 输入命令
                command = f"{self.command_var.get()} {creature} {position}"
                keyboard.write(command)
                time.sleep(0.1)
                
                keyboard.press_and_release('enter')  # 发送命令
                time.sleep(0.1)
                
                # 更新进度
                current = i + 1
                self.progress_bar['value'] = current
                self.progress_text.config(text=f"已召唤: {current}/{total} 只生物")
                self.status.config(text=f"状态: 正在召唤生物... ({current}/{total})")
                
                time.sleep(0.1)  # 最小延迟
            
            if self.stop_requested:
                self.status.config(text=f"状态: 召唤已停止! 已生成 {i} 只生物", fg="orange")
                self.progress_text.config(text=f"已停止 - 完成 {i}/{total}")
            else:
                self.status.config(text=f"状态: 召唤完成! {total}只生物已生成", fg="green")
                self.progress_text.config(text=f"完成! {total}只生物已召唤")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错: {str(e)}")
            self.status.config(text="状态: 召唤失败", fg="red")
        finally:
            self.is_running = False
            self.stop_requested = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def execute_command(self):
        cmd = self.cmd_var.get()
        try:
            if cmd == '/kick':
                self.execute_kick_command()
            elif cmd == '/kill':
                self.execute_kill_command()
            elif cmd == '/tp':
                self.execute_tp_command()
            elif cmd == '/give':
                self.execute_give_command()
            elif cmd == '/effect':
                self.execute_effect_command()
            
            self.status.config(text=f"状态: 命令执行成功!", fg="green")
        except Exception as e:
            messagebox.showerror("错误", f"执行命令失败: {str(e)}")
            self.status.config(text=f"状态: 命令执行失败", fg="red")
    
    def execute_kick_command(self):
        target = self.target_var.get()
        if target == "player":
            target = self.player_select_var.get()
            if not target:
                raise ValueError("请选择玩家")
        
        reason = self.reason_var.get()
        command = f"{self.cmd_var.get()} {target} {reason}"
        self.send_command(command)
    
    def execute_kill_command(self):
        target = self.target_var.get()
        if target == "player":
            target = self.player_select_var.get()
            if not target:
                raise ValueError("请选择玩家")
        
        command = f"{self.cmd_var.get()} {target}"
        self.send_command(command)
    
    def execute_tp_command(self):
        source = self.tp_source_var.get()
        if source == "player":
            source = self.tp_player_select_var.get()
            if not source:
                raise ValueError("请选择源玩家")
        
        dest = self.tp_dest_var.get()
        if dest == "player":
            dest = self.tp_dest_player_select_var.get()
            if not dest:
                raise ValueError("请选择目标玩家")
        elif dest == "coords":
            dest = self.tp_coords_var.get()
        else:  # 选择器
            dest = dest
        
        command = f"{self.cmd_var.get()} {source} {dest}"
        self.send_command(command)
    
    def execute_give_command(self):
        target = self.give_target_var.get()
        if target == "player":
            target = self.give_player_select_var.get()
            if not target:
                raise ValueError("请选择玩家")
        
        item = self.give_item_var.get()
        count = self.give_count_var.get()
        command = f"{self.cmd_var.get()} {target} {item} {count}"
        self.send_command(command)
    
    def execute_effect_command(self):
        target = self.effect_target_var.get()
        if target == "player":
            target = self.effect_player_select_var.get()
            if not target:
                raise ValueError("请选择玩家")
        
        effect = self.effect_type_var.get()
        duration = self.effect_duration_var.get()
        amplifier = self.effect_amplifier_var.get()
        command = f"{self.cmd_var.get()} {target} {effect} {duration} {amplifier}"
        self.send_command(command)
    
    def send_command(self, command):
        # 模拟按键序列发送命令
        keyboard.press_and_release('t')  # 打开聊天框
        time.sleep(0.1)
        keyboard.write(command)
        time.sleep(0.1)
        keyboard.press_and_release('enter')  # 发送命令
        time.sleep(0.1)
    
    def show_about(self):
        about_text = (
            "Minecraft 工具箱\n"
            "版本: 2.0\n"
            "作者: Damian2012\n\n"
            "功能说明:\n"
            "1. 召唤各种Minecraft生物\n"
            "2. 管理玩家名单\n"
            "3. 执行快捷命令(kick/kill/tp等)\n"
            "4. 自定义快捷键\n\n"
            "使用提示:\n"
            "- 确保Minecraft窗口处于活动状态\n"
            "- 游戏需开启作弊模式\n"
            "- 可能需要管理员权限运行"
        )
        messagebox.showinfo("关于", about_text)
    
    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出工具箱吗？"):
            try:
                keyboard.unhook_all()
            except:
                pass
            self.save_config()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # 设置主题样式
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', foreground='white', background='#2b7bb9')
    
    app = MinecraftToolbox(root)
    root.mainloop()