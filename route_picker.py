"""Terminal route selection, using only the Python standard library."""
import argparse
import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
LABELS = {'ZJGEast.txt': '紫金港东操场', 'ZJGWest.txt': '紫金港西操场',
          'YuQuan.txt': '玉泉操场', 'HaiNing.txt': '海宁操场'}


def route_files(directory=BASE_DIR, default=None):
    files = sorted(p.resolve() for p in Path(directory).glob('*.txt')
                   if p.is_file() and p.name != 'requirements.txt')
    if default and Path(default).is_file() and Path(default).resolve() not in files:
        files.append(Path(default).resolve())
    if not files:
        raise ValueError('未找到路线文件，请将路线 .txt 文件放入项目目录。')
    return files


def label(path):
    return f'{LABELS.get(path.name, "自定义路线")}  ({path.name})'


def select_route(default=None):
    files = route_files(default=default)
    index = files.index(Path(default).resolve()) if default and Path(default).resolve() in files else 0
    if not sys.stdin.isatty():
        raise ValueError('交互选择需要终端；自动运行请使用 --route 路线文件。')
    if os.name != 'nt' and os.environ.get('TERM', '') not in ('', 'dumb'):
        import curses

        def menu(screen):
            nonlocal index
            try:
                curses.curs_set(0)
            except curses.error:
                pass
            screen.keypad(True)
            while True:
                screen.erase()
                height, width = screen.getmaxyx()
                visible = max(1, height - 5)
                start = max(0, index - visible + 1)
                lines = ['iOSRealRun · 选择路线', '↑/↓ 选择 · Enter 确认 · q / Esc 退出', '']
                for i in range(start, min(start + visible, len(files))):
                    lines.append(('▶ ' if i == index else '  ') + label(files[i]))
                for row, text in enumerate(lines[:height]):
                    try:
                        screen.addnstr(row, 0, text, max(1, width - 1),
                                       curses.A_REVERSE if row >= 3 and start + row - 3 == index else 0)
                    except curses.error:
                        pass
                screen.refresh()
                key = screen.getch()
                if key in (curses.KEY_UP, ord('k')):
                    index = (index - 1) % len(files)
                elif key in (curses.KEY_DOWN, ord('j')):
                    index = (index + 1) % len(files)
                elif key in (10, 13, curses.KEY_ENTER):
                    return files[index]
                elif key in (27, ord('q'), 3):
                    raise KeyboardInterrupt
        try:
            return curses.wrapper(menu)
        except curses.error:
            pass
    print('\n=== iOSRealRun · 选择路线 ===')
    for i, path in enumerate(files, 1):
        print(f'  {i}. {label(path)}' + (' [默认]' if i - 1 == index else ''))
    while True:
        value = input(f'输入序号 [默认 {index + 1}]，q 退出：').strip()
        if value.lower() == 'q':
            raise KeyboardInterrupt
        if not value:
            return files[index]
        if value.isdigit() and 1 <= int(value) <= len(files):
            return files[int(value) - 1]
        print('请输入列表中的序号。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        chosen = select_route()
        Path(args.output).write_text(str(chosen), encoding='utf-8')
        print(f'已选择：{label(chosen)}')
    except (KeyboardInterrupt, EOFError):
        print('\n已取消。')
        raise SystemExit(130)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
