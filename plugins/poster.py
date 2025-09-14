from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from io import BytesIO
from PIL import Image
from plugins.config import Config

def resize_to_hd(image_bytes, width=1280, height=720):
    img = Image.open(BytesIO(image_bytes))
    img = img.convert("RGB")
    img.thumbnail((width, height), Image.ANTIALIAS)  # maintain aspect ratio
    # Create new image with exact size (optional: fill background)
    new_img = Image.new("RGB", (width, height), (0,0,0))
    offset_x = (width - img.width) // 2
    offset_y = (height - img.height) // 2
    new_img.paste(img, (offset_x, offset_y))
    buffer = BytesIO()
    new_img.save(buffer, format="JPEG")
    buffer.name = "poster_hd.jpg"
    buffer.seek(0)
    return buffer

@Client.on_message(filters.command("poster") & filters.user(Config.OWNER_ID))
async def poster_command(bot: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /poster <movie name>")
        return

    movie_name = " ".join(message.command[1:])
    await message.reply_text(f"🔎 Searching poster for: {movie_name}...")

    # TMDb Search API
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={movie_name}"
    resp = requests.get(search_url).json()

    if resp.get("results"):
        movie = resp["results"][0]
        poster_path = movie.get("poster_path")
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
            
            # Fetch image
            poster_resp = requests.get(poster_url)
            hd_photo = resize_to_hd(poster_resp.content)  # Resize to 1280x720

            await message.reply_photo(photo=hd_photo)
        else:
            await message.reply_text(f"❌ Poster not found for '{movie_name}'.")
    else:
        await message.reply_text(f"❌ Movie '{movie_name}' not found.")
