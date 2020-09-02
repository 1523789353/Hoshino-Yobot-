import asyncio
#import json
#import ujson
import platform
import os
import sys
import random
#import sqlite3
import time
import datetime
from typing import Any, Dict, Union
from aiocqhttp.api import Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from quart import Quart
#from .web_util import rand_string



class Auto_Reply:
    def __init__(self,
                 glo_setting: Dict[str, Any],
                 scheduler: AsyncIOScheduler,
                 app: Quart,
                 bot_api: Api,
                 *args, **kwargs):
        self.evn = glo_setting["verinfo"]["run-as"]
        self.path = glo_setting["dirname"]
        self.working_path = os.path.abspath('.\hoshino\modules\yobot\src\client')
        self.ver = glo_setting["verinfo"]
        self.setting = glo_setting
        self.api = bot_api
        self.images_foler = os.path.join(os.path.abspath('.'), 'res', 'img')
        print("[Yobot]自动回复模块已加载")


    def GetSign(self, UID, Date):
        #抽签方法
        LotsDB = "{}/LotsDB/{}".format(self.path,UID)
        if not os.path.isdir(LotsDB):
            os.makedirs(LotsDB,0o0755)
        Reply = "[CQ:at,qq={}]".format(UID)
        if os.path.isfile("{}/{}".format(LotsDB,Date)):
            Reply += "今天已经抽过签了!\n"
        else:
            with open("{}/{}".format(LotsDB,Date), "w", encoding='utf-8') as Num:
                Num.write(str(random.randint(1,364)))
        Reply += "今天抽到的签是:"
        with open("{}/{}".format(LotsDB,Date), "r", encoding='utf-8') as Num:
            Line = int(Num.read())
            with open("{}/ybplugins/Lots.yml".format(self.working_path), "r", encoding='utf-8') as Lot:
                Texts = Lot.readlines()
                Reply += "\n\n{}{}".format(Texts[Line*3-3], Texts[Line*3-2])
        Reply += "\n发送【解签】解读签文"
        return Reply


    def GetUnSign(self, UID, Date):
        #解签方法
        LotsDB = "{}/LotsDB/{}".format(self.path,UID)
        Reply = "[CQ:at,qq={}]".format(UID)
        if os.path.isfile("{}/{}".format(LotsDB,Date)):
            with open("{}/{}".format(LotsDB,Date), "r", encoding='utf-8') as Num:
                Line = int(Num.read())
                with open("{}/ybplugins/Lots.yml".format(self.working_path), "r", encoding='utf-8') as Lot:
                    Texts = Lot.readlines()
                    Reply += "今天的解签如下:\n{}".format(Texts[Line*3-1])
        else:
            Reply += "今天还没有抽签呢\n发送【抽签】来抽签".format(UID)
        return Reply


    def ReGetSign(self, UID, Date, BotOwner):
        #重新抽签方法(仅机器人所有者使用)
        if UID in BotOwner:
            LotsDB = "{}/LotsDB/{}".format(self.path,UID)
            with open("{}/{}".format(LotsDB,Date), "w", encoding='utf-8') as Num:
                Num.write(str(random.randint(1,364)))
            Reply = "[CQ:at,qq={}]您今天抽到的签是:".format(UID)
            with open("{}/{}".format(LotsDB,Date), "r", encoding='utf-8') as Num:
                Line = int(Num.read())
                with open("{}/ybplugins/Lots.yml".format(self.working_path), "r", encoding='utf-8') as Lot:
                    Texts = Lot.readlines()
                    Reply += "\n\n{}{}".format(Texts[Line*3-3], Texts[Line*3-2])
            Reply += "\n发送【解签】解读签文"
        else:
            Reply = "[CQ:image,file={}]".format(os.path.join(self.images_foler, "请不要这样.jpg"))
        return Reply


    async def Lot(self, UID, GID, BotOwner, Role, BotRole, MsgID):
        #抽奖方法(3%概率口一小时,97%概率口1~10分钟)
        #由于mirai版本不同,权限(Role,BotRole)字段可能为admin或administrator,故用startwith统一判定
        if UID in BotOwner:
            Reply = "[CQ:image,file={}]".format(os.path.join(self.images_foler, "请不要这样.jpg"))
            return Reply
        if BotRole == "owner" or ( BotRole.startswith("admin") and Role == "member" ):
            RandomTime = random.randint(1,10)*60
            if random.randint(1,100) >= 98:
                RandomTime = 3600
                Reply = "恭喜[CQ:at,qq={}]成为天弃之子".format(UID)
                await self.api.send_group_msg(
                    group_id=GID,
                    message=Reply,
                )
            await self.api.set_group_ban(
                group_id=GID,
                user_id=UID,
                duration=RandomTime
            )
            try:
                #消息撤回的API用不了(https://github.com/yyuueexxiinngg/cqhttp-mirai/issues/55)
                await self.api.delete_msg(
                    message_id=MsgID
                )
            except:
                pass
            Reply = "[CQ:at,qq={}]你已被随机禁言{}分钟\n[CQ:image,file={}]".format(UID, int(RandomTime/60), os.path.join(self.images_foler, "口住.jpg"))
        elif BotRole.startswith("admin") and Role.startswith("admin"):
            RandomTime = random.randint(1,10)*60
            if random.randint(1,100) >= 98:
                RandomTime = 3600
            Reply = "[CQ:at,qq={}]抽到禁言{}分钟,请到群主处领取".format(UID, int(RandomTime/60))
        else:
            Reply = "[CQ:image,file={}]".format(os.path.join(self.images_foler, "请不要这样.jpg"))
        return Reply


    async def execute_async(self, ctx: Dict[str, Any]) -> Union[None, bool, str]:
        Reply = None
        Time = time.strftime("%Y.%m.%d-%H:%M:%S",time.localtime())
        Date = time.strftime("%Y.%m.%d",time.localtime())
        BotID = ctx["self_id"]
        BotOwner = self.setting.get("super-admin", list())
        Msg = ctx["raw_message"]
        MsgID = ctx["message_id"]
        MsgType = ctx["message_type"]
        NickName = ctx["sender"]["nickname"]
        UID = ctx["sender"]["user_id"]
        GID = None
        Role = None
        BotRole = None
        if MsgType == "group":
            GID = ctx["group_id"]
            Role = ctx["sender"]["role"]
            BotInfo = await self.api.get_group_member_info(
                group_id=GID,
                user_id=BotID
            )
            BotRole=BotInfo["role"]
        #https://cqhttp.cc/docs/4.15/#/API
        #聊天记录
        if True:
            with open("History.log", "a", encoding='utf-8') as log:
                if MsgType == "private":
                    log.write("{}[UID:{}]:{}\n".format(Time,UID,Msg))
                elif MsgType == "group":
                    log.write("{}[UID:{}][GID:{}]:{}\n".format(Time,UID,GID,Msg))
                else:
                    log.write("{}[Unknow]:{}\n".format(Time,Msg))


        #[私聊/群聊]统一回复
        if Msg.startswith('shell'):
            if UID in BotOwner:
                Reply = str(os.popen("{}".format(Msg[6:])).read())
            else:
                Reply = "权限不足"
        elif Msg == "抽签":
            Reply = self.GetSign(UID, Date)
        elif Msg == "解签":
            Reply = self.GetUnSign(UID, Date)
        elif Msg == "重新抽签":
            Reply = self.ReGetSign(UID, Date, BotOwner)
        elif Msg == "菜单":
            #此方法可热更新但性能低下
            if platform.system() == "Windows":
                Reply = str(os.popen("cmd /c {}/ybplugins/Menu.bat".format(self.working_path)).read())
            else:
                Reply = str(os.popen("bash {}/ybplugins/Menu.sh".format(self.working_path)).read())
        elif Msg == "可可萝" or Msg == "妈":
            Reply = "喵喵～"
            if UID in BotOwner:
                Reply = "够修进sama～"
        #统一回复的return
        if not (Reply is None):
            if MsgType == "private":
                print("QQ:{}触发自动回复".format(UID))
            else:
                print("QQ:{}于群{}触发自动回复".format(UID, GID))
            return Reply


        if MsgType == "private":
            #私聊自动回复
            #私聊回复的另一种方法
            #await self.api.send_private_msg(
            #    user_id=UID,
            #    message=Reply
            #)
            if Msg == "我是谁" or Msg == "whoami":
                Reply = "喵喵喵？" 
                if UID in BotOwner:
                    Reply = "够修进sama～"
            else:
                return False
            print("QQ:{}触发自动回复".format(UID))
            return Reply
        elif MsgType == "group":
            #群聊自动回复
            #群聊回复的另一种方法
            #await self.api.send_group_msg(
            #    group_id=GID,
            #    message=Reply,
            #)
            #CQ码使用:
            #"[CQ:at,qq={}]".format(UID)@成员UID
            #[CQ:at,qq=all] #@全体成员
            #"[CQ:image,file={}]".format(Path) #Path是图片绝对路径
            #更多CQ码使用方法https://docs.cqp.im/manual/cqcode/
            if Msg == "群地位" or Msg == "我是谁" or Msg == "whoami":
                #默认值,找不到身份时回复
                Reply = "你是谁..?"
                if Role == 'owner':
                    Reply = "苟群主～"
                if Role.startswith("admin"):
                    Reply = "苟管理～"
                elif Role == 'member':
                    Reply = "苟群员～" 
                if UID in BotOwner:
                    Reply = "够修进sama～"
            elif Msg == "抽奖":
                Reply = await self.Lot(UID, GID, BotOwner, Role, BotRole, MsgID)
            else:
                #这里一定要返回false,不然会阻塞其他模块的TxT
                return False
            print("QQ:{}于群{}触发自动回复".format(UID,GID))
            return Reply
        else:
            #防止意外情况
            print("自动回复:找不到消息类型")
            return False
        return False
