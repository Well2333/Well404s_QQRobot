import json,os
#——————获取data的目录——————
path = f"{os.getcwd()}\\Well404\\bot_plugins\\basic_reply\\data"
#——————处理传入信息——————
class LoadReply:
    def __init__(self):
        with open(f"{path}\\universal.json", 'r') as f:
            self.universal_reply = json.load(f)      
        self.pravite_reply = {"key_max_len":50,"value_max_len":50}      
    #解析ctx_id
    def ctx_id(self,ctx_id):
        if ctx_id == "universal":
            return "universal"
        elif "group" in ctx_id:
            ctx_id = ctx_id.replace("/","T")
            ctx_id,_ = ctx_id.split("Tuser")
            return ctx_id
        else:
            ctx_id = ctx_id.replace("/","T")
            return ctx_id
    #查询key和value最长长度
    def key_max_len(self,ctx_id):
        ctx_id = self.ctx_id(ctx_id)
        try:
            with open(f'{path}\\{ctx_id}.json', 'r') as f:
                pravite_reply = json.load(f)
            try:
                return pravite_reply["key_max_len"]
            #如果无法找到键值，则新建一个
            except:
                pravite_reply["key_max_len"] = 50
                with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                    json.dump(pravite_reply,f)
                return "50"
        #如无法读取，则新建一个
        except:
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(self.pravite_reply,f)     
            return "!!!无法读取私有回复数据文件，已重置为默认值!!!"
    def value_max_len(self,ctx_id):
        ctx_id = self.ctx_id(ctx_id)
        try:
            with open(f'{path}\\{ctx_id}.json', 'r') as f:
                pravite_reply = json.load(f)
            try:
                return pravite_reply["value_max_len"]
            #如果无法找到键值，则新建一个
            except:
                pravite_reply["value_max_len"] = 50
                with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                    json.dump(pravite_reply,f)
                return "50"
        #如无法读取，则新建一个
        except:
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(self.pravite_reply,f)     
            return "!!!无法读取私有回复数据文件，已重置为默认值!!!"
    #优先搜索私有数据库，若无则尝试搜索共有数据库   
    def key_is_exist(self,ctx_id,inputstr):
        ctx_id = self.ctx_id(ctx_id)
        #尝试寻找私有数据库
        try:
            with open(f'{path}\\{ctx_id}.json', 'r') as f:
                pravite_reply = json.load(f)
            if inputstr in pravite_reply:
                return pravite_reply[inputstr]
            else:
                for key in list(pravite_reply.keys()):
                    if key in inputstr:
                        return pravite_reply[key]
        #如无法读取，则新建一个
        except:
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(self.pravite_reply,f)     
        #寻找共有部分      
        if inputstr in self.universal_reply:
            return self.universal_reply[inputstr]
        else:
            for key in self.show_keys():
                if key in inputstr:
                    return self.universal_reply[key]

        return "None"
    #增添关键词
    def add_key(self,key_str,value_str,ctx_id="universal"):
        ctx_id = self.ctx_id(ctx_id)
        #共有
        if ctx_id == "universal":
            self.universal_reply[key_str] = value_str
            with open(f'{path}\\universal.json', 'w+') as f:
                json.dump(self.universal_reply,f)
        #私有
        else:
            #尝试读取原有数据库
            try:
                with open(f'{path}\\{ctx_id}.json', 'r') as f:
                    pravite_reply = json.load(f)
            #如无法读取，则新建一个
            except: 
                pravite_reply = {}
            #覆写原有数据库
            pravite_reply[key_str] = value_str
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(pravite_reply,f)
    #删除关键词
    def del_key(self,key_str,ctx_id="universal"):
        ctx_id = self.ctx_id(ctx_id)
        #共有
        if ctx_id == "universal":
            del self.universal_reply[key_str]
            with open(f'{path}\\universal.json', 'w+') as f:
                json.dump(self.universal_reply,f)
        #私有
        else:
            #尝试覆写原有数据库
            try:
                with open(f'{path}\\{ctx_id}.json', 'r') as f:
                    pravite_reply = json.load(f)
                del pravite_reply[key_str]
            #如无法读取，则新建一个
            except:
                pravite_reply = {}
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(pravite_reply,f)
    #展示完整列表
    def show_keys(self,ctx_id="universal"):
        ctx_id = self.ctx_id(ctx_id)
        if ctx_id == "universal":
            return list(self.universal_reply.keys())
        else:
            try:
                with open(f'{path}\\{ctx_id}.json', 'r') as f:
                    pravite_reply = json.load(f)
            except:
                with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                    json.dump(self.pravite_reply,f) 
                pravite_reply = self.pravite_reply
            return list(pravite_reply.keys())  
    #清空关键词
    def clear_keys(self,ctx_id="universal"):
        ctx_id = self.ctx_id(ctx_id)
        #共有
        if ctx_id == "universal":
            self.universal_reply.clear()
            self.universal_reply['测试'] = '成功'
            with open(f"{path}\\universal.json", 'w+') as f:
                json.dump(self.universal_reply,f)
        #私有
        else:
            with open(f'{path}\\{ctx_id}.json', 'w+') as f:
                json.dump(self.pravite_reply,f)         

Load_Reply = LoadReply()
__all__ = ["Load_Reply",]