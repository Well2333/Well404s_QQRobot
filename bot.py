from os import path,getcwd
import nonebot,bot_config

for i in range(0,5):
    print(f'当前工作路径为:{getcwd()}')
nonebot.init(bot_config)
# 第一个参数为插件路径，第二个参数为插件前缀（模块的前缀）
nonebot.load_plugins(path.join(path.dirname(__file__), 'bot_plugins'), 'bot_plugins')

if __name__ == '__main__':
    nonebot.run()