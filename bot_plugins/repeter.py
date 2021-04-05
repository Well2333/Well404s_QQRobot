from nonebot import *
from nonebot.permission import *

__plugin_name__ = 'repeter'
__plugin_usage__ = '''手动复读机，群聊中仅管理员及以上可触发
————具体用法————
/re c=复读次数 复读内容
复读次数应为大于等于1的正整数
若无c=，则默认复读三次
/remax 数值
设定最大的复读次数，且不低于3次
默认最大10次，且重启后重置为10次'''

debugmod = False
replymsg = 'None'
maxcount = 10

@on_command('repeter',permission=(SUPERUSER|GROUP_ADMIN|PRIVATE_FRIEND),aliases=["re",'Repeter'],only_to_me=False)
async def _(session: CommandSession):
    temp = session.current_arg.strip()
    if "c=" in temp:
        count_temp,replymsg = temp.split(' ')
        _,counts = count_temp.split('=')
    else:
        counts = 2
        replymsg = temp
    if int(counts) < maxcount:
        for _ in range(0,int(counts)+1):
            await session.send(replymsg)
    else:
        await session.send('你要复读多少次啊kora!!!')

@on_command('repeter_max_count',permission=(SUPERUSER|GROUP_ADMIN|PRIVATE_FRIEND),aliases=["remax",'RepeterMaxCount'],only_to_me=False)
async def _(session: CommandSession):
    global maxcount
    temp = int(session.current_arg.strip())
    if temp < 3:
        await session.send(f'最大复读次数不得小于3次')
    else:
        ex_maxcount = maxcount
        maxcount = temp
        await session.send(f'最大复读次数已由{ex_maxcount}次变更为{maxcount}次')