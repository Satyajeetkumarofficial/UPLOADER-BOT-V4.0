from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.database.user_stats_db import get_user_stats, get_all_stats
from plugins.config import Config
from plugins.functions.display_progress import humanbytes

# ----------------- /myuses -----------------
@Client.on_message(filters.command("myuses") & filters.private)
async def my_uses(client: Client, message: Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)

    if not stats:
        await message.reply_text("📊 Aaj aapka koi record nahi mila. Pehle kuch upload karen.")
        return

    uploaded_gb = stats.get("uploaded_gb", 0)
    downloaded_gb = stats.get("downloaded_gb", 0)
    total_bytes = int((uploaded_gb + downloaded_gb) * (1024**3))
    total_files = stats.get("success_count", 0)

    text = (
        f"📈 **Aapka Aaj Ka Usage**\n\n"
        f"👤 User: {message.from_user.mention}\n"
        f"⬆️ Uploaded: `{humanbytes(int(uploaded_gb * (1024**3)))}`\n"
        f"⬇️ Downloaded: `{humanbytes(int(downloaded_gb * (1024**3)))}`\n"
        f"📦 Total Usage: `{humanbytes(total_bytes)}`\n"
        f"🗂 Files Uploaded: `{total_files}`"
    )

    await message.reply_text(text)


# ----------------- /totaluses -----------------
@Client.on_message(filters.command("totaluses"))
async def total_uses(client: Client, message):
    # Admin-only restriction
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text(
            "❌ This command is restricted to the bot admin."
        )
        return

    # Fetch all user stats
    cursor = await get_all_stats()
    stats_list = await cursor.to_list(length=None)

    if not stats_list:
        await message.reply_text(
            "📊 No usage records found for today.\n"
            "Users have not performed any actions yet."
        )
        return

    # Calculate totals
    total_uploaded_gb = sum(s.get("uploaded_gb", 0) for s in stats_list)
    total_downloaded_gb = sum(s.get("downloaded_gb", 0) for s in stats_list)
    total_files = sum(s.get("success_count", 0) for s in stats_list)
    total_bytes = int((total_uploaded_gb + total_downloaded_gb) * (1024**3))

    # Top 3 users by total usage
    sorted_users = sorted(
        stats_list,
        key=lambda x: (x.get("uploaded_gb", 0) + x.get("downloaded_gb", 0)),
        reverse=True
    )
    top3 = sorted_users[:3]

    # Build message text
    text = (
        f"📊 **All Users (Today) — Summary**\n\n"
        f"📤 **Total Uploaded:** `{humanbytes(int(total_uploaded_gb * (1024**3)))}`\n"
        f"📥 **Total Downloaded:** `{humanbytes(int(total_downloaded_gb * (1024**3)))}`\n"
        f"📦 **Total Combined:** `{humanbytes(total_bytes)}`\n"
        f"🗂 **Total Files Uploaded:** `{total_files}`\n\n"
        f"🏆 **Top 3 Users (by total usage)**"
    )

    if not top3:
        text += "\n\n(Top users not available)"
    else:
        for i, u in enumerate(top3, start=1):
            uid = u.get("user_id") or u.get("_id")
            uploaded = int(u.get("uploaded_gb", 0) * (1024**3))
            downloaded = int(u.get("downloaded_gb", 0) * (1024**3))
            total_user_bytes = uploaded + downloaded
            files = u.get("success_count", 0)

            text += (
                f"\n\n{i}. 👤 **User ID:** `{uid}`\n"
                f"    • **Uploaded:** {humanbytes(uploaded)} ⬆️\n"
                f"    • **Downloaded:** {humanbytes(downloaded)} ⬇️\n"
                f"    • **Total Usage:** {humanbytes(total_user_bytes)} 📦\n"
                f"    • **Files Uploaded:** {files} 🗂"
            )

    # Send as file if message too long
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
    # Check if user is owner/admin
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ This command is restricted to the bot admin.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.reply_text(
            "⚠️ **Command Usage:**\n"
            "`/useruses <user_id>`\n\n"
            "Example:\n"
            "`/useruses 123456789`\n\n"
            "_Use this command to fetch today's usage statistics of a specific user by their numeric Telegram ID._"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ Invalid user_id. Please provide a numeric Telegram user ID.")
        return

    stats = await get_user_stats(user_id)
    if not stats:
        await message.reply_text(f"❌ No stats found for user `{user_id}` today.")
        return

    uploaded = int(stats.get("uploaded_gb", 0) * (1024**3))
    downloaded = int(stats.get("downloaded_gb", 0) * (1024**3))
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
