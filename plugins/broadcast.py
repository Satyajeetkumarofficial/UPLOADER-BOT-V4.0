# (c) Debug Broadcast Handler for Koyeb Logs

import asyncio
from pyrogram import Client, filters
from plugins.config import Config
from plugins.database.database import db


@Client.on_message(filters.command('broadcast'))
async def broadcast_debug(c, m):
    print("⚡ Broadcast function started")   # यह Koyeb logs में दिखना चाहिए
    await m.reply_text("⚡ Broadcast function started")   # Telegram पर reply भी

    # ✅ Owner check
    if m.from_user.id != Config.OWNER_ID:
        await m.reply_text("❌ You are not authorized to use this command.")
        print(f"❌ Unauthorized user tried broadcast: {m.from_user.id}")
        return

    # ✅ Reply check
    if not m.reply_to_message:
        await m.reply_text("⚠️ Please reply to a message to broadcast.")
        print("⚠️ Broadcast failed: no reply message")
        return

    # ✅ Database test
    try:
        all_users = []
        async for user in db.get_all_users():   # Motor cursor पर async for
            all_users.append(user)

        total = len(all_users)
        print(f"✅ Total users fetched: {total}")
        await m.reply_text(f"✅ Total users fetched: {total}")

        # ✅ सिर्फ test: पहले user का ID दिखाओ
        if all_users:
            first_user_id = all_users[0]['id']
            print(f"👤 First user in DB: {first_user_id}")
            await m.reply_text(f"👤 First user in DB: {first_user_id}")

    except Exception as e:
        print(f"⚠️ Error fetching users: {e}")
        await m.reply_text(f"⚠️ Error fetching users: {e}")
