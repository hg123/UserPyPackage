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
from utils import update_code_list_by_local, update_code_list_by_local_force, get_code_in_code_list, input_activation_code

program_name = "文件蜈蚣自动激活器"
version = "1.0.0"

# 系统设置
def setup_locale():
    system_type = platform.system()
    if system_type == "darwin":
        os.system("export LC_ALL=zh_CN.UTF-8 && clear")
    elif system_type == "linux":
        os.system("locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8') && clear")
    else:
        os.system("chcp 65001 && cls")

# 确定资源路径的通用代码
try:
    # 编译环境下使用 `__compiled__`
    executable_dir = __compiled__.containing_dir
except NameError:
    # 非编译环境下使用当前脚本所在目录
    executable_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# 资源路径
window_icon = os.path.join(executable_dir, "favicon.ico")
tray_icon = os.path.join(executable_dir, "icon.png")

# GUI界面
def run_gui():
    # 创建主窗口
    main_window = create_main_window()
    main_window.withdraw()  # 初始化时隐藏窗口（用户可以从托盘菜单显示）
    
    # 启动托盘图标功能，确保它在单独的线程中运行
    tray_thread = threading.Thread(target=start_tray_icon, args=(main_window,))
    tray_thread.daemon = True  # 确保主线程结束时，托盘线程也自动退出
    tray_thread.start()

    # 运行主窗口主循环
    main_window.mainloop()

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
    size = '{}x{}+{}+{}'.format(width, height, x, y)

    root.geometry(size)
    root.minsize(width, height)
    # 不允许缩放
    root.resizable(False, False)

    def show_activation_code_window(activation_code, root):
        # 使用 after 将窗口创建移至主线程
        def create_window():
            # 创建新的弹窗
            top = tk.Toplevel(root)
            top.title("激活码")
            top.iconbitmap(window_icon)
            
            # 创建一个可选择文本的 Text 组件
            text_box = tk.Text(top, height=4, width=40)
            text_box.insert(tk.END, activation_code)
            text_box.config(state=tk.DISABLED)  # 禁止编辑
            text_box.pack(pady=10)

            # 添加关闭按钮
            tk.Button(top, text="关闭", command=top.destroy).pack(pady=5)
        
        # 使用 after 将创建窗口的操作放入主线程
        root.after(0, create_window)
    
    # 更新激活码功能
    def on_update_codes():
        update_code_list_by_local(".")
        messagebox.showinfo("更新成功", "激活码列表已更新")
        

    # 获取激活码
    def on_get_codes():
        activation_code = get_code_in_code_list('.')
        if activation_code:
            show_activation_code_window(activation_code, root)
        else:
            messagebox.showwarning("激活码获取失败", "未获取到有效激活码, 请更新激活码列表")

    # 填写激活码
    def on_input_codes():
        activation_code = get_code_in_code_list('.')
        if activation_code:
            isOk = input_activation_code("文件蜈蚣 - 激活码", activation_code)
            if not isOk:
                messagebox.showinfo("激活码填写失败", "未找到标题为 '文件蜈蚣 - 激活码' 的窗口")
        else:
            messagebox.showwarning("激活码获取失败", "未获取到有效激活码, 请更新激活码列表")

    # 窗口最小化事件处理
    def on_window_minimized(event):
        root.withdraw()  # 隐藏窗口

    root.bind("<Unmap>", on_window_minimized)

    # 关闭按钮的事件处理
    def on_close():
        root.withdraw()  # 隐藏窗口，而不是销毁
        root.quit()  # 退出主循环

    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", on_close)

    font = ("微软雅黑", 14)

    # 主窗口内容
    tk.Label(root, text=program_name, font=font).pack(pady=10)
    tk.Button(root, text="更新激活码", font=font, command=on_update_codes).pack(pady=10)
    tk.Button(root, text="获取激活码", font=font, command=on_get_codes).pack(pady=10)
    tk.Button(root, text="填入激活码", font=font, command=on_input_codes).pack(pady=10)

    return root

# 托盘图标功能
def start_tray_icon(root):
    def show_main_window(icon, item):
        root.deiconify()  # 显示主窗口
        root.update()  # 立即刷新窗口内容
        root.lift()  # 将窗口置顶
        root.focus_force()  # 强制窗口获取焦点

    def hide_main_window(icon, item):
        root.withdraw()  # 隐藏主窗口
        root.update_idletasks()  # 刷新窗口

    def exit_program(icon, item):
        icon.stop()  # 停止托盘图标
        root.destroy()  # 销毁主窗口


    # 创建托盘图标菜单
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
        if args.force:
            # 强制更新激活码列表
            update_code_list_by_local_force(executable_dir)
        else:
            # 更新激活码列表
            update_code_list_by_local(executable_dir)


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
    update_group.add_argument("-f", "--force", action="store_true", help="强制更新激活码列表")

    args = parser.parse_args()

    if len(sys.argv) > 1:
        run_command_line(args)  # 命令行模式
    else:
        run_gui()

# 程序入口
if __name__ == "__main__":
    parse_args()