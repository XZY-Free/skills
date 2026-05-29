# 08b — SSH 远程服务器部署

用户明确说要"部署到自己的服务器"时走这里。**真实交付物是远端可访问的应用 + 健康检查通过**, 不是 SSH 已连接、不是 build 已上传。

凭证脱敏 / 不进版本控制等通用规则: [10-contracts.md#token-安全契约](10-contracts.md#token-安全契约)。

## 何时读

- 用户贴 IP + 账号 / SSH 命令行, 要求部署到该机器
- 用户说"上线 / 部署到服务器 / 给我个公网链接"且当前未走云 PaaS
- production gate 前确认远端环境

跳过场景: 用户只要本地 production server, 走 [08-deployment.md#本地-production-server-路径](08-deployment.md#本地-production-server-路径)。

## 目录

- [一行凭证解析](#一行凭证解析)
- [SSH 工具自动装](#ssh-工具自动装)
- [测连接](#测连接)
- [远端依赖探嗅](#远端依赖探嗅)
- [代码同步](#代码同步)
- [远端 MySQL 启动](#远端-mysql-启动)
- [构建 + 启动](#构建--启动)
- [反向代理 + HTTPS(可选)](#反向代理--https可选)
- [健康检查 + release.md](#健康检查--releasemd)
- [部署完成门槛](#部署完成门槛)

---

## 一行凭证解析

用户可能用以下任一格式贴凭证, 都要能解析:

| 格式 | 例 | 解析结果 |
|---|---|---|
| `IP user/password` | `203.0.113.10 deploy/example-pass` | host=203.0.113.10 user=deploy port=22 pass=example-pass |
| `IP user password`(空格分隔) | `203.0.113.10 deploy example-pass` | 同上 |
| `IP:port user/password` | `203.0.113.10:2222 root/example-pass` | port=2222 |
| `ssh user@host` + 单独说密码 | `ssh root@203.0.113.10`, 下一句 `密码: example-pass` | 拼起来 |
| `ssh user@host -p PORT` | `ssh deploy@203.0.113.10 -p 2222` | port=2222, 等用户给密码或 key |
| `IP user key=PATH` | `203.0.113.10 deploy key=~/.ssh/id_rsa` | 用 key 不要密码 |
| URL 风格 | `ssh://deploy:example-pass@203.0.113.10:22` | URL 解析 |

**解析规则**:

- IPv4 / IPv6 / 域名都支持
- `user/password` 中 `/` 是分隔符; 密码本身含 `/` 时用户应改贴 `user password` 空格格式或 URL 格式
- 端口缺省 22
- key 路径用 `~` 时 expand 到 `$HOME`
- 密码若含特殊字符(空格、`@`、`#`、`$`、`!`), 在 shell 调用时用单引号或 `sshpass -e + 环境变量`

**回显约束**(按 [10-contracts.md#token-安全契约](10-contracts.md#token-安全契约)):

- 解析后回显格式: `host=203.0.113.10 user=deploy port=22 password=********`
- 写入 release.md 时密码替换成 `<password-redacted>` 占位; 服务器 IP 默认保留(IP 不算高敏感)
- 用户标"内部 / 仅自用"时, host 也脱敏成 `<host-1>`

---

## SSH 工具自动装

按"探嗅 → 装"顺序处理本地 SSH 客户端 + sshpass(密码登录用):

```bash
# ssh 客户端
ssh -V 2>/dev/null && SSH_OK=1 || SSH_OK=0
# macOS / Linux 默认自带 OpenSSH
# Windows: winget install --id Microsoft.OpenSSH.Beta
#          或 powershell: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# sshpass (密码登录, 不交互输入)
which sshpass >/dev/null 2>&1 && SSHPASS_OK=1 || SSHPASS_OK=0
# macOS: brew install hudochenkov/sshpass/sshpass
# Linux: apt-get install -y sshpass  /  yum install -y sshpass
# Windows: 用 plink (PuTTY 套件), 或推荐用户改用 SSH key

# rsync (代码同步, 比 scp 增量更快)
which rsync >/dev/null 2>&1 && RSYNC_OK=1 || RSYNC_OK=0
# macOS / Linux 默认自带, Windows 走 wsl 或 scp 替代
```

装完逐个验证 `ssh -V` / `sshpass -V` / `rsync --version`, 再继续。

---

## 测连接

部署任何动作前先测一次:

```bash
# 密码登录
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=accept-new \
  -o ConnectTimeout=8 -p "$PORT" "$USER@$HOST" 'echo OK && uname -a'

# Key 登录
ssh -i "$KEY" -o StrictHostKeyChecking=accept-new \
  -o ConnectTimeout=8 -p "$PORT" "$USER@$HOST" 'echo OK && uname -a'
```

期望输出: `OK` + `Linux ... x86_64 ...` 或类似。

失败分类:

| 错误 | 含义 | 处理 |
|---|---|---|
| `Connection refused` | 端口不通 / sshd 未起 | 让用户检查防火墙 / sshd 状态 |
| `Permission denied (publickey)` | 服务器只接受 key, 用户给了密码 | 让用户上传 key 或改 sshd_config |
| `Permission denied (password)` | 密码错 | 让用户重发, 脱敏回显前缀 + 末 4 位 |
| `Host key verification failed` | known_hosts 冲突 | `ssh-keygen -R <host>` 后重试 |
| 超时 | 网络 / 安全组 | 让用户检查云厂商安全组 / 本机出网 |

连接通过后, 把 host + user + port 记录到 `.opc/deployment/ssh-target.json`(密码字段不记, 走 env 或临时变量)。

---

## 远端依赖探嗅

ssh 上去后, 探嗅远端环境, 装缺失依赖:

```bash
ssh-cmd() { sshpass -p "$PASS" ssh -p "$PORT" "$USER@$HOST" "$@"; }

# 1. Docker (优先)
ssh-cmd 'docker info' >/dev/null 2>&1 && REMOTE_DOCKER=1 || REMOTE_DOCKER=0

# 2. 包管理器
ssh-cmd 'cat /etc/os-release' | grep -E '^ID=' | cut -d= -f2 | tr -d '"'
# 输出 ubuntu / debian / centos / rhel / alpine

# 3. Node.js
ssh-cmd 'node --version' 2>/dev/null
# 期望 >= 18

# 4. MySQL 客户端 (用于 prisma migrate 时连本机 MySQL)
ssh-cmd 'mysql --version' 2>/dev/null

# 5. pm2 / systemd 用于守护进程
ssh-cmd 'which pm2' 2>/dev/null
```

按结果装:

```bash
# Ubuntu / Debian
ssh-cmd 'curl -fsSL https://get.docker.com | sh && systemctl enable --now docker'
ssh-cmd 'curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs'
ssh-cmd 'npm install -g pm2'

# CentOS / RHEL
ssh-cmd 'curl -fsSL https://get.docker.com | sh && systemctl enable --now docker'
ssh-cmd 'curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && yum install -y nodejs'
ssh-cmd 'npm install -g pm2'
```

装完逐项验证再继续。**装失败不要硬上**, 走 [troubleshooting.md](troubleshooting.md) 排障。

---

## 代码同步

`rsync` 增量同步, 排除本地无用文件:

```bash
rsync -avz --delete \
  --exclude 'node_modules' --exclude '.next' --exclude '.git' \
  --exclude '.env' --exclude '*.log' --exclude '.opc' \
  -e "sshpass -p '$PASS' ssh -p $PORT -o StrictHostKeyChecking=accept-new" \
  ./ "$USER@$HOST:/opt/<app>/"
```

替代方案: `git clone` + `git pull`(用户的服务器能访问仓库 remote 时), 但 OPC 默认本地 rsync 同步, **不强求公开 git remote**。

---

## 远端 MySQL 启动

按 [02-clarification.md#mysql-本地启动探嗅](02-clarification.md#mysql-本地启动探嗅) 同样顺序, 在远端跑:

```bash
ssh-cmd 'docker info' && {
  ssh-cmd "docker run -d --name <app>-mysql \
    -p 127.0.0.1:3306:3306 \
    -e MYSQL_ROOT_PASSWORD='$DB_ROOT_PASS' \
    -e MYSQL_DATABASE='<app>' \
    -v <app>-mysql-data:/var/lib/mysql \
    --restart unless-stopped \
    mysql:8"
}
```

注意:

- `-p 127.0.0.1:3306` 只绑本机, 不开公网
- volume `<app>-mysql-data` 保证容器重启数据不丢
- `$DB_ROOT_PASS` 走 env 或随机生成, **不要直接写脚本里**
- DATABASE_URL 远端 `.env` 里写 `mysql://root:<pass>@127.0.0.1:3306/<app>`(同机访问)

迁移:

```bash
ssh-cmd 'cd /opt/<app> && npx prisma migrate deploy'
```

`migrate deploy` 不是 `migrate dev`: deploy 只跑已有的迁移, 不会建新迁移文件。

---

## 构建 + 启动

```bash
ssh-cmd 'cd /opt/<app> && npm ci --omit=dev=false'
ssh-cmd 'cd /opt/<app> && npm run build'

# pm2 启动(守护 + 自启)
ssh-cmd 'cd /opt/<app> && pm2 start npm --name <app> -- start'
ssh-cmd 'pm2 save && pm2 startup systemd -u root --hp /root'
```

应用默认监听 `127.0.0.1:3000`(同机访问); 公网通过反向代理 + 80/443 暴露(见下节)。

---

## 反向代理 + HTTPS(可选)

用户给了域名 + 要 HTTPS → 推荐 Caddy(零配置 ACME):

```bash
ssh-cmd 'apt-get install -y caddy'
ssh-cmd "cat > /etc/caddy/Caddyfile <<'EOF'
<user-domain> {
  reverse_proxy 127.0.0.1:3000
}
EOF"
ssh-cmd 'systemctl restart caddy'
```

只用 IP 没域名 → 直接 80 端口反代:

```bash
ssh-cmd "cat > /etc/caddy/Caddyfile <<'EOF'
:80 {
  reverse_proxy 127.0.0.1:3000
}
EOF"
```

不想装 Caddy → nginx 同样能做, 但要自己处理 cert; 在 release.md 里写明。

---

## 健康检查 + release.md

```bash
# 同机
ssh-cmd 'curl -sf http://127.0.0.1:3000 -o /dev/null -w "local=%{http_code}\n"'
# 公网(替换实际 host)
curl -sf "http://$HOST/" -o /dev/null -w "public=%{http_code}\n"
```

期望都是 200。

写 `.opc/deployment/release.md`(凭证字段一律占位):

```markdown
# Release Evidence

## 部署目标
- Mode: remote-ssh
- Host: 203.0.113.10  (用户标注内部时改 <host-1>)
- User: deploy
- Port: 22
- Auth: password (<password-redacted>) / key (<key-path-redacted>)

## Build
- Commands: npm ci && npm run build
- Build size: <X> MB

## Deployment
- Method: rsync + pm2
- App URL: http://203.0.113.10/  (或域名 https://<user-domain>/)
- Process manager: pm2 (name=<app>)
- DB: mysql:8 in docker, port 127.0.0.1:3306

## Environment
- DATABASE_URL: mysql://root:<password-redacted>@127.0.0.1:3306/<app>
- NEXTAUTH_SECRET: <secret-redacted>
- Other env vars: 见 .env.example

## Premortem / Red-team (production 才必跑)
- Top risks: ...
- Stop conditions: ...

## Verification
- 健康检查: HTTP 200
- 主链路浏览器验证: <截图路径或核心流程描述>
- DB 数据持久: <重启容器后数据仍在>

## Rollback
- 上一版本: pm2 list 显示 <prev-name> 仍在但 stopped
- 回滚命令: pm2 stop <app> && pm2 start <prev-name>
- 或: rsync 旧 build 回去 + pm2 restart
```

---

## 部署完成门槛

满足以下才能 mark deployment done:

- [ ] SSH 测连通过, 凭证不在 commit / release.md 明文
- [ ] 远端依赖(Docker / Node / MySQL / pm2)全部就绪
- [ ] 代码已 rsync 到 `/opt/<app>/` 或用户指定路径
- [ ] DB 迁移 `prisma migrate deploy` 成功, 表结构跟本地一致
- [ ] `npm run build` 成功, pm2 守护进程跑着
- [ ] 健康检查 HTTP 200(同机 + 公网)
- [ ] 主链路浏览器或 curl 验证通过, 数据真实持久
- [ ] release.md 写明: 部署目标、build / deploy 命令、URL、env 位置、rollback 方式
- [ ] **production 部署**: 额外要 premortem + stop conditions + rollback 实测

任一项缺 → 标 `blocked` + 原因, 不说"已部署"。
