# ========== 新增加：更新配置模块（放在最前面） ==========
import configparser
import os

APP_CONFIG_FILE = "app_config.ini"

def init_update_config():
    if not os.path.exists(APP_CONFIG_FILE):
        config = configparser.ConfigParser()
        config["APP_INFO"] = {
            "local_version": "1.0.0",
            "update_lock": "false"
        }
        with open(APP_CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)

def get_local_version():
    config = configparser.ConfigParser()
    config.read(APP_CONFIG_FILE, encoding="utf-8")
    return config.get("APP_INFO", "local_version")

def set_local_version(new_version):
    config = configparser.ConfigParser()
    config.read(APP_CONFIG_FILE, encoding="utf-8")
    config.set("APP_INFO", "local_version", new_version)
    with open(APP_CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)

def is_update_locked():
    config = configparser.ConfigParser()
    config.read(APP_CONFIG_FILE, encoding="utf-8")
    return config.getboolean("APP_INFO", "update_lock")

def set_update_lock(lock_status):
    config = configparser.ConfigParser()
    config.read(APP_CONFIG_FILE, encoding="utf-8")
    config.set("APP_INFO", "update_lock", str(lock_status).lower())
    with open(APP_CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)

# ========== 你原来的导入 ==========
import os
import requests
import importlib.util
import sys
from config import REMOTE_CODE_URL, LOCAL_CODE_PATH, VERSION

# ========== 新增加：云端更新检查（和你core里逻辑配套） ==========
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(timeout=10.0)
cloud_config = None

UPDATE_CONTROL_URL = "https://raw.githubusercontent.com/hd47zcfmd4-spec/ozon-pricing-calculator/main/update_control.ini"

def load_cloud_update_config():
    global cloud_config
    try:
        resp = http.request("GET", UPDATE_CONTROL_URL)
        if resp.status == 200:
            cloud_config = configparser.ConfigParser()
            cloud_config.read_string(resp.data.decode("utf-8"))
            return True
    except Exception:
        pass
    return False

def check_if_can_update():
    if is_update_locked():
        return False
    if not cloud_config:
        return False
    try:
        allow_update = cloud_config.getboolean("UPDATE", "allow_update")
        latest_version = cloud_config.get("UPDATE", "latest_version")
        local_version = get_local_version()
        return allow_update and (latest_version > local_version)
    except Exception:
        return False

def run_update():
    if not cloud_config:
        print("❌ 无法获取更新配置，更新失败")
        return False
    try:
        update_url = cloud_config.get("UPDATE", "update_url")
        local_file = cloud_config.get("UPDATE", "local_file")
        new_version = cloud_config.get("UPDATE", "latest_version")

        print("🔄 正在下载最新版本...")
        resp = http.request("GET", update_url)
        if resp.status != 200:
            print(f"❌ 下载失败，状态码：{resp.status}")
            return False

        if os.path.exists(local_file):
            os.rename(local_file, f"{local_file}.bak")

        with open(local_file, "wb") as f:
            f.write(resp.data)

        set_local_version(new_version)
        set_update_lock(True)
        print("✅ 更新成功！已自动锁定更新，请重启软件。")
        return True
    except Exception as e:
        print(f"❌ 更新失败：{e}")
        if os.path.exists(f"{local_file}.bak"):
            os.rename(f"{local_file}.bak", local_file)
        return False

# ========== 你原来的热更新函数不变 ==========
def update_remote_code():
    try:
        print(f"🔍 正在检查代码更新，当前版本：{VERSION}")
        response = requests.get(REMOTE_CODE_URL, timeout=10)
        response.raise_for_status()
        with open(LOCAL_CODE_PATH, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ 代码更新成功，已拉取最新版本")
        return True
    except Exception as e:
        print(f"❌ 代码更新失败：{str(e)}")
        if os.path.exists(LOCAL_CODE_PATH):
            print("⚠️  将使用本地缓存的旧代码，不影响正常使用")
            return True
        else:
            print("❌ 无可用代码，程序无法启动")
            return False

def load_core_code():
    if not update_remote_code():
        input("按回车键退出...")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("core", LOCAL_CODE_PATH)
    core_module = importlib.util.module_from_spec(spec)
    sys.modules["core"] = core_module
    spec.loader.exec_module(core_module)
    return core_module

# ========== 程序入口：加菜单 + 更新检查 ==========
if __name__ == "__main__":
    # 1. 初始化版本配置
    init_update_config()
    print("正在检查更新配置...")
    load_cloud_update_config()

    # 2. 智能解锁更新
    if check_if_can_update():
        set_update_lock(False)
        print("✅ 发现可用更新，已解锁更新权限")
    else:
        print("ℹ️ 暂无可用更新或更新已锁定")

    # 3. 显示菜单
    while True:
        print("\n===== Ozon 算价工具 =====")
        print("1. 启动算价工具")
        print("2. 检查并更新软件")
        print("3. 退出")
        choice = input("请输入选项（1/2/3）：").strip()

        if choice == "1":
            print("\n🔧 正在启动算价核心...")
            core = load_core_code()
            core.main()  # 调用core里的main
        elif choice == "2":
            if check_if_can_update():
                print("⚠️ 发现新版本，是否更新？(y/n)")
                if input().lower() == "y":
                    run_update()
                else:
                    print("已取消更新")
            else:
                print("当前已是最新版本，或更新未开放")
        elif choice == "3":
            print("👋 再见！")
            break
        else:
            print("❌ 输入错误，请输入 1/2/3")