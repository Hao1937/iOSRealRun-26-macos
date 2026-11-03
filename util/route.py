import ast
import math


def parse_route(content):
    points = ast.literal_eval('[{}]'.format(content))
    if len(points) < 2:
        raise ValueError('路线至少需要两个坐标点')
    result = []
    for point in points:
        lat, lng = float(point['lat']), float(point['lng'])
        if not (math.isfinite(lat) and math.isfinite(lng) and -90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError('路线包含无效经纬度')
        result.append({'lat': lat, 'lng': lng})
    if len({(p['lat'], p['lng']) for p in result}) < 2:
        raise ValueError('路线至少需要两个不同的坐标点')
    return result
