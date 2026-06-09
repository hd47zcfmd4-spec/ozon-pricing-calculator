# ===================== 热更新核心配置（你原来的，完全保留）=====================
# 1. 远程core.py的raw地址（替换成你自己的Gitee/GitHub/OSS地址）
REMOTE_CODE_URL = "https://raw.githubusercontent.com/hd47zcfmd4-spec/ozon-pricing-calculator/refs/heads/main/core.py"
# 2. 本地缓存的代码文件路径（不用改）
LOCAL_CODE_PATH = "core.py"
# 3. 版本号（每次更新远程代码后，把这个数字+1，方便做版本控制）
VERSION = "1.0.2"
# 4. 代码签名公钥（进阶安全用，基础版可以先不用）
PUBLIC_KEY = ""

# ===================== 智能更新开关模块（我给你加的，不冲突）=====================
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