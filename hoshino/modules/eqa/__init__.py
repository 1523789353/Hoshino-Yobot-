# -*- coding: UTF-8 -*-
"""
作者艾琳有栖

版本 0.0.5

基于 nonebot 问答

eqa文件夹复制到nonebot的模块目录就可

然后配置启用的模块添加 'eqa'

作者是在hoshino下开发 路径为 hoshino/modules/eqa/

默认规则如下

1 非超级管理员问答分群设置和显示
2 超级管理员设置的问题为全群
3 只允许群管理或者超级管理员删除别人的问题
4 群管理不允许删除超级管理员设置的问题
5 删除回答时只删除一个 并且是最近设置的问题
6 如果是管理员或者超级管理员删除回答时直接删除最近的一个
7 只允许超级管理员清空一个问题的全部回答
8 多个回答时 将优先自己的回答 如果自己的回答多个时则随机自己的回答
9 群员可以查看别人设置的问答



例子： 设置在默认的情况下
    设置一个问题：
    大家说111回答222
    我说333回答444
    大家说@某人回答图1图2 文字  mirai一次性太多图可能会发送失败哦

    查看个人设置的问题：
    调教
    调教@某人@某人2

    删除一个问答：
    不要回答111

    清空一个问答：
    清空回答111

    显示本群所有的问答：
    全部调教
    所有调教

"""
import re
import random
from nonebot import *
from . import util

from hoshino import Service  # 如果使用hoshino的分群管理取消注释这行

#
sv = Service('eqa')  # 如果使用hoshino的分群管理取消注释这行

config = util.get_config()
db = util.init_db(config['cache_dir'])

_bot = get_bot()


@sv.on_message('group')  # 如果使用hoshino的分群管理取消注释这行 并注释下一行的 @_bot.on_message("group")
# @_bot.on_message("group") # nonebot使用这
async def eqa_main(*params):
    bot, ctx = (_bot, params[0]) if len(params) == 1 else params

    msg = str(ctx['message']).strip()

    # 处理回答所有人的问题
    keyword = util.get_msg_keyword(config['comm']['answer_all'], msg, True)
    if keyword:
        return await bot.send(ctx, await ask(ctx, keyword, False))

    # 处理回答自己的问题
    keyword = util.get_msg_keyword(config['comm']['answer_me'], msg, True)
    if keyword:
        return await bot.send(ctx, await ask(ctx, keyword, True))

    # 回复消息
    ans = await answer(ctx)
    if ans:
        return await bot.send(ctx, ans)

    # 显示设置的问题
    show_target = util.get_msg_keyword(config['comm']['show_question'], msg, True)
    if show_target:
        return await bot.send(ctx, await show_question(ctx, str(show_target[0])))

    # 显示全部设置的问题
    show_target = util.get_msg_keyword(config['comm']['show_question_list'], msg, True)
    if show_target:
        return await bot.send(ctx, await show_question(ctx, str(show_target[0]), True))

    # 删除设置的问题
    del_target = util.get_msg_keyword(config['comm']['answer_delete'], msg, True)
    if del_target:
        return await bot.send(ctx, await del_question(ctx, str(del_target[0])))

    # 清空设置的问题
    del_all = util.get_msg_keyword(config['comm']['answer_delete_all'], msg, True)
    if del_all:
        return await bot.send(ctx, await del_question(ctx, str(del_all[0]), True))


# 设置问题的函数
async def ask(ctx, keyword, is_me):
    answer_handler = config['comm']['answer_handler']
    ans, qus = util.get_msg_keyword(answer_handler, keyword)
    qus = f'{qus}'.strip()
    if not str(qus).strip():
        return '问题呢? 问题呢??'
    if not str(ans).strip():
        return '回答呢? 回答呢??'
    if re.search(r'\[CQ:image,', qus):
        return '不能图片作为问题啦'
    message = []
    _once = False
    for ms in ctx['message'][util.find_ms_str_index(ctx['message'], answer_handler):]:
        if ms['type'] == 'text':
            reg = util.get_msg_keyword(answer_handler, ms['data']['text'])
            if reg and not _once:
                _once = True
                ms = MessageSegment.text(reg[0])
        if ms['type'] == 'image':
            ms = util.ms_handler_image(ms, config['rule']['use_cq_code_image_url'], config['cache_dir'],
                                       b64=config['image_base64'])
            if not ms:
                return '图片缓存失败了啦！'
        message.append(ms)

    qus_list = db.get(qus, [])
    qus_list.append({
        'user_id': ctx['user_id'],
        'group_id': ctx['group_id'],
        'is_me': is_me,
        'qus': qus,
        'message': message
    })
    db[qus] = qus_list
    return '我学会啦 来问问我吧！'


