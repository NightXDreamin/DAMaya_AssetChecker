"""把 DAMaya Asset Checker 挂进 Maya 启动脚本（userSetup.py），实现「开 Maya 自动出菜单」。

参考 DAMaya_MCP 的 install_maya_mcp.py：
* 定位 Windows 用户 Documents 目录（兼容 OneDrive/重定向）
* 幂等写入 userSetup.py 的 hook 块
* hook 内用 ``maya.utils.executeDeferred`` 延迟建菜单（等 Maya UI 初始化完成）

运行：  python scripts/install_maya_setup.py
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")


def _documents_dir():
    """定位用户 Documents 目录（Windows 用注册表，兼容 OneDrive）。"""
    if os.name == "nt":
        try:
            import winreg

            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                val, _ = winreg.QueryValueEx(key, "Personal")
                return os.path.expandvars(val)
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def _hook_code():
    return """# --- DAMaya Asset Checker Startup Hook ---
import sys
_project_path = r"{root}"
if _project_path not in sys.path:
    sys.path.insert(0, _project_path)

try:
    import maya.utils as _mutils

    def _dcc_checker_startup():
        from dcc_checker.ui import main_menu
        main_menu.install()

    _mutils.executeDeferred(_dcc_checker_startup)
except Exception as _e:
    print("DAMaya Asset Checker startup hook failed: %r" % _e)
# --- End of DAMaya Asset Checker Startup Hook ---""".format(root=PROJECT_ROOT)


def main():
    hook_start = "# --- DAMaya Asset Checker Startup Hook ---"
    hook_end = "# --- End of DAMaya Asset Checker Startup Hook ---"

    maya_scripts_dir = os.path.join(_documents_dir(), "maya", "scripts")
    user_setup_path = os.path.join(maya_scripts_dir, "userSetup.py")

    os.makedirs(maya_scripts_dir, exist_ok=True)

    existing = ""
    if os.path.exists(user_setup_path):
        with open(user_setup_path, "r", encoding="utf-8") as f:
            existing = f.read()

    hook_code = _hook_code()
    if hook_start in existing and hook_end in existing:
        start = existing.find(hook_start)
        end = existing.find(hook_end) + len(hook_end)
        new_content = existing[:start] + hook_code + existing[end:]
        print("[*] 已存在 DAMaya Asset Checker hook，更新其内容。")
    else:
        separator = "\n\n" if existing else ""
        new_content = existing + separator + hook_code
        print("[+] 新增 DAMaya Asset Checker hook。")

    with open(user_setup_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("[SUCCESS] 已写入:", user_setup_path)
    print("重启 Maya 后，主菜单栏将自动出现 DAMaya Asset Checker -> Open Tool Dock。")


if __name__ == "__main__":
    main()
