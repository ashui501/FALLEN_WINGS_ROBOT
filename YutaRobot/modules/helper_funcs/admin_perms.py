import requests
from YutaRobot import TOKEN


def can_manage_voice_chats(chat_id, user_id):
	result = requests.post(f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat_id}&user_id={user_id}")
	status = result.json()["ok"]

	if status == True:
		data = result.json()["result"]["can_manage_voice_chats"]
		return data
	return False
