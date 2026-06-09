import os
import requests
import importlib.util
import sys
from config import REMOTE_CODE_URL, LOCAL_CODE_PATH, VERSION

# ========== 热更新核心逻辑 ==========
def update_remote_code():
    """从远程拉取最新的核心代码，拉取失败则使用本地缓存"""
    try:
        print(f"🔍 正在检查代码更新，当前版本：{VERSION}")
        # 用HTTPS拉取远程代码，超时10秒
        response = requests.get(REMOTE_CODE_URL, timeout=10)
        response.raise_for_status()
        # 把最新代码写入本地缓存文件
        with open(LOCAL_CODE_PATH, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ 代码更新成功，已拉取最新版本")
        return True
    except Exception as e:
        print(f"❌ 代码更新失败：{str(e)}")
        # 拉取失败时，检查本地是否有缓存的旧代码
        if os.path.exists(LOCAL_CODE_PATH):
            print("⚠️  将使用本地缓存的旧代码，不影响正常使用")
            return True
        else:
            print("❌ 无可用代码，程序无法启动")
            return False

def load_core_code():
    """动态加载核心业务代码，返回核心模块"""
    if not update_remote_code():
        input("按回车键退出...")
        sys.exit(1)
    # 动态导入core.py模块
    spec = importlib.util.spec_from_file_location("core", LOCAL_CODE_PATH)
    core_module = importlib.util.module_from_spec(spec)
    # 把模块加入系统路径，保证内部导入正常
    sys.modules["core"] = core_module
    spec.loader.exec_module(core_module)
    return core_module

# ========== 程序入口 ==========
if __name__ == "__main__":
    # 先更新并加载核心代码
    core = load_core_code()
    # 调用核心代码的主函数，启动计算器
    core.main()