"""10 个音乐工具；演示曲库与共享状态都在业务侧。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult

SONGS = [{'id': 'sunny', 'name': '晴天'}, {'id': 'river', 'name': '七里香'}, {'id': 'night', 'name': '夜曲'}]


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    music = ctx.snapshot()['music']
    query = args.get('query', '')
    # 子串匹配离线曲库，空查询匹配全部歌曲；状态查询直接返回，不提交更新。
    matches = [s for s in SONGS if query in s['name']]
    if name == 'music_state_query':
        return ctx.result('当前音乐状态', data={'music': music})
    changes: dict = {}
    if name == 'music_search':
        changes['results'] = matches
    elif name == 'music_play':
        # 有查询时选择第一首匹配歌曲，无查询时继续当前歌曲。
        if query and not matches:
            raise ValueError('演示曲库中没有这首歌')
        changes = {'playing': True, 'currentIndex': SONGS.index(matches[0]) if query else music['currentIndex']}
    elif name in {'music_pause', 'music_toggle_playback'}:
        changes['playing'] = False if name == 'music_pause' else not music['playing']
    elif name in {'music_next', 'music_previous'}:
        # 取模让末尾的下一首回到第一首、第一首的上一首回到末尾。
        changes['currentIndex'] = (music['currentIndex'] + (1 if name == 'music_next' else -1)) % len(SONGS)
    elif name == 'music_source_control':
        changes['source'] = args['source']
    elif name == 'music_volume_control':
        # 静音开关与数值音量分开保存，mute 不会清除原来的音量。
        action = args['action']
        if action in {'mute', 'unmute'}:
            changes['muted'] = action == 'mute'
        else:
            volume = args.get('volume', music['volume']) if action == 'set' else music['volume'] + (
                args.get('delta', 1) if action == 'increase' else -args.get('delta', 1))
            changes['volume'] = min(11, max(0, volume))  # set 或增减后的音量都限制在 0–11。
    elif name == 'music_favorite_control':
        action = args.get('action', 'toggle')
        if action in {'next', 'previous'}:
            # 演示版选收藏中的第一首或最后一首，没有收藏则报告业务错误。
            indices = [i for i, s in enumerate(SONGS) if s['id'] in music['favoriteIds']]
            if not indices:
                raise ValueError('尚无收藏歌曲')
            changes['currentIndex'] = indices[0 if action == 'next' else -1]
        else:
            # 按查询或当前歌曲定位目标，复制收藏列表后执行添加/删除/切换。
            song = matches[0] if query and matches else SONGS[music['currentIndex']]
            favorites = list(music['favoriteIds'])
            if action == 'remove' or (action == 'toggle' and song['id'] in favorites):
                favorites = [item for item in favorites if item != song['id']]
            elif song['id'] not in favorites:
                # 已收藏时不再追加，避免同一个歌曲 ID 重复出现。
                favorites.append(song['id'])
            changes['favoriteIds'] = favorites
    else:
        raise ValueError('未知音乐工具')
    # 把所选操作的字段一次提交，再从新状态读取当前曲名生成真实结果文本。
    state = ctx.update('music', changes)
    song = SONGS[state['music']['currentIndex']]['name']
    return ctx.result('音乐状态已更新：' + song, ['music'], {'music': state['music']})
