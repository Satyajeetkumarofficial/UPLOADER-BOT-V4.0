import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ✅ Logger setup
logger = logging.getLogger("plugins.Instantthumbnail")

# Temporary storage per user
TEMP_VIDEOS = {}

# 📥 Step 1: User sends video/document
@Client.on_message(filters.private & (filters.video | filters.document))
async def ask_for_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id
    TEMP_VIDEOS[user_id] = message

    logger.info(f"📥 Received file from user {user_id}, waiting for thumbnail...")

    await message.reply_text("📸 Please send a thumbnail photo for this file.")


# 📸 Step 2: User sends thumbnail
@Client.on_message(filters.private & filters.photo)
async def apply_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in TEMP_VIDEOS:
        logger.warning(f"⚠️ Thumbnail received from {user_id} but no video/document pending.")
        await message.reply_text("❌ First send a video/document, then send a thumbnail.")
        return

    file_message = TEMP_VIDEOS.pop(user_id)
    thumb_path = f"thumb_{user_id}.jpg"

    # Download thumbnail
    try:
        await message.download(file_name=thumb_path)
        logger.info(f"✅ Thumbnail downloaded for user {user_id}: {thumb_path}")
    except Exception as e:
        logger.error(f"❌ Failed to download thumbnail for {user_id}: {e}")
        await message.reply_text("❌ Failed to download thumbnail.")
        return

    try:
        # ⏳ Small delay (simulate instant processing)
        await asyncio.sleep(5)
        logger.info(f"⏳ Applying thumbnail after 5s delay for user {user_id}")

        # Re-send video/document with thumbnail
        if file_message.video:
            await client.send_video(
                chat_id=user_id,
                video=file_message.video.file_id,
                thumb=thumb_path,
                caption="✅ Here is your video with the new thumbnail!"
            )
        elif file_message.document:
            await client.send_document(
                chat_id=user_id,
                document=file_message.document.file_id,
                thumb=thumb_path,
                caption="✅ Here is your document with the new thumbnail!"
            )

        logger.info(f"🎉 Thumbnail applied successfully for user {user_id}")

    except Exception as e:
        logger.error(f"❌ Failed to send file with thumbnail for {user_id}: {e}")
        await message.reply_text(f"❌ Error applying thumbnail: {e}")

    finally:
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            logger.info(f"🗑 Deleted temp thumbnail {thumb_path}")
