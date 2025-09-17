import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

# Memory store for user files
user_files = {}

# Timeout in seconds
THUMB_TIMEOUT = 30


@Client.on_message(filters.private & (filters.video | filters.document))
async def save_file(client: Client, message: Message):
    user_id = message.from_user.id
    file_id = message.video.file_id if message.video else message.document.file_id
    file_type = "video" if message.video else "document"

    # Save file_id temporarily
    user_files[user_id] = {"file_id": file_id, "file_type": file_type}

    await message.reply_text("📥 File saved! Now send me a thumbnail image within 30 seconds.")
    logger.info(f"📥 File saved from {user_id}: type={file_type}, file_id={file_id}")

    # Auto clear after timeout
    async def clear_file():
        await asyncio.sleep(THUMB_TIMEOUT)
        if user_id in user_files:
            del user_files[user_id]
            logger.warning(f"⌛ Timeout for {user_id}, file_id={file_id}")

    asyncio.create_task(clear_file())


@Client.on_message(filters.private & filters.photo)
async def save_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_files:
        await message.reply_text("⚠️ First send me a video/document.")
        logger.warning(f"⚠️ Thumbnail received from {user_id} but no file stored.")
        return

    file_info = user_files[user_id]
    file_id = file_info["file_id"]
    file_type = file_info["file_type"]

    # Download only thumbnail
    thumb_path = await message.download()
    logger.info(f"🖼 Thumbnail saved from {user_id}: {thumb_path}")

    try:
        if file_type == "video":
            await client.send_video(
                chat_id=user_id,
                video=file_id,
                thumb=thumb_path
            )
        else:
            await client.send_document(
                chat_id=user_id,
                document=file_id,
                thumb=thumb_path
            )

        await message.reply_text("✅ Thumbnail updated instantly!")
        logger.info(f"✅ Thumbnail applied for {user_id}, type={file_type}")
    except Exception as e:
        await message.reply_text(f"❌ Error updating thumbnail: {e}")
        logger.error(f"❌ Failed to update thumbnail for {user_id}: {e}")
    finally:
        # Cleanup
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        if user_id in user_files:
            del user_files[user_id]
