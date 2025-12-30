import os
import asyncio
import logging

from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait

from plugins.config import Config
from plugins.database.database import db
from plugins.settings.settings import OpenSettings
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes
from plugins.dl_button import ddl_call_back
from plugins.button import youtube_dl_call_back
from plugins.script import Translation

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ───────── Invite Link Cache ─────────
INVITE_LINK_CACHE = None


async def get_invite_link(bot: Client):
    global INVITE_LINK_CACHE

    if INVITE_LINK_CACHE:
        return INVITE_LINK_CACHE

    try:
        link = await bot.create_chat_invite_link(
            int(Config.UPDATES_CHANNEL),
            creates_join_request=False
        )
        INVITE_LINK_CACHE = link.invite_link
        return INVITE_LINK_CACHE

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return None


@Client.on_callback_query()
async def button(bot: Client, update):

    if update.data == "home":
        await update.message.edit(
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
        )

    elif update.data == "help":
        await update.message.edit(
            text=Translation.HELP_TEXT,
            reply_markup=Translation.HELP_BUTTONS,
        )

    elif update.data == "about":
        await update.message.edit(
            text=Translation.ABOUT_TEXT,
            reply_markup=Translation.ABOUT_BUTTONS,
        )

    # ───────── FORCE SUB REFRESH ─────────
    elif update.data == "refreshForceSub":

        if not Config.UPDATES_CHANNEL:
            await update.answer("Updates channel not configured", show_alert=True)
            return

        channel_id = int(Config.UPDATES_CHANNEL)

        try:
            user = await bot.get_chat_member(channel_id, update.from_user.id)

            if user.status == "kicked":
                await update.message.edit(
                    text="🚫 Sorry, you are banned.\nContact @SatyajeetKumarOfficial",
                    disable_web_page_preview=True
                )
                return

        except UserNotParticipant:
            invite_link = await get_invite_link(bot)

            if not invite_link:
                await update.answer("Unable to generate invite link", show_alert=True)
                return

            await update.message.edit(
                text="**I like your smartness, but don’t be oversmart 😑**\n\n"
                     "🔒 Please join the Updates Channel first!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🤖 Join Updates Channel",
                                url=invite_link
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔄 Refresh 🔄",
                                callback_data="refreshForceSub"
                            )
                        ]
                    ]
                ),
                disable_web_page_preview=True
            )
            return

        except Exception:
            await update.message.edit(
                text="⚠️ Something went wrong.\nContact @SatyajeetKumarOfficial",
                disable_web_page_preview=True
            )
            return

        # ✅ User joined → show home
        await update.message.edit(
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
        )

    # ───────── SETTINGS ─────────
    elif update.data == "OpenSettings":
        await update.answer()
        await OpenSettings(update.message)

    elif update.data == "showThumbnail":
        thumbnail = await db.get_thumbnail(update.from_user.id)
        if not thumbnail:
            await update.answer("You didn't set any custom thumbnail!", show_alert=True)
        else:
            await update.answer()
            await bot.send_photo(
                update.message.chat.id,
                thumbnail,
                "Custom Thumbnail",
                reply_markup=types.InlineKeyboardMarkup(
                    [[types.InlineKeyboardButton("Delete Thumbnail", callback_data="deleteThumbnail")]]
                )
            )

    elif update.data == "deleteThumbnail":
        await db.set_thumbnail(update.from_user.id, None)
        await update.answer(
            "Custom thumbnail deleted. Default will be used now.",
            show_alert=True
        )
        await update.message.delete(True)

    elif update.data == "setThumbnail":
        await update.message.edit(
            text=Translation.TEXT,
            reply_markup=Translation.BUTTONS,
            disable_web_page_preview=True
        )

    elif update.data == "triggerGenSS":
        await update.answer()
        value = await db.get_generate_ss(update.from_user.id)
        await db.set_generate_ss(update.from_user.id, not value)
        await OpenSettings(update.message)

    elif update.data == "triggerGenSample":
        await update.answer()
        value = await db.get_generate_sample_video(update.from_user.id)
        await db.set_generate_sample_video(update.from_user.id, not value)
        await OpenSettings(update.message)

    elif update.data == "triggerUploadMode":
        await update.answer()
        value = await db.get_upload_as_doc(update.from_user.id)
        await db.set_upload_as_doc(update.from_user.id, not value)
        await OpenSettings(update.message)

    elif "close" in update.data:
        await update.message.delete(True)

    elif "|" in update.data:
        await youtube_dl_call_back(bot, update)

    elif "=" in update.data:
        await ddl_call_back(bot, update)

    else:
        await update.message.delete()
