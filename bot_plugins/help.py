import nonebot
from nonebot import on_command, CommandSession

__plugin_name__ = 'help'
__plugin_usage__ = '''恭喜你发现彩蛋一枚(然并卵)'''

@on_command('help', aliases=['usage','Help'])
async def _(session: CommandSession):
    # 获取设置了名称的插件列表
    plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))

    arg = session.current_arg_text.strip().lower()
    if not arg:
        # 如果用户没有发送参数，则发送功能列表
        await session.send(
            '我现在支持的功能有：' + \
            '\n'.join(p.name for p in plugins) + \
            '\n/help <插件名>以查看插件的具体帮助')
        return

    # 如果发了参数则发送相应命令的使用帮助
    for p in plugins:
        if p.name.lower() == arg:
            await session.send(p.usage)