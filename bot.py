# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | @NT_BOTS_SUPPORT | LISA-KOREA/UPLOADER-BOT-V4
# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/UPLOADER-BOT-V4

import os
import logging
import plugins.admin.user_stats_cmd
from plugins.config import Config
from pyrogram import Client
from plugins.autopost import schedule_autopost   # ✅ autopost import

# ✅ Logger setup
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bot")

if __name__ == "__main__" :
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
        # ✅ Schedule autopost after bot starts
        schedule_autopost(app)
        logger.info("✅ AutoPost Scheduler is running (6 AM UTC daily)")
        print("🎊 I AM ALIVE 🎊  • Support @NT_BOTS_SUPPORT")
        await app.idle()  # बोट को लगातार चलने दें
        await app.stop()  # जब idle खत्म हो, बोट को बंद करें

    import asyncio
    asyncio.run(main())
