import logging
from pyrogram import Client, filters

logger = logging.getLogger("plugins.Instantthumbnail")

# Cache to hold file info temporarily
FILE_CACHE = {}

# ✅ Step 1: Catch video/document
@Client.on_message(filters.private & (filters.video | filters.document), group=-1)
async def save_file(client, message):
    user_id = message.from_user.id
    file_id = message.video.file_id if message.video else message.document.file_id
    file_type = "video" if message.video else "document"

    # Save file_id in cache
    FILE_CACHE[user_id] = {"file_id": file_id, "file_type": file_type}
    logger.info(f"📥 File saved from {user_id}: type={file_type}, file_id={file_id}")

    await message.reply_text(
        "📌 File received!\n\n"
        "Now send me a photo within 30 seconds, I’ll use it as the thumbnail."
    )


# ✅ Step 2: Catch thumbnail
@Client.on_message(filters.private & filters.photo, group=-1)
async def save_thumbnail(client, message):
    user_id = message.from_user.id

    if user_id not in FILE_CACHE:
        logger.warning(f"⚠️ Thumbnail received from {user_id} but no file stored.")
        await message.reply_text("⚠️ First send me a video/document, then a thumbnail.")
        return

    file_id = FILE_CACHE[user_id]["file_id"]
    file_type = FILE_CACHE[user_id]["file_type"]
    thumb_id = message.photo.file_id

    logger.info(
        f"✅ Thumbnail received from {user_id}: thumb_id={thumb_id}, for file_id={file_id}"
    )

    try:
        if file_type == "video":
            await message.reply_video(
                file_id,
                thumb=thumb_id,
                caption="✅ Thumbnail applied successfully!"
            )
        else:
            await message.reply_document(
                file_id,
                thumb=thumb_id,
                caption="✅ Thumbnail applied successfully!"
            )

        logger.info(f"🎉 Instant thumbnail applied for {user_id}")

    except Exception as e:
        logger.error(f"❌ Failed to send file with new thumbnail: {e}")
        await message.reply_text(f"❌ Error: {e}")

    # Clear cache
    del FILE_CACHE[user_id]
