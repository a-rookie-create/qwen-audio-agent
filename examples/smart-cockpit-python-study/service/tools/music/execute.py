"""10 个音乐工具；演示曲库与共享状态都在业务侧。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult

SONGS = [{'id': 'sunny', 'name': '晴天'}, {'id': 'river', 'name': '七里香'}, {'id': 'night', 'name': '夜曲'}]


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    music = ctx.snapshot()['music']
    query = args.get('query', '')
    matches = [s for s in SONGS if query in s['name']]
    if name == 'music_state_query':
        return ctx.result('当前音乐状态', data={'music': music})
    changes: dict = {}
    if name == 'music_search':
        changes['results'] = matches
    elif name == 'music_play':
        if query and not matches:
            raise ValueError('演示曲库中没有这首歌')
        changes = {'playing': True, 'currentIndex': SONGS.index(matches[0]) if query else music['currentIndex']}
    elif name in {'music_pause', 'music_toggle_playback'}:
        changes['playing'] = False if name == 'music_pause' else not music['playing']
    elif name in {'music_next', 'music_previous'}:
        changes['currentIndex'] = (music['currentIndex'] + (1 if name == 'music_next' else -1)) % len(SONGS)
    elif name == 'music_source_control':
        changes['source'] = args['source']
    elif name == 'music_volume_control':
        action = args['action']
        if action in {'mute', 'unmute'}:
            changes['muted'] = action == 'mute'
        else:
            volume = args.get('volume', music['volume']) if action == 'set' else music['volume'] + (
                args.get('delta', 1) if action == 'increase' else -args.get('delta', 1))
            changes['volume'] = min(11, max(0, volume))
    elif name == 'music_favorite_control':
        action = args.get('action', 'toggle')
        if action in {'next', 'previous'}:
            indices = [i for i, s in enumerate(SONGS) if s['id'] in music['favoriteIds']]
            if not indices:
                raise ValueError('尚无收藏歌曲')
            changes['currentIndex'] = indices[0 if action == 'next' else -1]
        else:
            song = matches[0] if query and matches else SONGS[music['currentIndex']]
            favorites = list(music['favoriteIds'])
            if action == 'remove' or (action == 'toggle' and song['id'] in favorites):
                favorites = [item for item in favorites if item != song['id']]
            elif song['id'] not in favorites:
                favorites.append(song['id'])
            changes['favoriteIds'] = favorites
    else:
        raise ValueError('未知音乐工具')
    state = ctx.update('music', changes)
    song = SONGS[state['music']['currentIndex']]['name']
    return ctx.result('音乐状态已更新：' + song, ['music'], {'music': state['music']})
