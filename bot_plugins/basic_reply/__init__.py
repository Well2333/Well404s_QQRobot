import sys,os
sys.path.append(os.getcwd()+r"\Well404\bot_plugins\basic_reply")
from nonebot import *
from nonebot.permission import *
from LoadReply import Load_Reply

__plugin_name__ = 'basic_reply'
__plugin_usage__ = '''根据不同的关键字返回特定的回复
————具体用法————
添加一个特定回复
/add key=value
删除一个特定回复
/del key
清空特定回复列表(在群聊内仅管理员及以上)
/clear
查看已有的特定回复
/show
查看全局特定回复
/showu
'''
#乒乓球(Bushi)
@on_command('ping',only_to_me=False)
async def _(session: CommandSession):
    await session.send('pong!')
#——————回答模块——————
#返回回答
@on_command('send_reply')
async def _(session: CommandSession):
    await session.send(replymsg)
#检查关键词是否有对应的回答
@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    global replymsg
    ctx_id = context_id(session.event)
    raw_msg = session.msg_text.strip()
    replymsg = Load_Reply.key_is_exist(ctx_id,raw_msg)
    if not replymsg == "None":
        return IntentCommand(61.0,'send_reply')
#——————仅私有——————
#增添私有关键词
@on_command('add_key',aliases=['add','addkey'],only_to_me=False)
async def _(session: CommandSession):
    ctx_id = context_id(session.event)
    stripped_arg = session.current_arg_text.strip()
    key_str,value_str = stripped_arg.split("=")
    mvl = Load_Reply.value_max_len(ctx_id)
    mkl = Load_Reply.key_max_len(ctx_id)
    if len(value_str)>mvl or len(key_str)>mkl:
        if len(value_str)>mvl:
            await session.send(f"‘{value_str}’作为value过长，目前最大长度为{mvl}个字")
        if len(key_str)>mkl:
            await session.send(f"‘{key_str}’作为key过长，目前最大长度为{mkl}个字")   
    else:
        Load_Reply.add_key(ctx_id = ctx_id,key_str = key_str,value_str = value_str)
        await session.send(f"已添加私有关键词{key_str}=>{value_str}")
#删除私有关键词
@on_command('del_key',aliases=["del","delkey"],only_to_me=False)
async def _(session: CommandSession):
    ctx_id = context_id(session.event)
    Load_Reply.del_key(ctx_id = ctx_id,key_str = session.current_arg_text.strip())
    await session.send(f"已删除私有关键词{session.current_arg_text.strip()}")
#清空私有关键词列表
@on_command('clear_keys',permission=(SUPERUSER|GROUP_ADMIN|PRIVATE_FRIEND),aliases=["clear",'clearkeys'],only_to_me=False)
async def _(session: CommandSession):
    ctx_id = context_id(session.event)
    Load_Reply.clear_keys(ctx_id = ctx_id)
    await session.send("已清空私有关键词列表")
#查看私有关键词
@on_command('show_key',aliases=["show",'showkey'],only_to_me=False)
async def _(session: CommandSession):
    lst = Load_Reply.show_keys(ctx_id = context_id(session.event))
    await session.send('私有关键词列表：\n'+str(lst))
#——————共有——————
#增添共有关键词
@on_command('add_key_universal',permission=SUPERUSER,aliases=['addu','addkeyuniversal'],only_to_me=False)
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    key_str,value_str = stripped_arg.split("=")
    Load_Reply.add_key(key_str = key_str,value_str = value_str)
    await session.send(f"已添加共有关键词{key_str}=>{value_str}")
#删除共有关键词
@on_command('del_key_universal',permission=SUPERUSER,aliases=["delu","delkeyuniversal"],only_to_me=False)
async def _(session: CommandSession):
    Load_Reply.del_key(key_str = session.current_arg_text.strip())
    await session.send(f"已删除共有关键词{session.current_arg_text.strip()}")
#清空私有关键词列表
@on_command('clear_keys_universal',permission=SUPERUSER,aliases=["clearu",'clearkeysuniversal'],only_to_me=False)
async def _(session: CommandSession):
    Load_Reply.clear_keys()
    await session.send("已清空共有关键词列表")
#查看共有关键词
@on_command('show_key_universal',aliases=["showu",'showkeyuniversal'],only_to_me=False)
async def _(session: CommandSession):
    lst = Load_Reply.show_keys()
    await session.send('共有关键词列表：\n'+str(lst))
