from nonebot import *
from nonebot.permission import *
import sqlite3

debugmod = False

__plugin_name__ = 'basic_reply2'
__plugin_usage__ = '''根据不同的关键字返回特定的回复
————具体用法————
添加一个特定回复
/add key===value <pri=优先度>
删除一个特定回复
/del key
清空特定回复列表(在群聊内仅管理员及以上)
/clear
查看已有的特定回复
/show
/showu(全局)
查看单个特定回复的详细信息
/check key
/checku key
'''

#分析数据，操作数据库
class DB:
    #连接数据库
    def __init__(self):
        self.conn = sqlite3.connect("DB\\reply.db")
        self.cur = self.conn.cursor()
    #——————解析部分——————
    #解析群组或用户身份ID
    def context_id_analysis(self,context_id = "universal"):
        if context_id == "universal":
            return "universal"
        elif "group" in context_id:
            context_id_temp = context_id.replace("/","T")
            context_id_temp,userid = context_id_temp.split("TuserT")
            groupid = context_id_temp.lstrip("TgroupT")
            context_id_analyzed = {"groupid":f"group{groupid}", "userid":userid}
        else:
            userid = (context_id.replace("/","T")).lstrip("TuserT")
            context_id_analyzed = {"groupid":f"user{userid}", "userid":userid}
        if debugmod:
            print(f'——————context_id_analysis:——————\
                    \n{str(context_id_analyzed)}\
                    \n————————————————————————————————')        
        return context_id_analyzed
    #解析具体内容
    def current_arg_analysis(self,current_arg):
        current_arg = current_arg.strip()
        if "pri=" in current_arg:
            current_arg,priority = current_arg.split('pri=')
            priority = int(priority)
            current_arg = current_arg.strip()
        else:
            priority = 50
        keyword,replyword = current_arg.split("===")
        if 'image' in keyword:
            for temp in keyword.split(','):
                if 'file=' in temp:
                    keyword = temp
        current_arg_analyzed = {"keyword"  :keyword, 
                                "replyword":replyword, 
                                "priority" :priority}
        if debugmod:
            print(f'——————current_arg_analysis:——————\
                    \n{str(current_arg_analyzed)}\
                    \n————————————————————————————————')
        return current_arg_analyzed    
    #精确搜索
    def precise_search(self,inputmsg,context_id,only_private=False):
        context_id_analyzed = self.context_id_analysis(context_id)
        #优先搜素私有关键词
        if not context_id == "universal":
            try:
                allinfo = self.cur.execute(f'SELECT keyword, replyword, userid, priority, usedcount from "{context_id_analyzed["groupid"]}" ORDER BY priority DESC')
                for row in allinfo:
                    print(str(row[0]))
                    if (str(row[0]) in inputmsg) or (str(row[0]) == inputmsg):
                        returnmsg = {'keyword' :row[0],
                                    'replyword':row[1],
                                    'userid'   :row[2],
                                    'priority' :row[3],
                                    'usedcount':row[4]}
                        if debugmod:
                            print(f'——————returnmsg:——————\
                                    \n{str(returnmsg)}\
                                    \n———————————————————————')
                        return returnmsg              
            except sqlite3.OperationalError:
                self.creat_table(context_id_analyzed)
                returnmsg = {'keyword' :'non',
                            'replyword':'non',
                            'userid'   :'non',
                            'priority' :'non',
                            'usedcount':'non'}
                if debugmod:
                    print(f'——————returnmsg:——————\
                            \n{str(returnmsg)}\
                            \n———————————————————————')     
                return returnmsg
        #搜索通用关键词
        if not only_private:
            allinfo = self.cur.execute(f'SELECT keyword, replyword, userid, priority, usedcount from universal ORDER BY priority DESC')
            for row in allinfo:
                if row[0] in inputmsg:
                    returnmsg = {'keyword' :row[0],
                                'replyword':row[1],
                                'userid'   :row[2],
                                'priority' :row[3],
                                'usedcount':row[4]}
                    if debugmod:
                        print(f'——————returnmsg:——————\
                                \n{str(returnmsg)}\
                                \n———————————————————————')
                    return returnmsg
        returnmsg = {'keyword' :'non',
                    'replyword':'non',
                    'userid'   :'non',
                    'priority' :'non',
                    'usedcount':'non'}
        if debugmod:
            print(f'——————returnmsg:——————\
                    \n{str(returnmsg)}\
                    \n———————————————————————')                
        return returnmsg        
    #——————执行部分——————
    #创建新表
    def creat_table(self,context_id_analyzed):
        self.cur.execute(
            f'''CREATE TABLE "{context_id_analyzed["groupid"]}"
            ("Id"	INTEGER NOT NULL UNIQUE,
            "keyword"	BLOB NOT NULL UNIQUE,
            "replyword"	BLOB NOT NULL,
            "userid"	BLOB NOT NULL,
            "priority"	INTEGER NOT NULL DEFAULT 50,
            "usedcount"	INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY("Id" AUTOINCREMENT))'''
            )
        self.conn.commit()
    #添加字段,若已经存在则修改字段
    def insert(self,current_arg,context_id):
        current_arg_analyzed = self.current_arg_analysis(current_arg)
        if context_id == 'universal':
            returnmsg = self.precise_search(current_arg_analyzed['keyword'],'universal')            
            if returnmsg['keyword'] == 'non':
                
                self.cur.execute(f'''INSERT INTO 'universal' (keyword, replyword, userid, priority)
                    VALUES ("{current_arg_analyzed['keyword']}", "{current_arg_analyzed['replyword']}", "superuser", "{current_arg_analyzed['priority']}")''')
                self.conn.commit()
                return f'''已成功添加通用关键词{current_arg_analyzed['keyword']} ==> {current_arg_analyzed['replyword']}'''
            else:
                if current_arg_analyzed['priority'] == 50:
                    self.cur.execute(f'''UPDATE 'universal'
                                        SET replyword = "{current_arg_analyzed['replyword']}" 
                                        WHERE keyword = "{returnmsg['keyword']}"''')
                else:
                    self.cur.execute(f'''UPDATE 'universal'
                                        SET replyword = "{current_arg_analyzed['replyword']}", priority = "{current_arg_analyzed['priority']}" 
                                        WHERE keyword = "{returnmsg['keyword']}"''')
                self.conn.commit()  
                return f'''已成功修改通用关键词{current_arg_analyzed['keyword']} ==> {current_arg_analyzed['replyword']}'''      
        else:
            context_id_analyzed = self.context_id_analysis(context_id)
            returnmsg = self.precise_search(current_arg_analyzed['keyword'],context_id,only_private=True)
            if returnmsg['keyword'] == 'non':
                self.cur.execute(f'''INSERT INTO {context_id_analyzed["groupid"]} (keyword, replyword, userid, priority)
                    VALUES ("{current_arg_analyzed['keyword']}", "{current_arg_analyzed['replyword']}", "{context_id_analyzed["userid"]}", "{current_arg_analyzed['priority']}")''')
                self.conn.commit()
                return f'''已成功添加{current_arg_analyzed['keyword']} ==> {current_arg_analyzed['replyword']}'''
            else:
                if current_arg_analyzed['priority'] == 50:
                    self.cur.execute(f'''UPDATE "{context_id_analyzed["groupid"]}"
                                        SET replyword = "{current_arg_analyzed['replyword']}" 
                                        WHERE keyword = "{returnmsg['keyword']}"''')
                else:
                    self.cur.execute(f'''UPDATE "{context_id_analyzed["groupid"]}" 
                                        SET replyword = "{current_arg_analyzed['replyword']}", priority = "{current_arg_analyzed['priority']}" 
                                        WHERE keyword = "{returnmsg['keyword']}"''')                       
                self.conn.commit()  
                return f'''已成功修改{current_arg_analyzed['keyword']} ==> {current_arg_analyzed['replyword']}'''      

    #删除\清空字段
    def delete(self,current_arg,context_id):
        if context_id == "universal":
            if current_arg == 'all':
                self.cur.execute(f'''DELETE FROM "universal"''')
                self.conn.commit()
                return '已成功清空全部关键词'
            else:                
                returnmsg = self.precise_search(current_arg,context_id)
                if not returnmsg['keyword'] == 'non':
                    self.cur.execute(f'''DELETE FROM "universal"  
                                    WHERE keyword = "{returnmsg['keyword']}"''')
                    self.conn.commit()  
                    return f'''已成功删除{returnmsg['keyword']} ==> {returnmsg['replyword']}'''      
                else:
                    return '未找到此关键词'
        else:
            context_id_analyzed = self.context_id_analysis(context_id)
            if current_arg == 'all':
                self.cur.execute(f'''DELETE FROM "{context_id_analyzed["groupid"]}"''')
                self.conn.commit()
                return '已成功清空全部关键词'
            else:
                returnmsg = self.precise_search(current_arg,context_id)
                if not returnmsg['keyword'] == 'non':
                    self.cur.execute(f'''DELETE FROM "{context_id_analyzed["groupid"]}"  
                                    WHERE keyword = "{returnmsg['keyword']}"''')
                    self.conn.commit()  
                    return f'''已成功删除{returnmsg['keyword']} ==> {returnmsg['replyword']}'''      
                else:
                    return '未找到此关键词'
    #查看全部关键词
    def check(self,context_id):
        keylist = []
        if context_id == 'universal':
            allinfo = self.cur.execute(f'SELECT keyword, replyword, userid, priority, usedcount from universal ORDER BY priority DESC')            
            for row in allinfo:
                keylist.append(row[0])
        else:
            context_id_analyzed = self.context_id_analysis(context_id)
            try:
                allinfo = self.cur.execute(f'SELECT keyword, replyword, userid, priority, usedcount from "{context_id_analyzed["groupid"]}" ORDER BY priority DESC')
                for row in allinfo:
                    keylist.append(row[0])
            except sqlite3.OperationalError:
                self.creat_table(context_id_analyzed)   
        return keylist
