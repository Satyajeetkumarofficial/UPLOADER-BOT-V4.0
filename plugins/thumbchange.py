from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.database.database import db

# 🔹 When user sends a video or document → ask thumbnail choice
@Client.on_message(filters.video | filters.document)
async def ask_for_thumb(client, message):
    user_thumb = await db.get_thumbnail(message.from_user.id)

    if user_thumb:
        await message.reply_text(
            "📸 Choose thumbnail option:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Use Saved Thumbnail", callback_data=f"use_default_thumb")],
                [InlineKeyboardButton("📸 Send New Thumbnail", callback_data=f"send_new_thumb")]
            ])
        )
    else:
        await message.reply_text(
            "😐 You don’t have a saved thumbnail.\n\n📸 Please send me a new one (use `/showthumb` or `/delthumb` from thumbnail menu)."
        )


# ✅ Use Saved Thumbnail
@Client.on_callback_query(filters.regex("^use_default_thumb$"))
async def use_default_thumb(client, query):
    user_thumb = await db.get_thumbnail(query.from_user.id)

    if not user_thumb:
        await query.message.edit("❌ No thumbnail saved. Please set one first using `/showthumb` command.")
        return

    await query.message.edit(
        "✅ Your saved thumbnail will be applied.\n\n"
        "👉 Next time when file/video is sent, it will use this thumbnail automatically."
    )


# 📸 Ask for New Thumbnail (redirect to thumbnail.py handler)
@Client.on_callback_query(filters.regex("^send_new_thumb$"))
async def ask_new_thumb(client, query):
    await query.message.edit(
        "📸 Please send me a photo to use as your thumbnail.\n\n"
        "👉 This will be handled by the thumbnail system."
    )
    # ⚡ No saving here → thumbnail.py ka save handler automatically kaam karega
