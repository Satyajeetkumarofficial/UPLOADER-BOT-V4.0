import logging
import os
from pyrogram import Client, filters

logger = logging.getLogger("plugins.Instantthumbnail")

FILE_CACHE = {}
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


# ✅ Step 1: Catch video/document
@Client.on_message(filters.private & (filters.video | filters.document), group=-1)
async def save_file(client, message):
    user_id = message.from_user.id

    if message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mp4"
        file_type = "video"
    else:
        file_id = message.document.file_id
        file_name = message.document.file_name or "file.bin"
        file_type = "document"

    FILE_CACHE[user_id] = {
        "file_id": file_id,
        "file_type": file_type,
        "file_name": file_name,
    }

    logger.info(f"📥 File saved from {user_id}: type={file_type}, name={file_name}, file_id={file_id}")

    await message.reply_text(
        f"📌 File received: <b>{file_name}</b>\n\n"
        "Now send me a photo, I’ll use it as the thumbnail.",
        quote=True
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
    file_name = FILE_CACHE[user_id]["file_name"]

    # Download thumbnail (photo) locally
    thumb_path = os.path.join(DOWNLOAD_DIR, f"{user_id}_thumb.jpg")
    await message.download(file_name=thumb_path)

    logger.info(f"✅ Thumbnail downloaded for {user_id}: {thumb_path}")

    try:
        if file_type == "video":
            await message.reply_video(
                file_id,
                thumb=thumb_path,
                file_name=file_name,  # ✅ Preserve original filename
                caption=f"✅ Thumbnail applied successfully!\n📂 <b>{file_name}</b>"
            )
        else:
            await message.reply_document(
                file_id,
                thumb=thumb_path,
                file_name=file_name,  # ✅ Preserve original filename
                caption=f"✅ Thumbnail applied successfully!\n📂 <b>{file_name}</b>"
            )

        logger.info(f"🎉 Instant thumbnail applied for {user_id}, file={file_name}")

    except Exception as e:
        logger.error(f"❌ Failed to send file with new thumbnail: {e}")
        await message.reply_text(f"❌ Error: {e}")

    # Cleanup
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
    del FILE_CACHE[user_id]
