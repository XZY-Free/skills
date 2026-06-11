# 截图自检 + 部署

## 截图自检：代码对 ≠ 视觉对

写完、改完版式，别只看代码就说「好了」。HTML 里 `style` 属性重复、flex 没撑开、内容超出一屏——这些代码看着没错，渲染出来是崩的。**用 Playwright 按投屏比例截一张，自己看一眼。**

脚手架配了脚本 [../scripts/shoot.mjs](../scripts/shoot.mjs)：

```bash
node shoot.mjs ./deck.html 3            # 本地第 3 页
node shoot.mjs http://host/培训 8       # 线上第 8 页（中文路径自动编码）
```

按 `1440×810`（16:9 投屏比例）截。改了版式的页、新做的页，都截来看。

**playwright 装哪不一定**，脚本里写了找法。如果报找不到模块，多半在 npx 缓存里，这样跑：
```bash
NODE_PATH=$(ls -d ~/.npm/_npx/*/node_modules 2>/dev/null | head -1) node shoot.mjs ./deck.html 3
```

**图片用绝对路径引用（`/xxx.jpg`）时，本地 `file://` 看不到图，必须截线上 URL。**

看截图时盯几样：内容有没有超出一屏、左右是不是失衡有大片空白、几个元素是不是各在不同高度显得散、装饰是不是堆太多（炫技，见 [anti-ai-flavor.md](anti-ai-flavor.md) 第三类）。

## 部署：通用做法

> 具体哪台服务器、什么 web server、哪个路径——**不写在这儿**，那是各项目自己的事，记到项目记忆。这里只讲不管在哪都该这么做的稳妥流程。

**改本地 → 传临时文件 → 备份原文件 → 原子替换 → 实测验证**：

1. 本地改好，记下文件字节数（待会儿核对传输完整）。
2. `scp` 上传到一个 `.new` 临时文件，别直接覆盖线上。
3. 服务器上：先把原文件备份（`cp xxx.html xxx.html.bak-<时间戳>`），再 `mv .new` 原子替换。这样随时能回退。
4. **实测**：在服务器上 `curl` 真实请求那个 URL，grep 一句这次改的内容，确认线上真的变了——别只看「传完了」就当成功。
5. 核对本地字节数 == 上传字节数，确认没传坏。

备份会越攒越多，隔段时间只留最近两三个、删早期的。

## 几个真踩过的坑

**中文文件名 / 中文路径走 ssh 命令行会失败（退出码 255）。** 中文出现在 `ssh ... '命令'` 的命令行参数里会触发连接异常。两个解法：

- 远程要跑的脚本通过 **stdin 管道**喂给 `ssh ... bash -s`，中文只走数据流、不进命令行参数：
  ```bash
  ssh -T user@host 'bash -s' <<'EOF'
  cd /var/www/plans && ls 财务培训.html
  EOF
  ```
- 传中文名的文件：先用**英文临时名** `scp` 上去，再在服务器端（用上面的 stdin 方式）`mv` 成中文名。

**curl 验证要带对 Host。** 一台机器 80 端口常有多个 server 块，目标 server 未必是 default。直接 `curl http://<公网IP>/<路径>` 命中正确 server，中文路径用 percent-encode。

**图片放服务器后**：确认它有自己可访问的 URL（比如 nginx 有 `location /plans/` 指向图片目录），HTML 里就用这个同源路径引用。传完 `curl -I` 看一下返回 200、`Content-Type` 对。
