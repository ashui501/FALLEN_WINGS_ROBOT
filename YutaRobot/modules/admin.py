import html
import requests
from telegram import ParseMode, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, \
    Filters, run_async, MessageHandler
from telegram.utils.helpers import mention_html

from YutaRobot import DRAGONS, dispatcher, TOKEN, LOGGER
from YutaRobot.modules.disable import DisableAbleCommandHandler
from YutaRobot.modules.sql import pin_sql
from YutaRobot.pyrogramee.pluginshelper import member_permissions
from YutaRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    is_user_admin,
    ADMIN_CACHE,
    user_can_promote,
    bot_can_change_info,
    user_can_change_info,
)
from YutaRobot.modules.helper_funcs.admin_perms import can_manage_voice_chats
from YutaRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from YutaRobot.modules.log_channel import loggable
from YutaRobot.modules.helper_funcs.alternate import send_message


@connection_status
@bot_admin
@can_promote
@user_admin
@user_can_promote
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "administrator" or user_member.status == "creator":
        message.reply_text("How am I meant to promote someone that's already an admin?")
        return

    if user_id == bot.id:
        message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)
    #can_promote_members = False
    #if "all" in permissions and bot_member.can_promote_members:
    #    can_promote_members = True

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            #can_promote_members=False,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            #can_manage_voice_chats=bot_member.can_manage_voice_chats
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("I can't promote someone who isn't in the group.")
        else:
            message.reply_text("An error occured while promoting.")
        return

    bot.sendMessage(
        chat.id,
        f"♔ {chat.title} Event! \
        \n• A new admin has been appointed! \
        \n• Let's all welcome {mention_html(user_member.user.id, user_member.user.first_name)}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏬ Demote",
                        callback_data=f"admin_demote_{user_member.user.id}",
                    ),
                    InlineKeyboardButton(
                        text="🔄 Cache",
                        callback_data="admin_refresh",
                    ),
                ],
            ],
        ),
    )

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except:
        pass

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    if title != "":
        log_message += f"<b>Admin Title:</b> {title}"

    return log_message



@connection_status
@bot_admin
@can_promote
@user_admin
@user_can_promote
@loggable
def promoteall(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "administrator" or user_member.status == "creator":
        message.reply_text("How am I meant to promote someone that's already an admin?")
        return

    if user_id == bot.id:
        message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)
    #can_promote_members = False
    #if "all" in permissions and bot_member.can_promote_members:
    #    can_promote_members = True

    result = requests.post(f"https://api.telegram.org/bot{TOKEN}/promoteChatMember?chat_id={chat.id}&user_id={user_id}&can_change_info={bot_member.can_change_info}&can_post_messages={bot_member.can_post_messages}&can_edit_messages={bot_member.can_edit_messages}&can_delete_messages={bot_member.can_delete_messages}&can_invite_users={bot_member.can_invite_users}&can_promote_members={bot_member.can_promote_members}&can_restrict_members={bot_member.can_restrict_members}&can_pin_messages={bot_member.can_pin_messages}&can_manage_voice_chats={can_manage_voice_chats(chat.id, bot.id)}")
    status = result.json()["ok"]
    if status == False:
        message.reply_text("An error occured while promoting.")
        return

    bot.sendMessage(
        chat.id,
        f"♔ {chat.title} Event! \
        \n• A new admin has been appointed with all rights! \
        \n• Let's all welcome {mention_html(user_member.user.id, user_member.user.first_name)}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏬ Demote",
                        callback_data=f"admin_demote_{user_member.user.id}",
                    ),
                    InlineKeyboardButton(
                        text="🔄 Cache",
                        callback_data="admin_refresh",
                    ),
                ],
            ],
        ),
    )

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except:
        pass

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    if title != "":
        log_message += f"<b>Admin Title:</b> {title}"

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@user_can_promote
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text("This person CREATED the chat, how would I demote them?")
        return

    if not user_member.status == "administrator":
        message.reply_text("Can't demote what wasn't promoted!")
        return

    if user_id == bot.id:
        message.reply_text("I can't demote myself! Get an admin to do it for me.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            #can_manage_voice_chats=False
        )

        bot.sendMessage(
            chat.id,
            f"Sucessfully demoted <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )

        try:
            ADMIN_CACHE.pop(update.effective_chat.id)
        except KeyError:
            pass

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "Could not demote. I might not be admin, or the admin status was appointed by another"
            " user, so I can't act upon them!",
        )
        return

