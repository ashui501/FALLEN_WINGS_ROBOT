from functools import wraps
from time import time
from traceback import format_exc as err

from pyrogram import enums
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message

from YutaRobot import pbot as app
from YutaRobot import DRAGONS as SUDO


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    try:
        member = await app.get_chat_member(chat_id, user_id)
        perijinan = member.privileges
    except Exception:
        return []
    if member.status != enums.ChatMemberStatus.MEMBER:
        if perijinan.can_post_messages:
            perms.append("can_post_messages")
        if perijinan.can_edit_messages:
            perms.append("can_edit_messages")
        if perijinan.can_delete_messages:
            perms.append("can_delete_messages")
        if perijinan.can_restrict_members:
            perms.append("can_restrict_members")
        if perijinan.can_promote_members:
            perms.append("can_promote_members")
        if perijinan.can_change_info:
            perms.append("can_change_info")
        if perijinan.can_invite_users:
            perms.append("can_invite_users")
        if perijinan.can_pin_messages:
            perms.append("can_pin_messages")
        if perijinan.can_manage_video_chats:
            perms.append("can_manage_video_chats")
    return perms


admins_in_chat = {}


async def list_admins(chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [member.user.id async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)],
    }
    return admins_in_chat[chat_id]["data"]


async def authorised(func, subFunc2, client, message, *args, **kwargs):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(e)
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    text = f"You don't have the required permission to perform this action.\n**Permission:** __{permission}__"
    chatID = message.chat.id
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    return subFunc2


def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if userID not in SUDO and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return subFunc
