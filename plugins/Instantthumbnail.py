# plugins/Instantthumbnail.py

import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger("plugins.Instantthumbnail")

# Memory dict: user_id -> file path
USER_FILES = {}

# 📥 When user sends a video or document
@Client.on_message(filters.private & (filters.video | filters.document))
async def save_file(client: Client, message: Message):
    user_id = message.from_user.id
    file = message.video or message.document

    if not file:
        await message.reply_text("❌ Unsupported file type.")
        return

    file_path = await client.download_media(file, file_name=f"{user_id}_file")
    USER_FILES[user_id] = file_path

    logger.info(f"📥 Received file from user {user_id}, waiting for thumbnail...")
    await message.reply_text("📥 File saved!\n\n📸 Now send me a thumbnail image within 30 seconds.")


# 📸 When user sends a photo (thumbnail)
@Client.on_message(filters.private & filters.photo)
async def save_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in USER_FILES:
        await message.reply_text("❌ No file found. Please send a video/document first.")
        logger.warning(f"⚠️ Thumbnail received from {user_id} but no file stored.")
        return

    thumb_path = await client.download_media(message.photo.file_id, file_name=f"{user_id}_thumb.jpg")
    file_path = USER_FILES.pop(user_id, None)

    if not file_path:
        await message.reply_text("❌ File not found in memory.")
        return

    logger.info(f"📸 Thumbnail received from {user_id}: {thumb_path}")
    await message.reply_text("⏳ Applying new thumbnail... Please wait.")

    try:
        # 5 second delay
        await asyncio.sleep(5)

        # Send file back with thumbnail
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

        logger.info(f"✅ File sent with new thumbnail for user {user_id}")

        # Cleanup
        os.remove(file_path)
        os.remove(thumb_path)

    except Exception as e:
        logger.error(f"❌ Error applying thumbnail: {e}")
        await message.reply_text(f"❌ Failed to apply thumbnail: {e}")
