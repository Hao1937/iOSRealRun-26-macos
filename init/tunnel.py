"""Own the actual tunnel subprocess so failures and shutdown cannot orphan it."""
import asyncio
import logging
import os
import re
import sys


async def stop_tunnel(process):
    if process.returncode is None:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), 5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()


async def tunnel(version, timeout=60):
    parts = tuple(int(p) for p in version.split('.')[:2])
    group = 'lockdown' if parts >= (17, 4) else 'remote'
    process = await asyncio.create_subprocess_exec(
        sys.executable, '-u', '-m', 'pymobiledevice3', group, 'start-tunnel',
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        start_new_session=os.name != "nt",
    )

    async def read_address():
        while line := await process.stdout.readline():
            output = line.decode(errors='replace').strip()
            logging.info('%s', output)
            match = re.search(r'--rsd\s+(\S+)\s+(\d+)', output)
            if match:
                return match.group(1), int(match.group(2))
        raise RuntimeError('隧道提前退出，请检查设备连接、开发者模式和管理员权限。')

    try:
        address, port = await asyncio.wait_for(read_address(), timeout)
    except BaseException:
        await stop_tunnel(process)
        raise
    return process, address, port


async def drain_output(process):
    while line := await process.stdout.readline():
        logging.info('%s', line.decode(errors='replace').strip())
