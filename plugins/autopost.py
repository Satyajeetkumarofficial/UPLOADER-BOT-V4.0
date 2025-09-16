import sys
import requests
import logging
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from plugins.config import Config

logger = logging.getLogger("plugins.autopost")

TMDB_API_KEY = Config.TMDB_API_KEY
FILE_CHANNEL = Config.FILE_CHANNEL
OWNER_ID = int(Config.OWNER_ID)   # ✅ Only Owner allowed
BASE_URL = "https://api.themoviedb.org/3"

# 🌐 Language map
LANG_MAP = {
    "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "ml": "Malayalam", "kn": "Kannada",
    "en": "English", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
    "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ur": "Urdu"
}


# ✅ Poster fetch helper (YouTube thumbnail style first)
def get_poster_url(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}/images?api_key={TMDB_API_KEY}"
        resp = requests.get(url, timeout=10).json()
        backdrops = resp.get("backdrops", [])
        posters = resp.get("posters", [])

        def pick_landscape(images, lang=None):
            for img in images:
                if lang and img.get("iso_639_1") != lang:
                    continue
                w, h = img.get("width"), img.get("height")
                if w and h and w >= 1000 and h <= 600:  # YouTube thumbnail style
                    return f"https://image.tmdb.org/t/p/original{img['file_path']}"
            return None

        # Hindi first
        url = pick_landscape(backdrops, "hi")
        if url: return url

        # English
        url = pick_landscape(backdrops, "en")
        if url: return url

        # Posters fallback
        if posters:
            return f"https://image.tmdb.org/t/p/original{posters[0]['file_path']}"

        # Any backdrop fallback
        if backdrops:
            return f"https://image.tmdb.org/t/p/original{backdrops[0]['file_path']}"

        return None
    except Exception as e:
        logger.error(f"❌ Poster fetch error: {e}")
        return None


# ✅ Format caption (same as movieinfo)
def format_caption(details, directors, top_actors, languages, tag):
    title = details.get("title")
    release_date = details.get("release_date", "N/A")
    year = release_date.split("-")[0] if release_date else "N/A"
    overview = details.get("overview", "No description available.")
    genres = ", ".join([g["name"] for g in details.get("genres", [])]) or "N/A"
    runtime = details.get("runtime", "N/A")

    caption = (
        f"🎬 <b>{title}</b> ({year})\n\n"
        f"<b>🏷 Status:</b> <code>{tag}</code>\n"
        f"<b>🗓 Release Date:</b> <code>{release_date}</code>\n"
        f"<b>⏱ Runtime:</b> <code>{runtime} min</code>\n"
        f"<b>🌐 Languages:</b> <code>{languages}</code>\n"
        f"<b>🎭 Genres:</b> <code>{genres}</code>\n"
        f"<b>🎬 Director:</b> <code>{directors}</code>\n"
        f"<b>⭐ Cast:</b> <code>{top_actors}</code>\n\n"
        f"📝 <code>{overview}</code>\n\n"
        f"Powered By : @ProBotXUpdate"
    )
    return caption


# ✅ Post movie to channel
async def send_movie_post(app, movie, tag):
    movie_id = movie["id"]

    # Movie details
    details_url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    details = requests.get(details_url, timeout=10).json()

    # Credits
    credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"
    credits = requests.get(credits_url, timeout=10).json()
    cast = credits.get("cast", [])
    crew = credits.get("crew", [])

    top_actors = ", ".join([a["name"] for a in cast[:10]]) or "N/A"
    directors = [m["name"] for m in crew if m.get("job") == "Director"]
    director_names = ", ".join(directors) if directors else "N/A"

    # Languages
    spoken_langs = details.get("spoken_languages", [])
    langs = [LANG_MAP.get(l["iso_639_1"], l["english_name"]) for l in spoken_langs]
    languages = ", ".join(langs) if langs else "N/A"

    # Poster
    poster_url = get_poster_url(movie_id)

    # Caption
    caption = format_caption(details, director_names, top_actors, languages, tag)

    try:
        if poster_url:
            await app.send_photo(FILE_CHANNEL, poster_url, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await app.send_message(FILE_CHANNEL, caption, parse_mode=ParseMode.HTML)

        logger.info(f"✅ Posted: {details.get('title')} ({tag})")
    except Exception as e:
        logger.error(f"❌ Failed to post {details.get('title')}: {e}")


# ✅ Check movies
async def check_movies(app):
    today = datetime.utcnow().date()

    url = f"{BASE_URL}/movie/upcoming?api_key={TMDB_API_KEY}&language=en-US&page=1&region=IN"
    try:
        resp = requests.get(url, timeout=10).json()
        movies = resp.get("results", [])
    except Exception as e:
        logger.error(f"❌ Fetch error: {e}")
        return

    logger.info(f"🔎 Checking {len(movies)} upcoming movies...")

    for movie in movies:
        release_date = movie.get("release_date")
        if not release_date:
            continue
        try:
            release = datetime.strptime(release_date, "%Y-%m-%d").date()
        except:
            continue

        if release == today:
            await send_movie_post(app, movie, "🎉 Releasing Today")
        elif release == today + timedelta(days=7):
            await send_movie_post(app, movie, "⏳ Releasing in 1 Week")
        elif release == today + timedelta(days=30):
            await send_movie_post(app, movie, "🗓 Releasing in 1 Month")
        elif release == today - timedelta(days=7):
            await send_movie_post(app, movie, "✅ Released 1 Week Ago")
        elif release == today - timedelta(days=30):
            await send_movie_post(app, movie, "📀 Released 1 Month Ago")
        elif release > today:
            await send_movie_post(app, movie, "📢 New Movie Added")


# ✅ Scheduler setup
def schedule_autopost(app):
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(check_movies, "cron", hour=6, args=[app])  # runs daily 6AM UTC
    scheduler.start()
    logger.info("✅ AutoPost Scheduler started (6 AM UTC)")


# ✅ Manual test command (random) - Only Owner
@Client.on_message(filters.command("autotest"))
async def autotest_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ Only owner can use this command!")
        return

    await message.reply_text("🎲 Picking random upcoming movie...")

    try:
        url = f"{BASE_URL}/movie/upcoming?api_key={TMDB_API_KEY}&language=en-US&page=1&region=IN"
        resp = requests.get(url, timeout=10).json()
        movies = resp.get("results", [])

        if not movies:
            await message.reply_text("❌ No upcoming movies found.")
            return

        movie = random.choice(movies)  # ✅ random movie pick
        await send_movie_post(client, movie, "📢 Test AutoPost")
        await message.reply_text(f"✅ Random test movie posted: {movie.get('title')}")

        logger.info(f"✅ /autotest posted random: {movie.get('title')}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
        logger.error(f"❌ /autotest failed: {e}")