# 回复的函数
async def answer(ctx):
    msg = str(ctx['message']).strip()
    ans_list = db.get(msg, [])
    if not ans_list:
        return False

    group_id = ctx['group_id']
    user_id = ctx['user_id']
    admins = config['admins']
    admins = admins if isinstance(admins, list) else [admins]
    super_admin_is_all_group = config['rule']['super_admin_is_all_group']
    priority_self_answer = config['rule']['priority_self_answer']
    multiple_question_random_answer = config['rule']['multiple_question_random_answer']

    # 获取到当前群的列表 判断是否来自该群 或者是否是超级管理员
    # 超级管理员设置的是否为所有群问答
    ans_list = util.filter_list(ans_list, lambda x: group_id == x['group_id'] or (
            x['user_id'] in admins) if super_admin_is_all_group else False)

    # 木有在这群
    if not ans_list:
        return ''

    # 是否优先自己的回答 是的话则选择自己的列表
    if priority_self_answer:
        self_list = util.filter_list(ans_list, lambda x: user_id == x['user_id'])
        ans_list = self_list if self_list else ans_list

    # 判断规则是否随机
    if multiple_question_random_answer:
        # 随机选个
        ans = random.choice(ans_list)
    else:
        # 否则选最后一个
        ans = ans_list[-1]

    # 判断是否是设置为自己的回复
    if ans['is_me']:
        # 如果是自己的回复 但是人不对就返回
        if ans['user_id'] != user_id:
            return ''

    # 如果使用了base64 那么需要把信息里的图片转换一下
    if config['image_base64']:
        ans['message'] = util.message_image2base64(ans['message'])

    # 最后就是把验证成功的消息返回去
    return ans['message']


# 显示问题的函数
async def show_question(ctx, target, show_all=False):
    print_all_split = config['str']['print_all_split'] or " | "

    db_list = list(db.values())
    # 获取当前群设置的问题列表
    ans_list = util.get_current_ans_list(ctx, db_list)

    if not show_all:
        # 如果只显示个人
        is_super_admin = ctx['user_id'] in config['admins']
        is_admin = util.is_group_admin(ctx) or is_super_admin

        # 如果跟了@人的对象
        target = list(int(i) for i in re.findall(r'\[CQ:at,qq=(\d+)]', target.strip()))
        is_at = bool(target)

        # 如果关了群友查询别人的选项
        if not config['rule']['member_can_show_other'] and target and not is_admin:
            return '不能看别人设置的问题啦'

        # 如果跟着@人对象 就显示@人的  没有就显示自己的
        target = target if is_at else [ctx['user_id']]
    else:
        # 显示全部
        target = [ctx['user_id']]
        is_at = False

    msg = ''
    for qq in target:
        head = ''
        priority_list = []
        if not show_all:  # 不是显示全部的话就筛选个人
            # 获取当前qq设置问题列表
            if qq in config['admins']:
                ans_list = util.get_all_ans_list_by_qq(qq, db_list)
            else:
                ans_list = util.get_all_ans_list_by_qq(qq, ans_list)

        else:
            # 这是所有人的问答
            all_list = util.filter_list(ans_list, lambda x: True in list(not i['is_me'] for i in x))
            # 这人个人问答
            priority_list = util.filter_list(ans_list, lambda x: True in list(i['is_me'] for i in x))

            ans_list = sum(list(util.get_all_ans_list_by_qq(q, db_list) for q in config['admins']), all_list)

        # 如果是多个人 那就加个名字区别一下
        if is_at:
            name = await util.get_group_member_name(ctx['group_id'], qq)
            head = f'{name} :\n'

        # 把问题都打印出来
        msg_context = "全体问答:\n" + print_all_split.join(util.get_qus_str_by_list(ans_list)) if show_all else "\n".join(
            util.get_qus_str_by_list(ans_list))

        priority_msg = ''
        if show_all:
            priority_msg = "\n个人问答:\n" + print_all_split.join(util.get_qus_str_by_list(priority_list))

        msg = "{}{}{}{}\n".format(msg, head, msg_context if ans_list else f'还没有设置过问题呢', priority_msg)
    return msg


# 删除问题的函数
async def del_question(ctx, target, clear=False):
    target = target.strip()
    ans_list = db.get(target, [])
    if not ans_list:
        return '没这个问题哦'

    is_super_admin = ctx['user_id'] in config['admins']
    is_group_admin = util.is_group_admin(ctx) if config['rule']['only_admin_can_delete'] else True
    is_admin = is_group_admin or is_super_admin

    # 如果直接清空
    if clear:
        if is_super_admin:
            util.delete_message_image_file(ans_list)
            db.pop(target)
            return '清空成功~'
        else:
            return '木有权限啦~~'

    if config['rule']['question_del_last']:
        ans_list.reverse()

    is_del_flag = False

    for index, value in enumerate(ans_list):
        # 如果不是本群就跳过  或者 是超级管理员的话 就继续删除
        if value['group_id'] != ctx['group_id'] and not (is_super_admin and value['user_id'] in config['admins']):
            continue
        # 管理员则直接删除第一个元素
        if is_admin:
            if not config['rule']['can_delete_super_admin_qa'] and \
                    value['user_id'] in config['admins'] and \
                    not is_super_admin:
                # 不允许删除超级管理员的设置
                continue
            else:
                is_del_flag = True
                util.delete_message_image_file(value)
                ans_list.pop(index)
                break
        else:
            # 如果不是管理员 就删除自己的第一个元素
            if value['user_id'] == ctx['user_id']:
                is_del_flag = True
                util.delete_message_image_file(value)
                ans_list.pop(index)
                break

    # 表示删除了元素 可以更新数据库了
    if is_del_flag:
        # 如果刚刚反转了 那要反转回来
        if config['rule']['question_del_last']:
            ans_list.reverse()
        if bool(ans_list):
            db[target] = ans_list
        else:
            db.pop(target)

    return '删除成功啦' if is_del_flag else '删除失败 可能木有权限'