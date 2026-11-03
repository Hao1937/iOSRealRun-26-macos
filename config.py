from pathlib import Path
import math
import yaml

BASE_DIR = Path(__file__).resolve().parent


class Config:
    def __init__(self, path=BASE_DIR / 'config.yaml'):
        path = Path(path).resolve()
        with path.open(encoding='utf-8') as stream:
            data = yaml.safe_load(stream)
        if not isinstance(data, dict):
            raise ValueError('配置文件必须是 YAML 字典')
        self.v = float(data['v'])
        if not math.isfinite(self.v) or not 0 < self.v < 1000 / 15:
            raise ValueError('v 必须为大于 0、小于 66.67 的有限速度（m/s）')
        self.routeConfig = str((path.parent / data['routeConfig']).resolve())


config = Config()
