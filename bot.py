from pyrogram import Client
import os
import logging
from plugins.config import Config
from plugins.autopost import schedule_autopost

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bot")

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)

    plugins = dict(root="plugins")
    app = Client(
        "@UploaderXNTBot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        upload_boost=True,
        sleep_threshold=300,
        plugins=plugins
    )

    async def main():
        await app.start()  # बोट स्टार्ट करें
        schedule_autopost(app)  # autopost scheduler चलाएँ
        logger.info("✅ AutoPost Scheduler is running (6 AM UTC daily)")
        print("🎊 I AM ALIVE 🎊  • Support @NT_BOTS_SUPPORT")
        await app.idle()  # बोट को लगातार चलने दें
        await app.stop()  # स्टॉप करें जब idle खत्म हो

    import asyncio
    asyncio.run(main())