@user_admin
@user_can_promote
def promote_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    bot = context.bot

    mode = query.data.split("_")[1]
    try:
        if is_user_admin(chat, user.id):
            if mode == "demote":
                user_id = query.data.split("_")[2]
                user_member = chat.get_member(user_id)
                bot.promoteChatMember(
                    chat.id,
                    user_id,
                    can_change_info=False,
                    can_post_messages=False,
                    can_edit_messages=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    #can_manage_voice_chats=False
                )
                query.message.delete()
                bot.answer_callback_query(
                    query.id,
                    f"Sucessfully demoted {user_member.user.first_name or user_id}",
                    show_alert=True,
                )
            elif mode == "refresh":
                try:
                    ADMIN_CACHE.pop(update.effective_chat.id)
                except KeyError:
                    pass
                bot.answer_callback_query(query.id, "Admins cache refreshed!")
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in promote buttons. %s", str(query.data))


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("Admins cache refreshed!")


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "This person CREATED the chat, how can i set custom title for him?",
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me.",
        )
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text("Either they aren't promoted by me or you set a title text that is impossible to set.")
        return

    bot.sendMessage(
        chat.id,
        f"Sucessfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )

# Pin module ka part
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent,
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PINNED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    pinned_msg = bot.get_chat(chat.id).pinned_message
    if not pinned_msg:
        update.effective_message.reply_text("There is no pinned message in this chat.")
        return

    try:
        bot.unpinChatMessage(chat.id)
        update.effective_message.reply_text(f"I have unpinned [this message]({pinned_msg.link}).", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNPINNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Message:</b> {pinned_msg.link}"
    )

    return log_message


@bot_admin
@user_admin
def cleanlinked(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message
    if args:
        if len(args)!=1:
            msg.reply_text("Invalid arguments!")
            return
        param = args[0]
        if param == "on" or param == "true" or param == "yes":
            pin_sql.setCleanLinked(chat.id, True)
            msg.reply_text(f"*Enabled* linked channel post deletion in {chat.title}. Messages sent from the linked channel will be deleted.", parse_mode=ParseMode.MARKDOWN)
            return
        elif param == "off" or param == "false" or param == "no":
            pin_sql.setCleanLinked(chat.id, False)
            msg.reply_text(f"*Disabled* linked channel post deletion in {chat.title}.", parse_mode=ParseMode.MARKDOWN)
            return
        else:
            msg.reply_text("Your input was not recognised as one of: yes/no/on/off") #on or off ffs
            return
    else:
        stat = pin_sql.getCleanLinked(str(chat.id))
        if stat:
            msg.reply_text(f"Linked channel post deletion is currently *enabled* in {chat.title}. Messages sent from the linked channel will be deleted.", parse_mode=ParseMode.MARKDOWN)
            return
        else:
            msg.reply_text(f"Linked channel post deletion is currently *disabled* in {chat.title}.", parse_mode=ParseMode.MARKDOWN)
            return

@bot_admin
@can_pin
@user_admin
def antichannelpin(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message
    if args:
        if len(args)!=1:
            msg.reply_text("Invalid arguments!")
            return
        param = args[0]
        if param == "on" or param == "true" or param == "yes":
            pin_sql.setAntiChannelPin(chat.id, True)
            msg.reply_text(f"*Enabled* anti channel pins. Automatic pins from a channel will now be replaced with the previous pin.", parse_mode=ParseMode.MARKDOWN)
            return
        elif param == "off" or param == "false" or param == "no":
            pin_sql.setAntiChannelPin(chat.id, False)
            msg.reply_text(f"*Disabled* anti channel pins. Automatic pins from a channel will not be removed.", parse_mode=ParseMode.MARKDOWN)
            return
        else:
            msg.reply_text("Your input was not recognised as one of: yes/no/on/off") #on or off ffs
            return
    else:
        stat = pin_sql.getAntiChannelPin(str(chat.id))
        if stat:
            msg.reply_text(f"Anti channel pins are currently *enabled* in {chat.title}. All channel posts that get auto-pinned by telegram will be replaced with the previous pin.", parse_mode=ParseMode.MARKDOWN)
            return
        else:
            msg.reply_text(f"Anti channel pins are currently *disabled* in {chat.title}.", parse_mode=ParseMode.MARKDOWN)
            return

def sfachat(update: Update, context: CallbackContext):
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if user and user.id == 136817688:
        cleanlinked = pin_sql.getCleanLinked(str(chat.id))
        if cleanlinked:
            msg.delete()
            return ""

        antichannelpin = pin_sql.getAntiChannelPin(str(chat.id))
        if antichannelpin:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/unpinChatMessage?chat_id={chat.id}&message_id={msg.message_id}")
    return ""


@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!",
            )
    else:
        update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!",
        )

def pinned(update: Update, context: CallbackContext):
    bot = context.bot
    try:
        update.effective_message.reply_text(f"The pinned message in {update.effective_chat.title} is [here]({bot.get_chat(update.effective_chat.id).pinned_message.link}).", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except:
        update.effective_message.reply_text(f"There is no pinned message in {update.effective_chat.title}.")
        return

@bot_admin
@user_admin
def unpinall(update: Update, context: CallbackContext):
    member = update.effective_chat.get_member(update.effective_user.id)
    if member.status != "creator" and member.user.id not in DRAGONS:
        return update.effective_message.reply_text("Only group owner can do this!")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Are you sure you want to unpin all messages?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="Yes", callback_data="unpinallbtn_yes"),
            InlineKeyboardButton(text="No", callback_data="unpinallbtn_no"),
        ]]),
    )


