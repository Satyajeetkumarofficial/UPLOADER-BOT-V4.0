from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from io import BytesIO
from PIL import Image
from plugins.config import Config

# Resize poster to 1280x720 HD
def resize_to_hd(image_bytes, width=1280, height=720):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    
    new_img = Image.new("RGB", (width, height), (0, 0, 0))
    offset_x = (width - img.width) // 2
    offset_y = (height - img.height) // 2
    new_img.paste(img, (offset_x, offset_y))
    
    buffer = BytesIO()
    new_img.save(buffer, format="JPEG")
    buffer.name = "poster_hd.jpg"
    buffer.seek(0)
    return buffer

# Fallback image (if poster not found)
FALLBACK_IMAGE_URL = "https://i.imgur.com/UH3IPXw.jpg"

@Client.on_message(filters.command("poster") & filters.user(Config.OWNER_ID))
async def poster_command(bot: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /poster <movie name> [year]")
        return

    # Extract movie name and optional year
    if message.command[-1].isdigit() and len(message.command[-1]) == 4:
        movie_year = message.command[-1]
        movie_name = " ".join(message.command[1:-1])
    else:
        movie_year = None
        movie_name = " ".join(message.command[1:])

    await message.reply_text(f"🔎 Searching poster for: {movie_name}" + (f" ({movie_year})" if movie_year else ""))

    # TMDb Search API
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={movie_name}"
    if movie_year:
        search_url += f"&year={movie_year}"

    try:
        resp = requests.get(search_url, timeout=10).json()
    except Exception as e:
        await message.reply_text(f"❌ Error fetching data: {e}")
        return

    # Get poster
    if resp.get("results"):
        movie = resp["results"][0]
        title = movie.get("title", movie_name)
        year = movie.get("release_date", "").split("-")[0] if movie.get("release_date") else movie_year
        poster_path = movie.get("poster_path")
        
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
        else:
            poster_url = FALLBACK_IMAGE_URL  # fallback image

        try:
            poster_resp = requests.get(poster_url, timeout=10)
            hd_photo = resize_to_hd(poster_resp.content)
            caption_text = f"🎬 {title}" + (f" ({year})" if year else "")
            await message.reply_photo(photo=hd_photo, caption=caption_text)
        except Exception as e:
            await message.reply_text(f"❌ Failed to fetch poster: {e}")
    else:
        await message.reply_text(f"❌ Movie '{movie_name}' not found.")
