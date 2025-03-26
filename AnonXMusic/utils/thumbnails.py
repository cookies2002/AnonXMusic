import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

def resize_image(image, width, height):
    return image.resize((width, height), Image.LANCZOS)

def clean_title(text, max_length=60):
    words = text.split()
    title = ""
    for word in words:
        if len(title) + len(word) < max_length:
            title += " " + word
    return title.strip()

async def get_thumb(videoid):
    cache_path = f"cache/{videoid}.png"
    if os.path.isfile(cache_path):
        return cache_path
    
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]
        
        title = re.sub("\W+", " ", result.get("title", "No Title")).title()
        duration = result.get("duration", "Unknown Mins")
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        base_image = Image.open(f"cache/temp_{videoid}.png").convert("RGBA")
        base_image = resize_image(base_image, 1280, 720)

        background = base_image.filter(ImageFilter.GaussianBlur(8))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)

        overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 100))
        background.paste(overlay, (0, 0), overlay)

        draw = ImageDraw.Draw(background)
        font_large = ImageFont.truetype("AnonXMusic/assets/font.ttf", 50)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        
        draw.text((50, 580), clean_title(title), (255, 255, 255), font=font_large)
        draw.text((50, 640), f"{channel} | {views}", (200, 200, 200), font=font_small)
        
        play_button = Image.open("AnonXMusic/assets/play_button.png").resize((100, 100))
        background.paste(play_button, (590, 310), play_button)
        
        os.remove(f"cache/temp_{videoid}.png")
        background.save(cache_path)
        return cache_path
    
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL
