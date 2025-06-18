#!/bin/bash

# ========= 获取用户和密码（支持环境变量） =========
USER_NAME=${PROXY_USER:-proxy}
USER_PASS=${PROXY_PASS:-secret}

# ========= 安装 sing-box =========
wget -qO- https://github.com/SagerNet/sing-box/releases/latest/download/sing-box-linux-amd64.tar.gz | tar xz
mv sing-box-* sing-box
chmod +x sing-box
mv sing-box /usr/local/bin/sing-box

# ========= 创建配置文件 =========
mkdir -p /etc/sing-box

cat > /etc/sing-box/config.json << EOF
{
  "log": {
    "level": "info",
    "output": "stdout"
  },
  "inbounds": [
    {
      "type": "socks",
      "tag": "socks-in",
      "listen": "::1",
      "listen_port": 1080,
      "users": [
        {
          "username": "$USER_NAME",
          "password": "$USER_PASS"
        }
      ],
      "udp_over_tcp": false
    }
  ],
  "outbounds": [
    {
      "type": "direct",
      "tag": "cf-direct",
      "domain_strategy": "prefer_ipv6"
    }
  ],
  "route": {
    "rules": [
      {
        "ip_cidr": [
          "104.16.0.0/12",
          "104.18.0.0/15",
          "172.64.0.0/13"
        ],
        "outbound": "cf-direct"
      }
    ]
  }
}
EOF

# ========= 创建 systemd 服务 =========
cat > /etc/systemd/system/sing-box.service << EOF
[Unit]
Description=Sing-box Service
After=network.target

[Service]
ExecStart=/usr/local/bin/sing-box run -c /etc/sing-box/config.json
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# ========= 启动并设置开机自启 =========
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable --now sing-box

# ========= 输出结果 =========
echo "✅ sing-box 已启动"
echo "🎯 SOCKS5 地址: [::1]:1080（仅限本机访问）"
echo "🔐 用户名: $USER_NAME"
echo "🔐 密码: $USER_PASS"
