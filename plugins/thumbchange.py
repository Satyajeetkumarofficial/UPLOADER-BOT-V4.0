from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from plugins.database.database import db

# Jab user video ya document bheje
@Client.on_message(filters.private & (filters.video | filters.document))
async def ask_thumbnail_choice(client, message):
    user_id = message.from_user.id
    saved_thumb = await db.get_thumbnail(user_id)

    if not saved_thumb:
        # Agar user ke paas thumbnail saved hi nahi hai to normal process chalo
        return

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Use Saved Thumbnail", callback_data=f"use_thumb:{message.id}")],
            [InlineKeyboardButton("📸 Send New Thumbnail", callback_data=f"new_thumb:{message.id}")]
        ]
    )

    await message.reply_text(
        "📌 Do you want to use your saved thumbnail for this file?",
        reply_markup=keyboard
    )

# Callback handler
@Client.on_callback_query(filters.regex("^(use_thumb|new_thumb)"))
async def handle_thumb_choice(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    choice, msg_id = callback.data.split(":")
    msg_id = int(msg_id)

    # Original message fetch karo
    original_msg = await client.get_messages(callback.message.chat.id, msg_id)

    if choice == "use_thumb":
        thumb = await db.get_thumbnail(user_id)
        if not thumb:
            await callback.answer("❌ You don't have any saved thumbnail.", show_alert=True)
            return

        # File dobara bhejna with thumbnail
        if original_msg.video:
            await client.send_video(
                chat_id=callback.message.chat.id,
                video=original_msg.video.file_id,
                thumb=thumb,
                caption=original_msg.caption or "🎥 Here is your file with saved thumbnail"
            )
        elif original_msg.document:
            await client.send_document(
                chat_id=callback.message.chat.id,
                document=original_msg.document.file_id,
                thumb=thumb,
                caption=original_msg.caption or "📄 Here is your file with saved thumbnail"
            )

        await callback.message.edit_text("✅ File sent with your saved thumbnail.")

    elif choice == "new_thumb":
        await callback.message.edit_text("📸 Please send me a new photo to set as your thumbnail.")
