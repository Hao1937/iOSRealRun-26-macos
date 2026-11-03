"""macOS/Windows entry point. Ctrl+C clears location before closing the tunnel."""
import argparse
import asyncio
import contextlib
import logging
import signal
from pathlib import Path

from route_picker import select_route

import coloredlogs
from init import init, route, tunnel
import config
import run


async def main(check=False, route_file=None):
    if route_file:
        config.config.routeConfig = str(Path(route_file).resolve())
    elif not check:
        config.config.routeConfig = str(select_route(config.config.routeConfig))
    loc = route.get_route()
    if check:
        sampled = run.fixLockT(loc, config.config.v, 0.2)
        print(f'环境和路线检查通过：{len(loc)} 个坐标点，{len(sampled)} 个采样点，{config.config.v} m/s')
        return
    version = await init.init()
    process = None
    drain = None
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stopped.set)
    try:
        if int(version.split('.')[0]) >= 17:
            process, address, port = await tunnel.tunnel(version)
            drain = asyncio.create_task(tunnel.drain_output(process))
            await run.run(address, port, loc, config.config.v,
                          stop_requested=stopped.is_set, clear_on_finish=True)
        else:
            await run.run_legacy(loc, config.config.v,
                                 stop_requested=stopped.is_set, clear_on_finish=True)
    finally:
        if process is not None:
            await tunnel.stop_tunnel(process)
        if drain is not None:
            await drain
        print('程序已退出。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='iOSRealRun macOS — Ctrl+C 停止并恢复定位')
    parser.add_argument('--check', action='store_true', help='只检查环境和路线，不连接设备或修改定位')
    parser.add_argument('--route', help='指定路线文件，跳过交互选择')
    args = parser.parse_args()
    coloredlogs.install(level=logging.INFO)
    try:
        asyncio.run(main(args.check, args.route))
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logging.exception('运行失败：%s', exc)
        raise SystemExit(1)
