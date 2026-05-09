# iOSRealRun-26

本项目基于 [iOSRealRun-cli-18](https://github.com/MTDickens/iOSRealRun-cli-18) 修改而来，兼容了26版系统

测试环境：
- 操作系统：Windows11
- Python版本：3.10
- iPad OS版本：26.4

## 用法简介

### 前置条件

1. 系统是 `Windows` 或 `MacOS`
2. iPhone 或 iPad 系统版本为26版
3. Windows 需要安装 iTunes
4. 已安装 `Python3` 和 `pip3`

### 步骤

1. 克隆本项目到本地并进入项目目录

2. 安装依赖（建议使用虚拟环境）

    ```shell
    conda create -n fake python=3.10 -y
    conda activate fake
    pip install -r requirements.txt
    ```
    
3. 修改配置和路线文件 （见 [这里](https://github.com/iOSRealRun/iOSRealRun-cli/blob/main/README.md#%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95) 的 4、5、7 步）
  
    > 当前项目已有
    >
    > - `ZJGEast.txt`：紫金港东操场
    > - `ZJGWest.txt`：紫金港西操场
    > - `YuQuan.txt`：玉泉操场
    > - `HaiNing.txt`：海宁操场
    >
    > 在`config.yaml`中修改
    >
    > ```yaml
    > v: 4.4
    > routeConfig: "ZJGEast.txt" # 修改为对应路线名即可
    > libimobiledeviceDir: "libimobiledevice"
    > imageDir: "DeveloperDiskImage"
    > ```
    
4. 将设备连接到电脑，解锁，如果请求信任的提示框，请点击信任

5. 打开终端（cmd 或 PowerShell），执行以下命令获取DDI
    ```shell
    pymobiledevice3 mounter auto-mount
    ```
    
6. 运行程序
  
  
    Windows **以管理员身份** 打开终端（cmd 或 PowerShell），先进入项目目录，然后执行以下命令 
    ```shell
    python main.py
    ```
    MacOS 打开终端，先进入项目目录，然后执行以下命令  
    ```shell
    sudo python3 main.py
    ```
    
    > 需要 管理员 或 root 权限是因为需要创建 tun 设备  

7. 按照提示操作，如果一直说没有设备连接，Windows请确保 iTunes 已安装（可能需要打开），重新运行程序，在第3步时请确保设备已连接，解锁并信任

8. 结束请务必使用 `Ctrl + C` 终止程序，否则无法恢复定位

9. 如果定位未恢复，可以重启手机解决

### 自定义配置文件

- 若希望修改速度，请在 config.yaml 中修改 v
    - 默认的 `4.2 m/s`，就是大约 `4 min/km` 的水平
- 若需修改配置文件，请在 config.yaml 中修改 routeConfig

### 一键运行

Windows系统可以尝试当前文件目录下的.bat脚本，一键开始跑步
