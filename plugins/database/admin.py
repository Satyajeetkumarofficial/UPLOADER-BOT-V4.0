import shutil
import psutil
from pyrogram import filters
from pyrogram.types import Message
from plugins.config import Config
from pyrogram import Client
from plugins.database.database import db
from plugins.functions.display_progress import humanbytes

@Client.on_message(filters.private & filters.command('total'))
async def sts(c, m):
    if m.from_user.id != Config.OWNER_ID:
        return 
    total_users = await db.total_users_count()
    await m.reply_text(text=f"<b>Total users:</b> {total_users}", quote=True)


@Client.on_message(filters.command('status') & filters.user(Config.OWNER_ID))
async def status_handler(_, m: Message):
    # ---------------- Original Server Stats ----------------
    total, used, free = shutil.disk_usage(".")
    total_str = humanbytes(total)
    used_str = humanbytes(used)
    free_str = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    total_users = await db.total_users_count()

    # ---------------- MongoDB Storage Info ----------------
    db_stats = await db.db.command("dbstats")
    mongo_data_size = humanbytes(db_stats.get("dataSize", 0))        # Actual data size
    mongo_storage_size = humanbytes(db_stats.get("storageSize", 0))  # Allocated storage

    # ---------------- Build Message ----------------
    text = (
        f"**Total Disk Space:** {total_str} \n"
        f"**Used Space:** {used_str}({disk_usage}%) \n"
        f"**Free Space:** {free_str} \n"
        f"**CPU Usage:** {cpu_usage}% \n"
        f"**RAM Usage:** {ram_usage}%\n\n"
        f"**Total Users in DB:** `{total_users}`\n\n"
        f"**MongoDB Storage:**\n"
        f"💽 Data Size: {mongo_data_size} | Storage Allocated: {mongo_storage_size}"
    )

    await m.reply_text(text, quote=True)
