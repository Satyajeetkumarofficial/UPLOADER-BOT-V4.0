# plugins/poster.py

import logging
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config   # TMDB_API_KEY, OWNER_ID

logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"


async def fetch_json(url, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logger.error(f"❌ Failed API call {url}, status {resp.status}")
                return None
            return await resp.json()


@Client.on_message(filters.private & filters.command("poster"))
async def get_posters(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "⚡ Movie search karne ke liye:\n\n`/poster movie name [year]`",
            quote=True
        )
        return

    query = " ".join(message.command[1:])
    logger.info(f"🔎 Searching posters for: {query}")

    # search movie
    search_url = f"{TMDB_BASE_URL}/search/movie"
    params = {"api_key": Config.TMDB_API_KEY, "query": query}
    data = await fetch_json(search_url, params)

    if not data or not data.get("results"):
        await message.reply_text("❌ Koi result nahi mila.")
        return

    movie = data["results"][0]
    movie_id = movie["id"]
    movie_title = movie["title"]
    movie_year = movie.get("release_date", "Unknown")[:4]

    # fetch images
    images_url = f"{TMDB_BASE_URL}/movie/{movie_id}/images"
    images = await fetch_json(images_url, {"api_key": Config.TMDB_API_KEY})
    if not images:
        await message.reply_text("❌ Poster nahi mila.")
        return

    posters = images.get("posters", [])
    backdrops = images.get("backdrops", [])

    # Landscape (>=1280 width) & Portrait (tall images)
    landscape_links = [
        IMAGE_BASE_URL + b["file_path"] for b in backdrops if b.get("width", 0) >= 1200
    ][:10]

    portrait_links = [
        IMAGE_BASE_URL + p["file_path"] for p in posters if p.get("height", 0) > p.get("width", 0)
    ][:10]

    logger.info(f"✅ Found {len(landscape_links)} landscapes & {len(portrait_links)} portraits")

    buttons = []

    if landscape_links:
        # Upload first landscape
        first_landscape = landscape_links[0]
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=first_landscape,
                caption=(
                    f"🎬 <b>Movie:</b> {movie_title} ({movie_year})\n\n"
                    f"• English Landscape:\n1. First image uploaded 👆"
                ),
                parse_mode="html"
            )
        except Exception as e:
            logger.error(f"❌ Failed to send landscape: {e}")

        # Remaining landscape buttons (2-10)
        for i, link in enumerate(landscape_links[1:], start=2):
            buttons.append([InlineKeyboardButton(f"Landscape {i}", url=link)])

    if portrait_links:
        for i, link in enumerate(portrait_links, start=1):
            buttons.append([InlineKeyboardButton(f"Poster {i}", url=link)])

    if buttons:
        await message.reply_text(
            f"📌 More Posters for <b>{movie_title} ({movie_year})</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="html"
        )
    else:
        await message.reply_text("❌ Aur koi posters available nahi hai.")