@bot_admin
@user_admin
@loggable
def unpinallbtn(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query
    user = update.effective_user
    reply = query.data.split("_")[1]
    if reply == 'yes':
        unpinall = requests.post(f"https://api.telegram.org/bot{TOKEN}/unpinAllChatMessages?chat_id={chat.id}")
        if unpinall:
            query.message.edit_text("All pinned messages have been unpinned.")
        else:
            query.message.edit_text("Failed to unpin all messages")
            return
    else:
        query.message.edit_text("Unpin of all pinned messages has been cancelled.")
        return
    log_message = "<b>{}:</b>" \
                  "\n#UNPINNEDALL" \
                  "\n<b>Admin:</b> {}".format(
                      html.escape(chat.title),
                      mention_html(user.id, user.first_name),
                  )
    return log_message

@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat] -> unused variable
    user = update.effective_user  # type: Optional[User]
    args = context.args # -> unused variable
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "This command only works in Groups.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title # -> unused variable

    try:
        msg = update.effective_message.reply_text(
            "Fetching group admins...", parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Fetching group admins...", quote=False, parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = f"Admins in <b>{html.escape(update.effective_chat.title)}</b>:"

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id, user.full_name,
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Creator:"
            text += f"\n<code> • </code>{name}\n"

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🔱 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id, user.full_name,
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += f"\n<code> • </code>{admin}"

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0], html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += f"\n🚨 <code>{admin_group}</code>"
        for admin in value:
            text += f"\n<code> • </code>{admin}"
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return

@connection_status
@bot_admin
@bot_can_change_info
@user_admin
@user_can_change_info
@loggable
def gtitle(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        message.reply_text("Cool empty title")
        return
    new_title = " ".join(args)
    bot.set_chat_title(chat.id, new_title)

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#GTITLE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>New Title:</b> {html.escape(new_title)}"
    )


