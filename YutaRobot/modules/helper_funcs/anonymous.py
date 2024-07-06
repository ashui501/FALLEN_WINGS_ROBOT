from YutaRobot import dispatcher
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler

anonymous_data = {}

def anonymous_admin_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    if not is_user_admin(update.effective_chat, update.effective_user.id):
        query.answer("You need to be an admin to do this.")
        return
    data = query.data.split("_", 1)
    query.message.delete()
    if not data[1] in anonymous_data:
        query.message.edit_text("This button is expired!")
        return
    try:
        d = anonymous_data[data[1]]
        message = d["message"]
        context.__setattr__("args", message.text.split(None)[1:])
        update.__setattr__("_effective_message", message)
        update.__setattr__("callback_query", None)
        d["func"](update, context)
        del anonymous_data[data[1]]
    except:
        context.bot.send_message(update.effective_chat.id, "Failed to authorize you!")

dispatcher.add_handler(CallbackQueryHandler(anonymous_admin_callback, pattern="anonAdmin_"))

from YutaRobot.modules.helper_funcs import chat_status
is_user_admin = chat_status.is_user_admin
