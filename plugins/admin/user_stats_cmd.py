from pyrogram import Client, filters
from plugins.database.user_stats_db import get_user_stats, get_all_stats

# ✅ /mystatus
@Client.on_message(filters.command("mystatus"))
async def my_status(client, message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    if not stats:
        return await message.reply_text("❌ Aapke liye koi data nahi mila.")
    
    text = (
        f"📊 **Aapka Daily Status**\n\n"
        f"⬆ Uploaded: {stats.get('uploaded_gb',0)} GB\n"
        f"⬇ Downloaded: {stats.get('downloaded_gb',0)} GB\n"
        f"✅ Successful Uploads: {stats.get('success_count',0)}"
    )
    await message.reply_text(text)

# ✅ /userstatus (admin only)
@Client.on_message(filters.command("userstatus"))
async def user_status(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠ Usage: `/userstatus user_id`", quote=True)

    user_id = int(message.command[1])
    stats = await get_user_stats(user_id)
    if not stats:
        return await message.reply_text("❌ User ke liye data nahi mila.")

    text = (
        f"📊 **User {user_id} ka Daily Status**\n\n"
        f"⬆ Uploaded: {stats.get('uploaded_gb',0)} GB\n"
        f"⬇ Downloaded: {stats.get('downloaded_gb',0)} GB\n"
        f"✅ Successful Uploads: {stats.get('success_count',0)}"
    )
    await message.reply_text(text)

# ✅ /allstatus (admin only)
@Client.on_message(filters.command("allstatus"))
async def all_status(client, message):
    cursor = await get_all_stats()
    top_upload = {"user_id": None, "uploaded_gb": 0}
    top_download = {"user_id": None, "downloaded_gb": 0}

    text = "📊 **Sabhi Users ka Daily Status**\n\n"
    async for stats in cursor:
        text += (
            f"👤 User {stats['user_id']}\n"
            f"⬆ {stats.get('uploaded_gb',0)} GB | "
            f"⬇ {stats.get('downloaded_gb',0)} GB | "
            f"✅ {stats.get('success_count',0)} Uploads\n\n"
        )

        if stats.get("uploaded_gb",0) > top_upload["uploaded_gb"]:
            top_upload = {"user_id": stats["user_id"], "uploaded_gb": stats["uploaded_gb"]}
        if stats.get("downloaded_gb",0) > top_download["downloaded_gb"]:
            top_download = {"user_id": stats["user_id"], "downloaded_gb": stats["downloaded_gb"]}

    text += f"🏆 **Top Upload User:** {top_upload['user_id']} ({top_upload['uploaded_gb']} GB)\n"
    text += f"🏆 **Top Download User:** {top_download['user_id']} ({top_download['downloaded_gb']} GB)\n"

    await message.reply_text(text)
