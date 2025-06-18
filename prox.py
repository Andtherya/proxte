import os
import json
import subprocess
import platform
from pathlib import Path
import urllib.request
import tarfile

# ========= 用户参数 =========
username = os.getenv("PROXY_USER", "proxy")
password = os.getenv("PROXY_PASS", "secret")
port = 1080
install_dir = Path.home() / ".sing-box-noroot"

# ========= 创建目录 =========
install_dir.mkdir(parents=True, exist_ok=True)

# ========= 下载 sing-box =========
arch = "amd64" if platform.machine() == "x86_64" else platform.machine()
url = f"https://github.com/SagerNet/sing-box/releases/latest/download/sing-box-linux-{arch}.tar.gz"
tar_path = install_dir / "sing-box.tar.gz"

print("📦 正在下载 sing-box ...")
urllib.request.urlretrieve(url, tar_path)

# ========= 解压 =========
print("📂 正在解压 sing-box ...")
with tarfile.open(tar_path, "r:gz") as tar:
    for member in tar.getmembers():
        if "sing-box" in member.name and not member.name.endswith(".sig"):
            member.name = "sing-box"  # 重命名
            tar.extract(member, path=install_dir)
            break

# ========= 写入配置文件 =========
config = {
    "log": {
        "level": "info",
        "output": "stdout"
    },
    "inbounds": [{
        "type": "socks",
        "tag": "socks-in",
        "listen": "::1",
        "listen_port": port,
        "users": [{
            "username": username,
            "password": password
        }],
        "udp_over_tcp": False
    }],
    "outbounds": [{
        "type": "direct",
        "tag": "cf-direct",
        "domain_strategy": "prefer_ipv6"
    }],
    "route": {
        "rules": [{
            "ip_cidr": [
                "104.16.0.0/12",
                "104.18.0.0/15",
                "172.64.0.0/13"
            ],
            "outbound": "cf-direct"
        }]
    }
}

config_path = install_dir / "config.json"
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

# ========= 运行 sing-box =========
bin_path = install_dir / "sing-box"
print(f"🚀 正在启动 sing-box，监听 ::1:{port} ...")
subprocess.run([str(bin_path), "run", "-c", str(config_path)])
