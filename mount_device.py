"""Run the upstream mounter with bounded retries for DDI downloads only."""
import runpy
import sys
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

import requests
from developer_disk_image import repo


def download(url, **kwargs):
    kwargs.setdefault('timeout', (15, 60))
    name = urlsplit(url).path.rsplit('/', 1)[-1]
    for attempt in range(1, 4):
        print(f'下载镜像文件 {name}（尝试 {attempt}/3）', flush=True)
        try:
            response = requests.get(url, **kwargs)
            if response.status_code in (429, 500, 502, 503, 504):
                response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == 3:
                raise
            print('下载连接中断，3 秒后重试当前文件。', flush=True)
            time.sleep(3)


if __name__ == '__main__':
    # Limit the override to the DDI repository; device and Apple signing calls
    # keep the upstream behavior. TLS verification and proxy settings are kept.
    repo.requests = SimpleNamespace(get=download)
    sys.argv = ['pymobiledevice3', 'mounter', 'auto-mount']
    runpy.run_module('pymobiledevice3', run_name='__main__')
