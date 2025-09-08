# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | TG-SORRY


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math
from PIL import Image
from plugins.config import Config
from plugins.script import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
import os
import time
import random
from pyrogram import enums
from pyrogram import Client
from plugins.functions.verify import verify_user, check_token, check_verification, get_token
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.display_progress import humanbytes
from plugins.functions.help_uploadbot import DownLoadFile
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from plugins.functions.ran_text import random_char
from plugins.database.database import db
from plugins.database.add import AddUser
from pyrogram.types import Thumbnail
cookies_file = 'cookies.txt'



@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    # Step 1: Check banned users
    if update.from_user.id in Config.BANNED_USERS:
        await update.reply_text(
            text="🚫 आप इस बॉट का उपयोग नहीं कर सकते।",
            disable_web_page_preview=True
        )
        return  # Stop further processing

    # Step 2: Verification check
    if update.from_user.id != Config.OWNER_ID:
        if not await check_verification(bot, update.from_user.id) and Config.TRUE_OR_FALSE:
            button = [[
                InlineKeyboardButton(
                    "✓⃝ Vᴇʀɪꜰʏ ✓⃝",
                    url=await get_token(bot, update.from_user.id, f"https://telegram.me/{Config.BOT_USERNAME}?start=")
                )
            ],[
                InlineKeyboardButton(
                    "🔆 कैसे verify करें 🔆",
                    url=f"{Config.VERIFICATION}"
                )
            ]]
            await update.reply_text(
                text="<b>कृपया पहले verify करें।</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(button)
            )
            return

    # Step 3: Log channel forwarding
    if Config.LOG_CHANNEL:
        try:
            log_message = await update.forward(Config.LOG_CHANNEL)
            log_info = "Message Sender Information\n"
            log_info += "\nFirst Name: " + update.from_user.first_name
            log_info += "\nUser ID: " + str(update.from_user.id)
            log_info += "\nUsername: @" + (update.from_user.username if update.from_user.username else "")
            log_info += "\nUser Link: " + update.from_user.mention
            await log_message.reply_text(
                text=log_info,
                disable_web_page_preview=True,
                quote=True
            )
        except Exception as error:
            print(error)

    # Step 4: User validation
    if not update.from_user:
        return await update.reply_text("I don't know about you :(")

    await AddUser(bot, update)

    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    logger.info(update.from_user)
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

    # Step 5: URL Parsing
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
        elif len(url_parts) == 4:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
            youtube_dl_username = url_parts[2].strip()
            youtube_dl_password = url_parts[3].strip()
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
    else:
        for entity in update.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]

    # Step 6: Prepare yt-dlp command
    command_to_exec = [
        "yt-dlp",
        "--no-warnings",
        "--allow-dynamic-mpd",
        "--cookies", cookies_file,
        "--no-check-certificate",
        "-j",
        url
    ]

    if Config.HTTP_PROXY:
        command_to_exec.extend(["--proxy", Config.HTTP_PROXY])
    else:
        command_to_exec.extend(["--geo-bypass-country", "IN"])

    if youtube_dl_username:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password:
        command_to_exec.extend(["--password", youtube_dl_password])

    logger.info(command_to_exec)

    chk = await bot.send_message(
        chat_id=update.chat.id,
        text='ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ ⌛',
        disable_web_page_preview=True,
        reply_to_message_id=update.id,
        parse_mode=enums.ParseMode.HTML
    )

    # Step 7: Run yt-dlp subprocess
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(e_response)

    # Step 8: Handle yt-dlp errors
    if e_response and "nonnumeric port" not in e_response:
        error_message = e_response.replace(
            "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", ""
        )
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        await chk.delete()
        time.sleep(10)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            reply_to_message_id=update.id,
            disable_web_page_preview=True
        )
        return False

    # Step 9: Process yt-dlp JSON response
    if t_response:
        x_response = t_response.split("\n")[0]
        response_json = json.loads(x_response)
        randem = random_char(5)
        save_ytdl_json_path = f"{Config.DOWNLOAD_LOCATION}/{update.from_user.id}{randem}.json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        inline_keyboard = []
        duration = response_json.get("duration")

        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note") or formats.get("format")
                if format_string and "DASH" in format_string.upper():
                    continue
                format_ext = formats.get("ext")
                size = formats.get("filesize") or formats.get("filesize_approx") or 0
                cb_string_video = f"video|{format_id}|{format_ext}|{randem}"
                cb_string_file = f"file|{format_id}|{format_ext}|{randem}"

                if format_string and "audio only" not in format_string.lower():
                    ikeyboard = [InlineKeyboardButton(
                        f"📁 {format_string} {format_ext} {humanbytes(size)}",
                        callback_data=cb_string_video.encode("UTF-8")
                    )]
                else:
                    ikeyboard = [InlineKeyboardButton(
                        f"📁 [{humanbytes(size)}]",
                        callback_data=cb_string_video.encode("UTF-8")
                    )]
                inline_keyboard.append(ikeyboard)

            if duration:
                # Add mp3 buttons
                inline_keyboard.append([
                    InlineKeyboardButton(f"🎵 ᴍᴘ3 (64k)", callback_data=f"audio|64k|mp3|{randem}".encode("UTF-8")),
                    InlineKeyboardButton(f"🎵 ᴍᴘ3 (128k)", callback_data=f"audio|128k|mp3|{randem}".encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(f"🎵 ᴍᴘ3 (320k)", callback_data=f"audio|320k|mp3|{randem}".encode("UTF-8"))
                ])

            inline_keyboard.append([InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data='close')])

        else:
            format_id = response_json.get("format_id")
            format_ext = response_json.get("ext")
            cb_string_video = f"video|{format_id}|{format_ext}|{randem}"
            inline_keyboard.append([InlineKeyboardButton("📁 Document", callback_data=cb_string_video.encode("UTF-8"))])

        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(Thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )

    else:
        # fallback for nonnumeric port or empty response
        inline_keyboard = [InlineKeyboardButton("📁 ᴍᴇᴅɪᴀ", callback_data="video|OFL|ENON".encode("UTF-8"))]
        reply_markup = InlineKeyboardMarkup([inline_keyboard])
        await chk.delete(True)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=update.id
          )
