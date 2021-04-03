from nonebot import *
from nonebot.permission import *
import time as t

__plugin_name__ = 'repeter'
__plugin_usage__ = '''手动复读机，群聊中仅管理员及以上可触发
————具体用法————
/re c=复读次数 复读内容
复读次数应为大于等于1的正整数
若无c=，则默认复读三次'''

debugmod = False
replymsg = 'None'

@on_command('repeter',permission=(SUPERUSER|GROUP_ADMIN|PRIVATE_FRIEND),aliases=["re",'Repeter'],only_to_me=False)
async def _(session: CommandSession):
    temp = session.current_arg.strip()
    if "c=" in temp:
        count_temp,replymsg = temp.split(' ')
        _,counts = count_temp.split('=')
    else:
        counts = 3
        replymsg = temp
    for _ in range(0,int(counts)):
        t.sleep(0.2)
        await session.send(replymsg)

