from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.database.user_stats_db import get_user_stats, get_all_stats
from plugins.config import Config
from plugins.functions.display_progress import humanbytes
import os

# ----------------- /myuses -----------------
@Client.on_message(filters.command("myuses") & filters.private)
async def my_uses(client: Client, message: Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)

    if not stats:
        await message.reply_text("📊 Aaj aapka koi record nahi mila. Pehle kuch upload ya download karein.")
        return

    uploaded = stats.get("uploaded_bytes", 0)
    downloaded = stats.get("downloaded_bytes", 0)
    total_bytes = uploaded + downloaded
    total_files = stats.get("success_count", 0)

    text = (
        f"📈 **Aapka Aaj Ka Usage**\n\n"
        f"👤 User: {message.from_user.mention}\n"
        f"⬆️ Uploaded: `{humanbytes(uploaded)}`\n"
        f"⬇️ Downloaded: `{humanbytes(downloaded)}`\n"
        f"📦 Total Usage: `{humanbytes(total_bytes)}`\n"
        f"🗂 Files Uploaded: `{total_files}`"
    )

    await message.reply_text(text)


# ----------------- /totaluses -----------------
@Client.on_message(filters.command("totaluses"))
async def total_uses(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ Ye command sirf bot owner ke liye hai.")
        return

    cursor = await get_all_stats()
    stats_list = await cursor.to_list(length=None)

    if not stats_list:
        await message.reply_text("📊 Aaj ke liye koi usage record nahi mila.")
        return

    total_uploaded = sum(s.get("uploaded_bytes", 0) for s in stats_list)
    total_downloaded = sum(s.get("downloaded_bytes", 0) for s in stats_list)
    total_files = sum(s.get("success_count", 0) for s in stats_list)
    total_bytes = total_uploaded + total_downloaded

    sorted_users = sorted(
        stats_list,
        key=lambda x: (x.get("uploaded_bytes", 0) + x.get("downloaded_bytes", 0)),
        reverse=True
    )
    top3 = sorted_users[:3]

    text = (
        f"📊 **All Users (Today) — Summary**\n\n"
        f"📤 **Total Uploaded:** `{humanbytes(total_uploaded)}`\n"
        f"📥 **Total Downloaded:** `{humanbytes(total_downloaded)}`\n"
        f"📦 **Total Combined:** `{humanbytes(total_bytes)}`\n"
        f"🗂 **Total Files Uploaded:** `{total_files}`\n\n"
        f"🏆 **Top 3 Users (by total usage)**"
    )

    if not top3:
        text += "\n\n(Top users not available)"
    else:
        for i, u in enumerate(top3, start=1):
            uid = u.get("user_id") or u.get("_id")
            uploaded = u.get("uploaded_bytes", 0)
            downloaded = u.get("downloaded_bytes", 0)
            total_user_bytes = uploaded + downloaded
            files = u.get("success_count", 0)

            text += (
                f"\n\n{i}. 👤 **User ID:** `{uid}`\n"
                f"    • **Uploaded:** {humanbytes(uploaded)} ⬆️\n"
                f"    • **Downloaded:** {humanbytes(downloaded)} ⬇️\n"
                f"    • **Total Usage:** {humanbytes(total_user_bytes)} 📦\n"
                f"    • **Files Uploaded:** {files} 🗂"
            )

    if len(text) > 4000:
        fname = f"totaluses_{message.message_id}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(text)
        await message.reply_document(fname, caption="📊 All Users Today (Summary)")
        try:
            os.remove(fname)
        except:
            pass
    else:
        await message.reply_text(text)


# ----------------- /useruses <user_id> -----------------
@Client.on_message(filters.command("useruses"))
async def check_user_cmd(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ Ye command sirf bot owner ke liye hai.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.reply_text(
            "⚠️ **Usage:**\n"
            "`/useruses <user_id>`\n\n"
            "Example:\n"
            "`/useruses 123456789`"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ Invalid user_id. Sirf numeric Telegram ID dijiye.")
        return

    stats = await get_user_stats(user_id)
    if not stats:
        await message.reply_text(f"❌ Aaj ke liye user `{user_id}` ka koi record nahi mila.")
        return

    uploaded = stats.get("uploaded_bytes", 0)
    downloaded = stats.get("downloaded_bytes", 0)
    total = uploaded + downloaded
    files = stats.get("success_count", 0)

    text = (
        f"📊 **Stats for** `{user_id}` (Today)\n\n"
        f"⬆️ Uploaded: `{humanbytes(uploaded)}`\n"
        f"⬇️ Downloaded: `{humanbytes(downloaded)}`\n"
        f"📦 Total Usage: `{humanbytes(total)}`\n"
        f"🗂 Files Uploaded: `{files}`"
    )
    await message.reply_text(text)
