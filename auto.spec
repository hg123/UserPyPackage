# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 1. 导入必要的模块
import os
import sys

# 2. 定义资源路径函数
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 3. 分析部分
a = Analysis(
    ['main.py'],  # 主脚本文件
    pathex=[],  # 搜索路径，用于查找模块，如果你的项目有额外的模块不在标准库或虚拟环境中，需要在此处添加路径
    binaries=[],  # 二进制文件，如果你的项目使用了 C 扩展或其他二进制文件，需要在此处添加
    datas=[  # 资源文件
        (resource_path('favicon.ico'), '.'),  # 图标文件，打包到根目录
        (resource_path('icon.png'), '.'),  # 图标文件，打包到根目录
        # (resource_path('data/config.json'), 'data'),  # 数据文件，打包到 data 文件夹
    ],
    hiddenimports=[],  # 隐式导入的模块，如果你的项目使用了某些 PyInstaller 无法自动检测到的模块，需要在此处添加
    hookspath=[],  # 自定义 hook 脚本路径
    hooksconfig={},  # hook 配置
    runtime_hooks=[],  # 运行时 hook
    excludes=[],  # 排除的模块
    win_no_prefer_redirects=False,  # Windows specific
    win_private_assemblies=False,  # Windows specific
    cipher=block_cipher,  # 加密
    noarchive=False,  # 是否打包成归档文件
)

# 4. PYZ 部分
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 5. EXE 部分
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='File Centipede Automatic Activation',  # 输出文件名，使用 GitHub Actions 变量
    debug=False,  # 是否开启调试模式
    bootloader_ignore_signals=False,  # Windows specific
    strip=False,  # 是否去除符号信息
    upx=True,  # 是否使用 UPX 压缩
    upx_exclude=[],  # UPX 排除文件
    runtime_tmpdir=None,  # 运行时临时目录
    console=False,  # 是否显示控制台窗口，如果你的程序是 GUI 程序，通常设置为 False
    disable_windowed_traceback=False,  # Windows specific
    argv_emulation=False,  # Windows specific
    target_arch=None,  # 目标架构
    codesign_identity=None,  # 代码签名
    entitlements_file=None,  # 权限文件
    icon=resource_path('favicon.ico'),  # 可执行文件图标
)
