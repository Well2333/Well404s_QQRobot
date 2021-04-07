from nonebot import *
from nonebot.permission import *
import sqlite3,time

debugmod = False

__plugin_name__ = 'blacklist'
__plugin_usage__ = '''将群聊中的成员添加至黑名单，机器人将不再响应此人的任何消息，仅管理员及以上可以使用
————具体用法————
1、添加某个用户至黑名单
/blist qq=<qq号> func={功能名1&功能名2&功能名3&……} retime={时长}
注:其中qq=<qq号>部分可以直接@对应的成员，如/blist @群内鬼
func=部分为选填部分，若填写则仅禁用这些功能，若不填写则禁用全部功能;
功能名可在/help <插件名>中查询，填写格式例如add&del&ping
retime=部分为选填部分，若填写则仅禁用{时长}个小时，若不填写则永久禁用。
2、将用户移除黑名单
/blist qq=<qq号> remove
注:此处qq号如果为all，则会清空全部黑名单
3、查看黑名单列表
/blist show
4、查看具体信息
/blist qq=<qq号> check
————使用提示————
1、<参数>中的"<"和">"无需打出来，且表示为必填参数，不可省略。
2、{参数}中的"{"和"}"无需打出来，且表示为可选参数，可以省略。'''
#分析数据，操作数据库
class DB:
    def __init__(self):
        self.conn = sqlite3.connect("DB\\blacklist.db")
        self.cur = self.conn.cursor()
    #解析群组或用户身份ID
    def context_id_analysis(self,context_id):
        if "group" in context_id:
            context_id_temp = context_id.replace("/","T")
            context_id_temp,userid = context_id_temp.split("TuserT")
            groupid = context_id_temp.lstrip("TgroupT")
            context_id_analyzed = {"groupid":f"group{groupid}", "userid":userid}
        else:
            context_id_analyzed = {"groupid":"user", "userid":"user"}
        if debugmod:
            print(f'——————context_id_analysis:——————\
                    \n{str(context_id_analyzed)}\
                    \n————————————————————————————————')        
        return context_id_analyzed
    #解析命令部分,并调用对应的模块进行执行
    def analysis(self,current_arg,context_id):
        context_id_analyzed = self.context_id_analysis(context_id)
        #判断是否是私人聊天
        if context_id_analyzed["groupid"] == "user":
            return '你是认真的吗？这可是私人聊天啊'
        #若不是则开始执行
        current_arg = current_arg.strip()
        #判断是否为show指令
        if "show" in current_arg:
            return f'现在处于黑名单的qq号为：\n{self.check("all",context_id_analyzed)}'
        #切片
        userid = 'non'
        funcs = []
        retime=9999999999999.00
        for msg in current_arg.split(' '):
            if debugmod:
                print(f'——————blacklist_msg:——————\
                        \nmsg:{msg}\
                        \n————————————————————————————————') 
            #查找对应的字段，并分析               
            if "qq=" in msg:
                _,userid = msg.split('=')
                userid = int(userid.rstrip(']'))
            elif "func=" in msg:
                _,func_raw = msg.split('=')
                for func in func_raw.split('&'):
                    funcs.append(func)
            elif "retime=" in msg:
                _,retime_raw = msg.split('=')
                retime = float(f'{(float(retime_raw)*3600 + time.time()):.2f}')
            elif "check" in msg:
                returnmsg = self.check(userid,context_id_analyzed)
                if not returnmsg['userid'] == 'non':
                    return f"QQ号:{returnmsg['userid']}\
                            \n禁用的功能:{returnmsg['disabledfunc']}\
                            \n添加者QQ号:{returnmsg['adderid']}\
                            \n剩余封禁时长:{((float(returnmsg['releasetime'])-time.time())/3600):.2f}h"
                else:
                    return '此QQ号并未在黑名单中'
            elif "remove" in msg:
                return self.remove(userid,context_id_analyzed)
        if debugmod:
            print(f'——————blacklist_analysis:——————\
                    \nuserid:{userid}\
                    \ncontext_id_analyzed:{context_id_analyzed}\
                    \nfuncs:{funcs}\
                    \nretime:{retime}\
                    \n————————————————————————————————')             
        return self.add(userid,context_id_analyzed,funcs,retime)        
    #创建新表
    def creat_table(self,context_id_analyzed):
        self.cur.execute(
            f'''CREATE TABLE "{context_id_analyzed["groupid"]}"
            ("id"	INTEGER NOT NULL UNIQUE,
	        "userid"	INTEGER NOT NULL,
	        "disabledfunc"	BLOB NOT NULL,
	        "adderid"	INTEGER NOT NULL,
	        "releasetime"	BLOB NOT NULL,
	        PRIMARY KEY("id" AUTOINCREMENT))'''
            )
        self.conn.commit()
    #查询对应信息
    def check(self,userid,context_id_analyzed):
        returnmsg = {"userid"	   :"non",
                     "disabledfunc":"non",
                     "adderid"	   :"non",
                     "releasetime" :"non",
                     "db":"non"}
        try:
            dbname = context_id_analyzed["groupid"]
            allinfo = self.cur.execute(f'SELECT userid, disabledfunc, adderid, releasetime, releasetime \
                                       from "{dbname}"')
            #判断是否为show指令
            if str(userid) == 'all':
                keylist = []
                for row in allinfo:
                    keylist.append(row[0])
                return keylist
            for row in allinfo:
                if debugmod:
                    print(str(row[0]))
                if str(row[0]) == str(userid):
                    returnmsg = {"userid"	  :row[0],
                                "disabledfunc":row[1],
                                "adderid"	  :row[2],
                                "releasetime" :row[3],
                                'db':dbname}            
        except sqlite3.OperationalError:
            self.creat_table(context_id_analyzed)
            returnmsg = {"userid"	  :"non",
                        "disabledfunc":"non",
                        "adderid"	  :"non",
                        "releasetime" :"non",
                        "db":"just_builded"}
        if debugmod:
            print(f'——————returnmsg:——————\
                    \n{str(returnmsg)}\
                    \n———————————————————————')     
        return returnmsg
    #添加新id
    def add(self,userid,context_id_analyzed,func,retime):
        if userid == 'non':
            return f'QQ号格式不正确，添加失败'    
        try:
            returnmsg = self.check(userid,context_id_analyzed)
            if func == []:
                func = '全部'
            if returnmsg['userid'] == 'non':
                self.cur.execute(f'''INSERT INTO {context_id_analyzed["groupid"]} (userid, disabledfunc, adderid, releasetime)
                    VALUES ("{userid}", "{func}", "{context_id_analyzed["userid"]}", "{((float(retime)-time.time())/3600):.2f}")''')
                self.conn.commit()
                return f'''已成功禁用{userid}的{func}功能，时长为{retime}h'''
            else:
                self.cur.execute(f'''UPDATE "{context_id_analyzed["groupid"]}" 
                                    SET disabledfunc = "{func}", releasetime = "{retime}", adderid = {context_id_analyzed["userid"]} 
                                    WHERE userid = "{returnmsg['userid']}"''')                       
                self.conn.commit()  
                return f'''已成功更新禁用{userid}的{func}功能,时长为{((float(retime)-time.time())/3600):.2f}h'''  
        #若数据库连接失败则新建一个 
        except sqlite3.OperationalError:
            self.creat_table(context_id_analyzed)
            return f'已新建本群的数据表，请重新输入一次指令'
    #移除id
    def remove(self,userid,context_id_analyzed):
        try:
            if userid == 'all':
                self.cur.execute(f'''DELETE FROM "{context_id_analyzed["groupid"]}"''')
                self.conn.commit()
                return '已成功清空黑名单'
            else:                
                returnmsg = self.check(userid,context_id_analyzed)
                if not returnmsg['userid'] == 'non':
                    self.cur.execute(f'''DELETE FROM "{context_id_analyzed["groupid"]}"  
                                    WHERE userid = "{returnmsg['userid']}"''')
                    self.conn.commit()  
                    return f'''已成功将{returnmsg['userid']}移除黑名单'''      
                else:
                    return '此QQ号并未在黑名单中'
        except sqlite3.OperationalError:
            self.creat_table(context_id_analyzed)
            return '此QQ号并未在黑名单中'
#实例化
db = DB()
#提供给别的插件查询用的接口
async def check(funcname,context_id):
    context_id_analyzed = db.context_id_analysis(context_id)
    if context_id_analyzed["groupid"] == 'user':
        return True
    else:
        userid = context_id_analyzed["userid"]
        returnmsg = db.check(userid,context_id_analyzed)
        if returnmsg['disabledfunc'] == 'non':
            return True
        elif returnmsg['disabledfunc'] == '全部':
            return False
        elif float(returnmsg['releasetime']) < time.time():
            db.remove(userid,context_id_analyzed)
            return True
        elif funcname in returnmsg['disabledfunc']:
            return False
        else:
            return True
#获取指令
@on_command('black_list',permission=(SUPERUSER|GROUP_ADMIN),aliases=['blist','BlackList'],only_to_me=False)
async def _(session: CommandSession):
    if await check('blist',context_id(session.event)):
        await session.send(db.analysis(session.current_arg,context_id(session.event)))