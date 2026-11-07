"""Reuse an already mounted DDI before invoking the network-based auto-mounter."""
import json
import subprocess
import sys


def developer_image_mounted(images):
    return any(image.get('IsMounted') is True and
               image.get('MountPath') == '/System/Developer'
               for image in images)


def list_images():
    result = subprocess.run(
        [sys.executable, '-m', 'pymobiledevice3', 'mounter', 'list'],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout)


def prepare_device():
    if developer_image_mounted(list_images()):
        print('设备已挂载开发者镜像，直接复用，跳过下载。', flush=True)
        return
    print('设备尚未挂载开发者镜像，正在准备（iOS 27+ 自动使用 Cryptex）……', flush=True)
    print('首次需要联网下载并向 Apple 签名；请保持设备解锁和连接，最多等待 10 分钟。', flush=True)
    subprocess.run([sys.executable, '-u', '-m', 'pymobiledevice3', 'mounter', 'auto-mount'], check=True, timeout=600)
    # The upstream CLI can print an error while returning exit status zero.
    if not developer_image_mounted(list_images()):
        raise RuntimeError('开发者镜像未成功挂载，请检查设备开发者模式和镜像下载网络。')


if __name__ == '__main__':
    try:
        prepare_device()
    except KeyboardInterrupt:
        print('\n已取消设备准备。', file=sys.stderr)
        raise SystemExit(130)
    except subprocess.TimeoutExpired:
        print('设备准备超时，已停止等待。请检查 USB 连接、开发者模式及 GitHub / Apple 网络后重试。', file=sys.stderr)
        raise SystemExit(1)
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        print('设备准备失败。若日志出现 raw.githubusercontent.com / SSL 错误，请检查 GitHub 下载网络；路线文件与此错误无关。', file=sys.stderr)
        raise SystemExit(1)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
