# from typing import Dict

# from gsuid_core.message_models import Button
from gsuid_core.logger import logger
from gsuid_core.sv import SV, Bot, Event
from gsuid_core.utils.message import send_diff_msg

from ..utils.database.models import CS2Bind

# from ..utils.error_reply import get_error
from .add_ck import add_uid, add_token, add_stoken

csgo_user_bind = SV('CS2用户绑定')
csgo_add_tk = SV('CS2添加TK', area='DIRECT')
csgo_add_uids = SV('CS2添加UID', area='DIRECT')
csgo_switch_paltform = SV('CS2切换平台', area='DIRECT')


@csgo_add_tk.on_prefix(('添加TK', '添加tk'))
async def send_csgo_add_tk_msg(bot: Bot, ev: Event):
    tk = ev.text.strip()
    await bot.send(await add_token(ev, tk))


@csgo_add_tk.on_prefix(('添加SK', '添加sk'))
async def send_csgo_add_st_msg(bot: Bot, ev: Event):
    tk = ev.text.strip()
    await bot.send(await add_stoken(ev, tk))


@csgo_add_uids.on_prefix(('添加uid', '添加uid'))
async def send_csgo_add_uid_msg(bot: Bot, ev: Event):
    tk = ev.text.strip()
    await bot.send(await add_uid(ev, tk))


@csgo_user_bind.on_command(
    (
        '绑定uid',
        '绑定UID',
        '绑定',
        '切换uid',
        '切换UID',
        '删除uid',
        '删除UID',
    ),
    block=True,
)
async def send_csgo_bind_uid_msg(bot: Bot, ev: Event):
    uid = ev.text.strip()
    if "5e" in ev.text:
        uid = uid.replace("5e", "").strip()
        logger.info("[cs][5e]正在绑定uid{}".format(uid))
        await bot.logger.info('[CS2] 开始执行[绑定/解绑用户信息]')
        qid = ev.user_id
        await bot.logger.info('[CS2] [绑定/解绑]UserID: {}'.format(qid))

        if '绑定' in ev.command:
            if not uid:
                return await bot.send(
                    '该命令需要带上正确的uid!\n如果不知道, 可以使用[cs搜索5e xxx]查询uid'
                )
            # data = await CS2Bind.insert_uid(
            #     qid, ev.bot_id, uid, ev.group_id, is_digit=False
            # )
            data = await CS2Bind.update_data(
                qid, ev.bot_id, domain=uid, group_id=ev.group_id
            )
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f'[CS2][5E] 绑定UID{uid}成功！',
                    -1: f'[CS2][5E] UID{uid}的位数不正确！',
                    -2: f'[CS2][5E] UID{uid}已经绑定过了！',
                    -3: '[CS2][5E] 你输入了错误的格式!',
                },
            )
        elif '切换' in ev.command:
            retcode = await CS2Bind.switch_uid_by_game(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f'[CS2][5E] 切换UID{uid}成功！')
            else:
                return await bot.send(f'[CS2][5E] 尚未绑定该UID{uid}')
        else:
            data = await CS2Bind.delete_uid(qid, ev.bot_id, uid)
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f'[CS2][5E] 删除UID{uid}成功！',
                    -1: f'[CS2][5E] 该UID{uid}不在已绑定列表中！',
                },
            )
    else:
        logger.info("[cs][完美]正在绑定uid{}".format(uid))
        await bot.logger.info('[CS2] 开始执行[绑定/解绑用户信息]')
        qid = ev.user_id
        await bot.logger.info('[CS2] [绑定/解绑]UserID: {}'.format(qid))

        if uid and not uid.isdigit() or uid and len(uid) != 17:

            return await bot.send(
                '你输入了错误的格式!\n正确的UID是个人资料steam64位id\n可以使用[cs搜索 xxx]查询uid'
            )

        if '绑定' in ev.command:
            if not uid:
                return await bot.send(
                    '该命令需要带上正确的uid!(steam64位id)\n如果不知道, 可以使用[cs搜索 xxx]查询uid'
                )
            data = await CS2Bind.insert_uid(
                qid, ev.bot_id, uid, ev.group_id, is_digit=False
            )
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f'[CS2] 绑定UID{uid}成功！',
                    -1: f'[CS2] UID{uid}的位数不正确！',
                    -2: f'[CS2] UID{uid}已经绑定过了！',
                    -3: '[CS2] 你输入了错误的格式!',
                },
            )
        elif '切换' in ev.command:
            retcode = await CS2Bind.switch_uid_by_game(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f'[CS2] 切换UID{uid}成功！')
            else:
                return await bot.send(f'[CS2] 尚未绑定该UID{uid}')
        else:
            data = await CS2Bind.delete_uid(qid, ev.bot_id, uid)
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f'[CS2] 删除UID{uid}成功！',
                    -1: f'[CS2] 该UID{uid}不在已绑定列表中！',
                },
            )


@csgo_switch_paltform.on_command(
    ('切换平台',),
    block=True,
)
async def send_csgo_switch_paltform_msg(bot: Bot, ev: Event):
    paltform = ev.text.strip()
    logger.info(paltform)
    bot_id = ev.bot_id
    logger.info('[CS2] 开始执行[切换平台]')
    qid = ev.user_id
    logger.info('[CS2] [切换平台]UserID: {} - {}'.format(qid, paltform))

    if "pf" in paltform or "完美" in paltform:
        await CS2Bind.switch_paltform(qid, bot_id, "pf")
        return await bot.send('[CS2] 切换完美平台成功！')
    elif "5e" in paltform:
        await CS2Bind.switch_paltform(qid, bot_id, "5e")
        return await bot.send('[CS2] 切换5e平台成功！')
    elif "官匹" in paltform or "国服" in paltform:
        await CS2Bind.switch_paltform(qid, bot_id, "gf")
        return await bot.send('[CS2] 切换国服官匹平台成功！')
    else:
        return await bot.send('[CS2] 平台错误！')
