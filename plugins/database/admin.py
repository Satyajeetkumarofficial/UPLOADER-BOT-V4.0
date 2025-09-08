import shutil
import psutil
from pyrogram import filters
from pyrogram.types import (
    Message
)
from plugins.config import Config
from pyrogram import Client, enums
from plugins.database.database import db
from plugins.functions.display_progress import humanbytes
from pyrogram import Client

# Total users
@Client.on_message(filters.private & filters.command('total'))
async def sts(c, m):
    if m.from_user.id != Config.OWNER_ID:
        return 
    total_users = await db.total_users_count()
    await m.reply_text(text=f"<b>Total users:</b> {total_users}", quote=True)

# Bot status
@Client.on_message(filters.command('status') & filters.user(Config.OWNER_ID))
async def status_handler(_, m: Message):
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    total_users = await db.total_users_count()
    await m.reply_text(
        text=f"**Total Disk Space:** {total} \n"
             f"**Used Space:** {used}({disk_usage}%) \n"
             f"**Free Space:** {free} \n"
             f"**CPU Usage:** {cpu_usage}% \n"
             f"**RAM Usage:** {ram_usage}%\n\n"
             f"**Total Users in DB:** `{total_users}`",
        quote=True
    )

# Ban Command
@Client.on_message(filters.command("ban") & filters.user(Config.OWNER_ID))
async def ban_command(bot: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("कृपया पहले यूजर का मैसेज reply करें जिसे आप ban करना चाहते हैं।")
        return
    user_id = message.reply_to_message.from_user.id
    ban_user(user_id)
    await message.reply_text(f"✅ User {user_id} को ban कर दिया गया।")

# Unban Command
@Client.on_message(filters.command("unban") & filters.user(Config.OWNER_ID))
async def unban_command(bot: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("कृपया पहले यूजर का मैसेज reply करें जिसे आप unban करना चाहते हैं।")
        return
    user_id = message.reply_to_message.from_user.id
    unban_user(user_id)
    await message.reply_text(f"✅ User {user_id} को unban कर दिया गया।")

# Check ban status (optional)
@Client.on_message(filters.command("isbanned") & filters.user(Config.OWNER_ID))
async def check_ban(bot: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("कृपया यूजर के मैसेज को reply करें।")
        return
    user_id = message.reply_to_message.from_user.id
    if is_banned(user_id):
        await message.reply_text(f"🚫 User {user_id} अभी banned है।")
    else:
        await message.reply_text(f"✅ User {user_id} banned नहीं है।")
