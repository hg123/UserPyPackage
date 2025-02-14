import os
import sys
import json
import platform
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from PIL import Image
from argparse import ArgumentParser
import threading
import logging
from utils import update_code_list_by_local, update_code_list_by_local_force, get_code_in_code_list, input_activation_code

# 程序信息
program_name = "文件蜈蚣自动激活器"
version = "1.0.1"  # 更新版本号

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 系统设置
def setup_locale():
    system_type = platform.system()
    if system_type == "Darwin":  # macOS
        os.system("export LC_ALL=zh_CN.UTF-8 && clear")
    elif system_type == "Linux":
        os.system("locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8') && clear")
    else:  # Windows
        os.system("chcp 65001 && cls")

# 资源路径处理函数
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 资源路径
window_icon = resource_path("favicon.ico")
tray_icon = resource_path("icon.png")

# GUI 界面
def run_gui():
    root = create_main_window()
    root.withdraw()

    tray_thread = threading.Thread(target=start_tray_icon, args=(root,))
    tray_thread.daemon = True
    tray_thread.start()

    root.mainloop()

# 主程序窗口设置
def create_main_window():
    root = tk.Tk()
    root.title(program_name)
    root.iconbitmap(window_icon)

    width = 300
    height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    size = f'{width}x{height}+{x}+{y}'  # 使用 f-string 格式化字符串

    root.geometry(size)
    root.minsize(width, height)
    root.resizable(False, False)

    def show_activation_code_window(activation_code, root):
        def create_window():
            top = tk.Toplevel(root)
            top.title("激活码")
            top.iconbitmap(window_icon)

            text_box = tk.Text(top, height=4, width=40)
            text_box.insert(tk.END, activation_code)
            text_box.config(state=tk.DISABLED)
            text_box.pack(pady=10)

            tk.Button(top, text="关闭", command=top.destroy).pack(pady=5)

        root.after(0, create_window)

    def on_update_codes():
        try:
            update_code_list_by_local(".")
            messagebox.showinfo("更新成功", "激活码列表已更新")
        except Exception as e:
            logging.error(f"更新激活码列表失败: {e}")
            messagebox.showerror("更新失败", f"更新激活码列表失败: {e}")

    def on_get_codes():
        activation_code = get_code_in_code_list('.')
        if activation_code:
            show_activation_code_window(activation_code, root)
        else:
            messagebox.showwarning("激活码获取失败", "未获取到有效激活码, 请更新激活码列表")

    def on_input_codes():
        activation_code = get_code_in_code_list('.')
        if activation_code:
            isOk = input_activation_code("文件蜈蚣 - 激活码", activation_code)
            if not isOk:
                messagebox.showinfo("激活码填写失败", "未找到标题为 '文件蜈蚣 - 激活码' 的窗口")
        else:
            messagebox.showwarning("激活码获取失败", "未获取到有效激活码, 请更新激活码列表")

    def on_window_minimized(event):
        root.withdraw()

    root.bind("<Unmap>", on_window_minimized)

    def on_close():
        root.withdraw()
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_close)

    font = ("微软雅黑", 14)

    tk.Label(root, text=program_name, font=font).pack(pady=10)
    tk.Button(root, text="更新激活码", font=font, command=on_update_codes).pack(pady=10)
    tk.Button(root, text="获取激活码", font=font, command=on_get_codes).pack(pady=10)
    tk.Button(root, text="填入激活码", font=font, command=on_input_codes).pack(pady=10)

    return root

# 托盘图标功能
def start_tray_icon(root):
    def show_main_window(icon, item):
        root.deiconify()
        root.update()
        root.lift()
        root.focus_force()
        root.update_idletasks()  # 刷新窗口

    def hide_main_window(icon, item):
        root.withdraw()
        root.update_idletasks()

    def exit_program(icon, item):
        icon.stop()
        root.destroy()

    menu = Menu(
        MenuItem("显示主程序", show_main_window),
        MenuItem("隐藏主程序", hide_main_window),
        MenuItem("退出", exit_program)
    )
    icon_image = Image.open(tray_icon)
    icon = Icon("文件蜈蚣自动激活器", icon=icon_image, menu=menu)
    icon.run()

# 命令行模式
def run_command_line(args):
    setup_locale()

    if args.force and not args.update:
        parser.error("'-f' 选项只能与 '-u' 选项一起使用")
        sys.exit(0)

    if args.update:
        try:
            if args.force:
                update_code_list_by_local_force(executable_dir)
            else:
                update_code_list_by_local(executable_dir)
        except Exception as e:
            logging.error(f"更新激活码列表失败: {e}")
            print(f"更新激活码列表失败: {e}") # 同时在控制台输出错误信息

    if args.code:
        activation_codes = get_code_in_code_list(executable_dir)
        print(f"激活码: {activation_codes}")

    if args.version:
        print("版本号", version)

# 命令行参数解析
def parse_args():
    parser = ArgumentParser(description="文件蜈蚣自动激活器", epilog="直接运行程序以显示用户界面")

    command_group = parser.add_argument_group("命令行参数")
    command_group.add_argument("-c", "--code", action="store_true", help="获取激活码")
    command_group.add_argument("-v", "--version", action="store_true", help="版本号")

    update_group = parser.add_argument_group("更新参数")
    update_group.add_argument("-u", "--update", action="store_true", help="更新激活码列表")
    update_group._group_actions.append(parser._actions.pop()) # 将-f从主参数组中移除

    force_update_group = parser.add_mutually_exclusive_group() # 创建互斥组
    force_update_group.add_argument("-f", "--force", action="store_true", help="强制更新激活码列表")

    args = parser.parse_args()

    if len(sys.argv) > 1:
        run_command_line(args)
    else:
        run_gui()

# 程序入口
if __name__ == "__main__":
    parse_args()
