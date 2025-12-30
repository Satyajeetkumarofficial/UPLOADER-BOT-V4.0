import asyncio
from plugins.config import Config
from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    UserNotParticipant,
    ChatAdminRequired,
    PeerIdInvalid,
    ChannelInvalid
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


async def handle_force_subscribe(bot: Client, message):

    if not Config.UPDATES_CHANNEL:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Updates channel not configured.\nPlease contact the admin.",
            disable_web_page_preview=True
        )
        return 400

    try:
        user = await bot.get_chat_member(
            int(Config.UPDATES_CHANNEL),
            message.from_user.id
        )

        # 🚫 Banned user
        if user.status == "kicked":
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Sorry, you are banned from using this bot.",
                disable_web_page_preview=True
            )
            return 400

        return True  # ✅ User joined

    except UserNotParticipant:
        invite_link = await get_invite_link(bot)

        if not invite_link:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Unable to generate invite link.\nPlease try again later.",
                disable_web_page_preview=True
            )
            return 400

        await bot.send_message(
            chat_id=message.from_user.id,
            text="Please join the Updates Channel to use this bot!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Join Channel",
                            url=invite_link
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Refresh",
                            callback_data="refreshForceSub"
                        )
                    ]
                ]
            ),
            disable_web_page_preview=True
        )
        return 400

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return 400

    except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ValueError):
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Bot is not properly configured or missing access to the Updates Channel.\nPlease contact the admin!",
            disable_web_page_preview=True
        )
        return 400

    except Exception:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="An unexpected error occurred.\nPlease contact support.",
            disable_web_page_preview=True
        )
        return 400
