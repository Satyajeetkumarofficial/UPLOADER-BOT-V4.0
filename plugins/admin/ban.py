# plugins/admin/ban.py

from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.config import Config
from plugins.database.database import db


# 🔒 Ban Command
@Client.on_message(filters.command("ban") & filters.user(Config.OWNER_ID))
async def ban_command(client: Client, message: Message):
    if len(message.command) == 2:  
        # ✅ /ban <user_id>
        try:
            user_id = int(message.command[1])
            if await db.is_banned(user_id):
                await message.reply_text(f"⚠️ User `{user_id}` पहले से banned है।")
            else:
                await db.add_banned_user(user_id)
                await message.reply_text(f"🚫 User `{user_id}` को सफलतापूर्वक ban कर दिया गया।")
        except ValueError:
            await message.reply_text("❌ सही User ID दो। Example: `/ban 123456789`")
    elif message.reply_to_message:
        # ✅ /ban (reply to user)
        user_id = message.reply_to_message.from_user.id
        if await db.is_banned(user_id):
            await message.reply_text(f"⚠️ User `{user_id}` पहले से banned है।")
        else:
            await db.add_banned_user(user_id)
            await message.reply_text(f"🚫 User `{user_id}` को सफलतापूर्वक ban कर दिया गया।")
    else:
        await message.reply_text("❌ Usage:\n`/ban <user_id>`\nया फिर किसी message को reply करो।")


# 🔓 Unban Command
@Client.on_message(filters.command("unban") & filters.user(Config.OWNER_ID))
async def unban_command(client: Client, message: Message):
    if len(message.command) == 2:
        # ✅ /unban <user_id>
        try:
            user_id = int(message.command[1])
            if await db.is_banned(user_id):
                await db.remove_banned_user(user_id)
                await message.reply_text(f"✅ User `{user_id}` को unban कर दिया गया।")
            else:
                await message.reply_text(f"ℹ️ User `{user_id}` banned नहीं है।")
        except ValueError:
            await message.reply_text("❌ सही User ID दो। Example: `/unban 123456789`")
    elif message.reply_to_message:
        # ✅ /unban (reply to user)
        user_id = message.reply_to_message.from_user.id
        if await db.is_banned(user_id):
            await db.remove_banned_user(user_id)
            await message.reply_text(f"✅ User `{user_id}` को unban कर दिया गया।")
        else:
            await message.reply_text(f"ℹ️ User `{user_id}` banned नहीं है।")
    else:
        await message.reply_text("❌ Usage:\n`/unban <user_id>`\nया फिर किसी message को reply करो।")


# 📋 Banned Users List
@Client.on_message(filters.command("bannedlist") & filters.user(Config.OWNER_ID))
async def banned_list(client: Client, message: Message):
    users = await db.get_all_banned_users()
    if not users:
        await message.reply_text("✅ अभी कोई banned user नहीं है।")
    else:
        text = "🚫 **Banned Users List:**\n\n"
        text += "\n".join([f"• `{user_id}`" for user_id in users])
        await message.reply_text(text)
