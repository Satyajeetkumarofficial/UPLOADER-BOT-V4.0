from plugins.database.database import db
import datetime

# 🗓 आज की तारीख (UTC me) return karega
def today_date():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

# 📊 User stats update / insert karega
async def update_user_stats(user_id, uploaded_gb=0, downloaded_gb=0, success_count=0):
    stats = await db.db["user_stats"].find_one({"user_id": user_id, "date": today_date()})
    if not stats:
        await db.db["user_stats"].insert_one({
            "user_id": user_id,
            "uploaded_gb": uploaded_gb,
            "downloaded_gb": downloaded_gb,
            "success_count": success_count,
            "date": today_date()
        })
    else:
        await db.db["user_stats"].update_one(
            {"user_id": user_id, "date": today_date()},
            {"$inc": {
                "uploaded_gb": uploaded_gb,
                "downloaded_gb": downloaded_gb,
                "success_count": success_count
            }}
        )

# 🧾 Ek user ke stats laane ke liye
async def get_user_stats(user_id):
    return await db.db["user_stats"].find_one({"user_id": user_id, "date": today_date()})

# 📈 Aaj ke sabhi users ke stats laane ke liye
async def get_all_stats():
    return db.db["user_stats"].find({"date": today_date()})
