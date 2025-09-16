from pyrogram import Client, filters
from pyrogram.types import Message
import os

# Temporary save folder
THUMB_DIR = "thumbnails"
if not os.path.exists(THUMB_DIR):
    os.makedirs(THUMB_DIR)

# Store last video/document for each user
user_last_file = {}

# Step 1: User sends video/document
@Client.on_message(filters.private & (filters.video | filters.document))
async def ask_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id
    user_last_file[user_id] = message  # save file message
    await message.reply_text("📸 Please send a thumbnail photo for this file.")


# Step 2: User sends thumbnail (photo)
@Client.on_message(filters.private & filters.photo)
async def set_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_last_file:
        await message.reply_text("⚠️ First send a video/document.")
        return

    # Save thumbnail
    thumb_path = os.path.join(THUMB_DIR, f"{user_id}.jpg")
    await message.download(file_name=thumb_path)

    file_msg = user_last_file[user_id]

    # ✅ Re-send video/document with new thumbnail
    if file_msg.video:
        await client.send_video(
            chat_id=user_id,
            video=file_msg.video.file_id,
            thumb=thumb_path,
            caption=file_msg.caption or "🎬 Your file with custom thumbnail",
        )
    elif file_msg.document:
        await client.send_document(
            chat_id=user_id,
            document=file_msg.document.file_id,
            thumb=thumb_path,
            caption=file_msg.caption or "📂 Your file with custom thumbnail",
        )

    await message.reply_text("✅ Thumbnail applied successfully!")
    # Optionally delete saved thumb
    os.remove(thumb_path)
    del user_last_file[user_id]