#实例化            
db = DB()
replymsg = {}
#乒乓球(bushi)
@on_command('ping',only_to_me=False)
async def _(session: CommandSession):
    await session.send('pong!')
#——————————————自然语言处理——————————————
#返回回答
@on_command('send_reply')
async def _(session: CommandSession):
    await session.send(replymsg['replyword'])
#检查关键词是否有对应的回答
@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    global replymsg
    if debugmod:
        print(f'——————session.msg:——————\
                \n{session.msg.strip()}\
                \n———————————————————————')
    replymsg = db.precise_search(session.msg.strip(),context_id(session.event))
    if not replymsg['keyword'] == "non":
        return IntentCommand(61.0,'send_reply')
#——————————————通用数据库操作——————————————
#增添通用关键词
@on_command('add_key_universal',permission=SUPERUSER,aliases=['addu','addkeyuniversal'],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.insert(session.current_arg,'universal'))
#删除通用关键词
@on_command('del_key_universal',permission=SUPERUSER,aliases=["delu","delkeyuniversal"],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.delete(session.current_arg,'universal'))
#清空通用关键词列表
@on_command('clear_keys_universal',permission=SUPERUSER,aliases=["clearu",'clearkeysuniversal'],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.delete('all','universal'))
#查看通用关键词列表
@on_command('show_key_universal',aliases=["showu",'showkeyuniversal'],only_to_me=False)
async def _(session: CommandSession):
    await session.send('通用关键词列表：\n'+str(db.check('universal')))
