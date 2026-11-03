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
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def prepare_device():
    if developer_image_mounted(list_images()):
        print('设备已挂载开发者镜像，直接复用，跳过下载。', flush=True)
        return
    print('设备尚未挂载开发者镜像，正在自动挂载……', flush=True)
    subprocess.run([sys.executable, '-m', 'pymobiledevice3', 'mounter', 'auto-mount'], check=True)
    # The upstream CLI can print an error while returning exit status zero.
    if not developer_image_mounted(list_images()):
        raise RuntimeError('开发者镜像未成功挂载，请检查设备开发者模式和镜像下载网络。')


if __name__ == '__main__':
    try:
        prepare_device()
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        print('设备准备失败。若日志出现 raw.githubusercontent.com / SSL 错误，请检查 GitHub 下载网络；路线文件与此错误无关。', file=sys.stderr)
        raise SystemExit(1)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
