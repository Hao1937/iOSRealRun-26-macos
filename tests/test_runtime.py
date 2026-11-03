import asyncio
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch
import run
from util.route import parse_route
from init import tunnel


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_routes(self):
        for path in Path(__file__).resolve().parents[1].glob('*.txt'):
            if path.name == 'requirements.txt':
                continue
            route = parse_route(path.read_text())
            self.assertTrue(run.fixLockT(route, 4.4, 0.2))

    async def test_clear_before_disconnect_on_error(self):
        events = []
        class Rsd:
            def __init__(self, *args): pass
            async def connect(self): pass
            async def close(self): events.append('disconnect')
        class Provider:
            def __init__(self, *args): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
        class Location(Provider):
            async def clear(self): events.append('clear')
        with patch.object(run, 'RemoteServiceDiscoveryService', Rsd), patch.object(run, 'DvtProvider', Provider), patch.object(run, 'LocationSimulation', Location), patch.object(run.asyncio, 'sleep', AsyncMock()), patch.object(run, '_run_with_location_simulation', AsyncMock(side_effect=RuntimeError('lost'))):
            with self.assertRaises(RuntimeError):
                await run.run('::1', 1234, [], 4.4, clear_on_finish=True)
        self.assertEqual(events, ['clear', 'disconnect'])

    async def test_tunnel_early_exit_fails_and_reaps(self):
        process = AsyncMock()
        process.returncode = 1
        process.stdout.readline.return_value = b''
        with patch.object(tunnel.asyncio, 'create_subprocess_exec', AsyncMock(return_value=process)):
            with self.assertRaises(RuntimeError):
                await tunnel.tunnel('26.0', timeout=0.5)

    async def test_invalid_route(self):
        for content in ['', "{'lat': 1, 'lng': 1}", "{'lat': 99, 'lng': 0}, {'lat': 0, 'lng': 0}"]:
            with self.assertRaises(ValueError):
                parse_route(content)


if __name__ == '__main__':
    unittest.main()