#查看单个通用关键词的详细信息
@on_command('check_key_universal',aliases=["checku",'checkkeyuniversal'],only_to_me=False)
async def _(session: CommandSession):
    info = db.precise_search(session.current_arg,'universal')
    await session.send(f"通用关键词信息:\
                        \n关键词名:{info['keyword']}\
                        \n回复内容:{info['replyword']}\
                        \n添加者id:{info['userid']}\
                        \n优先度:{info['priority']}\
                        \n累计使用次数:{info['usedcount']}")
#——————————————私有数据库操作——————————————
#增添私有关键词
@on_command('add_key',aliases=['add','addkey'],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.insert(session.current_arg,context_id(session.event)))
#删除私有关键词
@on_command('del_key',aliases=["del","delkey"],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.delete(session.current_arg,context_id(session.event)))
#清空私有关键词列表
@on_command('clear_keys',permission=(SUPERUSER|GROUP_ADMIN|PRIVATE_FRIEND),aliases=["clear",'clearkeys'],only_to_me=False)
async def _(session: CommandSession):
    await session.send(db.delete('all',context_id(session.event)))
#查看私有关键词列表
@on_command('show_key',aliases=["show",'showkey'],only_to_me=False)
async def _(session: CommandSession):
    await session.send('私有关键词列表：\n'+str(db.check(context_id(session.event))))
#查看单个私有关键词的详细信息
@on_command('check_key',aliases=["check",'checkkey'],only_to_me=False)
async def _(session: CommandSession):
    info = db.precise_search(session.current_arg,context_id(session.event))
    await session.send(f"私有关键词信息:\
                        \n关键词名:{info['keyword']}\
                        \n回复内容:{info['replyword']}\
                        \n添加者id:{info['userid']}\
                        \n优先度:{info['priority']}\
                        \n累计使用次数:{info['usedcount']}")
                       