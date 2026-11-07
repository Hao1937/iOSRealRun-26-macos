# iOSRealRun-26-macos

面向 **macOS** 的 iOS / iPadOS 路线定位模拟工具。基于 [BixingWu/iOSRealRun-26](https://github.com/BixingWu/iOSRealRun-26)，上游源自 [MTDickens/iOSRealRun-cli-18](https://github.com/MTDickens/iOSRealRun-cli-18)。保留上游 MPL-2.0 许可证。

此版本补齐 Windows 复制目录缺失的连接及路线模块，增加 macOS 启动器、独立 Python 环境、与工作目录无关的配置加载、隧道超时及进程清理，以及退出时的定位清除。

## macOS 启动

1. 安装 Python **3.12**（也可使用 3.10–3.13）。如已安装 Homebrew：`brew install python@3.12`。
2. USB 连接 iPhone / iPad，解锁并信任此 Mac，在设备「设置 → 隐私与安全性」中开启开发者模式，按提示重启。
3. 在终端进入本项目，运行：

   ```bash
   ./Start-iOSRealRun.command
   ```

   也可在 Finder 双击 `Start-iOSRealRun.command`。下载后若没有执行权限，先运行 `chmod +x Start-iOSRealRun.command`。

启动后首先显示路线选择菜单：用 **↑/↓** 选择，**Enter** 确认，**q / Esc** 取消。菜单显示四条示例路线，也会自动发现项目目录下新增的 `.txt` 路线文件（排除 `requirements.txt`）。终端不支持方向键菜单时使用数字选择。

选定后，启动器在 `.venv` 中安装依赖、检查所选路线、检查并复用设备已挂载的开发者镜像（未挂载时才下载挂载），然后请求 Mac 登录密码建立隧道。**不要用 sudo 启动整个脚本**。从 Windows 复制的 `.pvenv` 不可复用，启动器不会使用它。macOS 不需要安装 iTunes。

4. 按 **Ctrl+C** 停止。程序会尝试清除模拟定位，再关闭隧道。不要直接关闭窗口或拔线；断线时清除可能失败，如定位未恢复，请重启设备。

仅检查软件环境和路线，不连接设备、不改定位：

```bash
./Start-iOSRealRun.command --check
```

已挂载镜像时，可用 `./Start-iOSRealRun.command --skip-mount`。

直接运行 `main.py` 也会先选择路线；指定 `--route /path/to/route.txt` 可跳过菜单。`--check` 保持非交互，选择只对本次运行生效，不修改配置文件。

## 配置

编辑 `config.yaml`：

```yaml
v: 4.4                     # 速度，单位 m/s
routeConfig: "ZJGEast.txt"  # 相对于配置文件所在目录
```

附带 `ZJGEast.txt`、`ZJGWest.txt`、`YuQuan.txt`、`HaiNing.txt` 四条示例路线。路线格式为逗号分隔的坐标字典（不加外层方括号）：

```text
{"lng": 120.123, "lat": 30.123},
{"lng": 120.124, "lat": 30.124}
```

沿用上游 **BD-09** 输入坐标格式，运行时转换为 WGS-84；不要直接填入 WGS-84 坐标。路线循环运行直到 Ctrl+C。

## 验证范围及排错

- 已在 Apple Silicon macOS / Python 3.12 完成依赖导入、配置读取、四条路线解析和离线采样，4 项针对性测试通过；`--check` 不证明设备端定位已成功。
- iOS / iPadOS 26 的实际兼容性需要连接对应设备验证。本仓库不将上游环境声明当作本机真机测试结果。
- iOS 17.4+ 使用 `lockdown start-tunnel`；17.0–17.3 使用 `remote start-tunnel`。隧道最长等待 60 秒，失败后退出。
- 设备未发现：检查 USB 数据线、设备解锁、信任和开发者模式。
- 镜像挂载失败：先运行 `.venv/bin/python -m pymobiledevice3 mounter auto-mount` 查看具体错误，确认网络可下载匹配镜像。
- 固定 `pymobiledevice3==11.50.0`（iOS 27+ 自动使用 Cryptex 开发者镜像），防止依赖升级造成接口变化。Python 3.14 不在本启动器支持范围内。
- 原 Windows 启动文件仍保留，本次适配主要验证 macOS。

设备连接及隧道机制参考 [pymobiledevice3 官方文档](https://github.com/doronz88/pymobiledevice3)。

启动器在选定路线后将输出保存到 `logs/run-日期时间-进程号.log`；报错时会显示日志路径。日志不会提交到 GitHub。若下载镜像出现 SSL 错误，需检查到 `raw.githubusercontent.com` 的网络连接；pip 更新提示不是启动失败原因。

## iOS 27 / 27.3 beta

设备库已升级至 11.50.0，由其根据系统版本选择镜像：iOS 27+ 使用 Cryptex 安装，较旧系统继续使用对应的挂载流程。已验证 Python 接口导入、离线路线及自动化测试；27.3 beta 真机的镜像安装、定位和恢复仍需重新连接设备后验证。

系统更新后需要重新准备镜像。连接并解锁手机、确认信任和开发者模式后，可先执行：

```bash
./Start-iOSRealRun.command --prepare-only
```

选好路线后只检查环境并准备镜像，不开始模拟定位。成功后再正常启动。首次下载及 Apple 签名需要联网；准备过程超过 10 分钟会终止并显示排错提示，Ctrl+C 可取消。设备库升级不代表所有 beta 版本都已验证兼容。
