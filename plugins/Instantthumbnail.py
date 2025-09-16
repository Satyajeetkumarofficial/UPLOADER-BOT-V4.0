import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger("plugins.Instantthumbnail")

USER_FILES = {}  # user_id -> {"file_path": str, "task": asyncio.Task}


# 📥 Catch all file messages (video/document/animation)
@Client.on_message(filters.private & (filters.video | filters.document | filters.animation))
async def save_file(client: Client, message: Message):
    user_id = message.from_user.id
    file = message.video or message.document or message.animation

    if not file:
        await message.reply_text("❌ Unsupported file type.")
        logger.warning(f"⚠️ Unsupported file from {user_id}")
        return

    file_path = await client.download_media(file, file_name=f"{user_id}_file")
    logger.info(f"📥 File saved from {user_id}: {file_path}")

    # Cancel old task if exists
    if user_id in USER_FILES and "task" in USER_FILES[user_id]:
        USER_FILES[user_id]["task"].cancel()

    # Timeout task
    task = asyncio.create_task(thumbnail_timeout(client, message.chat.id, user_id))

    USER_FILES[user_id] = {"file_path": file_path, "task": task}
    await message.reply_text("📥 File saved!\n\n📸 Now send me a thumbnail image within 30 seconds.")


# 📸 Save thumbnail
@Client.on_message(filters.private & filters.photo)
async def save_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in USER_FILES:
        await message.reply_text("❌ No file found. Please send a video/document first.")
        logger.warning(f"⚠️ Thumbnail received from {user_id} but no file stored.")
        return

    thumb_path = await client.download_media(message.photo.file_id, file_name=f"{user_id}_thumb.jpg")
    file_path = USER_FILES[user_id]["file_path"]

    if "task" in USER_FILES[user_id]:
        USER_FILES[user_id]["task"].cancel()

    logger.info(f"📸 Thumbnail received from {user_id}: {thumb_path}")
    await message.reply_text("⏳ Applying new thumbnail... Please wait.")

    try:
        await asyncio.sleep(5)  # delay
        if file_path.endswith(".mp4"):
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                thumb=thumb_path,
                caption="✅ Here is your file with new thumbnail!"
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                thumb=thumb_path,
                caption="✅ Here is your file with new thumbnail!"
            )

        logger.info(f"✅ File sent with new thumbnail for {user_id}")

    except Exception as e:
        logger.error(f"❌ Error applying thumbnail for {user_id}: {e}")
        await message.reply_text(f"❌ Failed to apply thumbnail: {e}")

    finally:
        try:
            os.remove(file_path)
            os.remove(thumb_path)
        except:
            pass
        USER_FILES.pop(user_id, None)


# ⏳ Timeout
async def thumbnail_timeout(client: Client, chat_id: int, user_id: int):
    try:
        await asyncio.sleep(30)
        if user_id in USER_FILES:
            file_path = USER_FILES[user_id]["file_path"]
            await client.send_message(chat_id, "⏳ Timeout! No thumbnail received.\n❌ Please try again.")
            logger.warning(f"⌛ Timeout for {user_id}, file: {file_path}")

            try:
                os.remove(file_path)
            except:
                pass
            USER_FILES.pop(user_id, None)
    except asyncio.CancelledError:
        logger.info(f"✅ Timeout cancelled for {user_id} (thumbnail received)")