__help__ = """
*Admin commands:*
✥ *Pins:*
 • `/pin`: silently pins the message replied to - add `'loud'` or `'notify'` to give notifs to users
 • `/unpin`: unpins the currently pinned message
 • `/pinned`: to get the current pinned message
 • `/unpinall`: to unpin all messages in the chat
 • `/antichannelpin <yes/no/on/off>`: Don't let telegram auto-pin linked channels. If no arguments are given, shows current setting
 • `/cleanlinked <yes/no/on/off>`: Delete messages sent by the linked channel

✥ *Promote and Titles:*
 • `/promote`: promotes the user replied to
 • `/fullpromote`: fullpromotes the user replied to
 • `/demote`: demotes the user replied to
 • `/title <title here>`: sets a custom title for an admin that the bot promoted
 • `/admincache`: force refresh the admins list

✥ *Others:*
 • `/invitelink`: gets invitelink
 • `/gtitle <new title>`: sets chat title

*Moderation:*
✥ *Banning and Kicks:*
 • `/ban <userhandle>`: bans a user (via handle, or reply)
 • `/sban <userhandle>`: Silently ban a user then deletes command + replied to message and doesn't reply (via handle, or reply)
 • `/dban <messagereplied>`: Silently bans the user and deletes the target replied to message
 • `/tban <userhandle> x(m/h/d)`: bans a user for x time, (via handle, or reply) `m` = `minutes`, `h` = `hours`, `d` = `days`
 • `/unban <userhandle>`: unbans a user (via handle, or reply)
 • `/punch or kick or headshot <userhandle>`: Punches a user out of the group (via handle, or reply)

✥ *Muting:*
 • `/mute <userhandle>`: silences a user, Can also be used as a reply, muting the replied to user
 • `/tmute <userhandle> x(m/h/d)`: mutes a user for x time (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`
 • `/unmute <userhandle>`: unmutes a user, Can also be used as a reply, muting the replied to user

*Logging:*
 • `/logchannel`*:* get log channel info
 • `/setlog`*:* set the log channel
 • `/unsetlog`*:* unset the log channel

✥ *How to setup:*
 • Add bot to channel with admin perms
 • Send `/setlog` command in the channel
 • Forward that channel message to the group you want to setup logging for, the same channel message can be forwarded to multiple groups at once as well
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist, run_async=True)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.chat_type.groups, run_async=True)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.chat_type.groups, run_async=True)
PINNED_HANDLER = CommandHandler("pinned", pinned, filters=Filters.chat_type.groups, run_async=True)
UNPINALL_HANDLER = CommandHandler("unpinall", unpinall, filters=Filters.chat_type.groups, run_async=True)
UNPINALL_BTN_HANDLER = CallbackQueryHandler(unpinallbtn, pattern=r"unpinallbtn_", run_async=True)
CLEANLINKED_HANDLER = CommandHandler("cleanlinked", cleanlinked, filters=Filters.chat_type.groups, run_async=True)
ANTICPIN_HANDLER = CommandHandler("antichannelpin", antichannelpin, filters=Filters.chat_type.groups, run_async=True)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
PROMOTEALL_HANDLER = DisableAbleCommandHandler(["promoteall", "fullpromote"], promoteall, run_async=True)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

PROMOTE_CALLBACK_HANDLER = CallbackQueryHandler(promote_button, pattern=r"admin_", run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
GTITLE_HANDLER = CommandHandler("gtitle", gtitle, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.chat_type.groups, run_async=True,
)
SFA_HANDLER = MessageHandler(Filters.all, sfachat, allow_edit=True, run_async=True)

dispatcher.add_handler(SFA_HANDLER, group=69)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(UNPINALL_HANDLER)
dispatcher.add_handler(UNPINALL_BTN_HANDLER)
dispatcher.add_handler(CLEANLINKED_HANDLER)
dispatcher.add_handler(ANTICPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(PROMOTEALL_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(PROMOTE_CALLBACK_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(GTITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "ᴀᴅᴍɪɴꜱ"
__command_list__ = [
    "adminlist",
    "admins",
    "invitelink",
    "promote",
    "demote",
    "admincache",
    "gtitle",
]
__handlers__ = [
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    GTITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
