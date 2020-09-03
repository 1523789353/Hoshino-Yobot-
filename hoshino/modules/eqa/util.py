# -*- coding: UTF-8 -*-
from sqlitedict import SqliteDict
from io import BytesIO
from nonebot import *
import base64
import requests
import imghdr
import uuid
import yaml
import json
import os
import re

bot = get_bot()


# 获取配置
def get_config():
    file = open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r', encoding="utf-8")
    return yaml.load(file.read())


# 获取字符串中的关键字
def get_msg_keyword(keyword, msg, is_first=False):
    msg = msg[0] if isinstance(msg, tuple) else msg
    res = re.split(format_reg(keyword, is_first), msg, 1)
    return tuple(res[::-1]) if len(res) == 2 else False


# 格式化配置中的正则表达式
def format_reg(keyword, is_first=False):
    keyword = keyword if isinstance(keyword, list) else [keyword]
    return f"{'|'.join([f'^{i}' for i in keyword] if is_first else keyword)}"


def get_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


# 初始化数据库
def init_db(db_dir, db_name='db.sqlite'):
    return SqliteDict(get_path(db_dir, db_name),
                      encode=json.dumps,
                      decode=json.loads,
                      autocommit=True)


# 寻找MessageSegment里的某个关键字的位置
def find_ms_str_index(ms, keyword, is_first=False):
    for index, item in enumerate(ms):
        if item['type'] == 'text' and re.search(format_reg(keyword, is_first), item['data']['text']):
            return index
    return -1


# 下载图片到本地 并返回message图片类型
def ms_handler_image(ms, msg_diy=False, cache_dir='', dir_name='img', b64=False):
    url = str(ms['data']['url'] if ms['data'].get('url') else ms['data']['file']).strip()
    if not url:
        return False
    if msg_diy and url[0] == '?':
        return MessageSegment.image(url[1:])
    try:
        pic = requests.get(url, timeout=30)
    except requests.exceptions.ConnectionError:
        return False
    base64_suffix = '.base64' if b64 else ''
    file_name = get_path(cache_dir, dir_name, f'{uuid.uuid1().hex}.{imghdr.what(None, pic.content)}{base64_suffix}')
    fp = open(file_name, 'wb')
    content = bytes(pic2b64(pic.content), encoding="utf8") if b64 else pic.content
    fp.write(content)
    fp.close()
    protocol = '' if b64 else 'file:///'
    return MessageSegment.image(f'{protocol}{os.path.abspath(file_name)}')


# 是否是群管理员
def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def filter_list(plist, func):
    return list(filter(func, plist))


# 获取群内的群友名字
async def get_group_member_name(group_id, user_id):
    qq_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    return qq_info['card'] or qq_info['nickname']


# 获取当前群设置的问题列表
def get_current_ans_list(ctx, ans_list):
    return filter_list(ans_list,
                       lambda x: (x[0]['group_id'] if isinstance(x, list) else x['group_id']) == ctx['group_id'])


def get_all_ans_list_by_qq(qq, ans_list):
    return filter_list(ans_list, lambda x: filter_list(x, lambda w: w['user_id'] == qq)
    if isinstance(x, list) else x['user_id'] == qq)


def get_qus_str_by_list(ans_list):
    return set(i[0]['qus'] for i in ans_list)


def pic2b64(pic) -> str:
    return 'base64://' + base64.b64encode(pic).decode()


def get_file_suffix(file_name: str) -> str:
    return os.path.splitext(file_name)[-1]


def message_image2base64(message):
    for index, value in enumerate(message):
        if value['type'] == 'image':
            url = value['data']['file'] or value['data']['url']
            if get_file_suffix(url) == '.base64':
                try:
                    with open(url, encoding='utf8') as f:
                        message[index] = MessageSegment.image(f.read())
                except FileNotFoundError:
                    print('设置的图片丢失。。' + url)
    return message


def delete_message_image_file(message):
    message = message if isinstance(message, list) else [message]
    for value in message:
        # 首先取出message里的图片链接
        urls = list(i['data']['file'] or i['data']['url'] for i in
                    filter_list(value['message'], lambda x: x['type'] == 'image'))
        # 如果包含file协议就删除
        urls = list(i[8:] if 'file:///' in i else i for i in urls)
        # 直接删除
        ok = list(os.remove(i) for i in urls)
