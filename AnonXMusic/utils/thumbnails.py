import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from AnonXMusic import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    return image.resize((maxWidth, maxHeight))

def clear(text, limit=50):
    return " ".join(text.split()[:limit])

async def get_thumb(videoid):
    cache_path = f"cache/{videoid}.png"
    if os.path.isfile(cache_path):
        return cache_path
    
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result.get("title", "Unknown Title")).title()
            duration = result.get("duration", "Unknown")
            thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/tmp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())
        
        youtube = Image.open(f"cache/tmp_{videoid}.png").convert("RGBA")
        image1 = changeImageSize(1280, 720, youtube)
        blurred_bg = image1.filter(ImageFilter.GaussianBlur(15))
        enhancer = ImageEnhance.Brightness(blurred_bg)
        background = enhancer.enhance(0.3)
        overlay = Image.new("RGBA", background.size, (0, 0, 0, 90))
        background.paste(overlay, (0, 0), overlay)
        
        draw = ImageDraw.Draw(background)
        font_main = ImageFont.truetype("AnonXMusic/assets/font.ttf", 42)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        
        draw.text((50, 550), f"{channel}  |  {views}", (255, 255, 255), font=font_small)
        draw.text((50, 600), clear(title, 8), (255, 255, 255), font=font_main)
        draw.rectangle([(50, 670), (1220, 675)], fill="white")
        
        draw.text((50, 690), "00:00", (255, 255, 255), font=font_small)
        draw.text((1150, 690), duration, (255, 255, 255), font=font_small)
        
        background.save(cache_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return cache_path
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
