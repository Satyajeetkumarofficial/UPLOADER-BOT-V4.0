from plugins.database.database import db
import datetime

# Collection define karo
user_stats_col = db["user_stats"]

def today_date():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

async def update_user_stats(user_id, uploaded_gb=0, downloaded_gb=0, success_count=0):
    stats = await user_stats_col.find_one({"user_id": user_id, "date": today_date()})
    if not stats:
        await user_stats_col.insert_one({
            "user_id": user_id,
            "uploaded_gb": uploaded_gb,
            "downloaded_gb": downloaded_gb,
            "success_count": success_count,
            "date": today_date()
        })
    else:
        await user_stats_col.update_one(
            {"user_id": user_id, "date": today_date()},
            {"$inc": {
                "uploaded_gb": uploaded_gb,
                "downloaded_gb": downloaded_gb,
                "success_count": success_count
            }}
        )

async def get_user_stats(user_id):
    return await user_stats_col.find_one({"user_id": user_id, "date": today_date()})

async def get_all_stats():
    return user_stats_col.find({"date": today_date()})
