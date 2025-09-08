# ©️ Tg @yeah_new | YEAR-NEW | @NT_BOT_CHANNEL

import traceback, datetime, asyncio, string, random, time, os
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from plugins.database.database import db
from plugins.config import Config

broadcast_ids = {}

# Batch size from ENV (default = 50)
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 50))

# ========== Helper Function ==========
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        print(f"⏳ FloodWait {e.x}s for user {user_id}")
        await asyncio.sleep(e.x)
        return await send_msg(user_id, message)   # ✅ await fix
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


# ========== Broadcast Command ==========
@Client.on_message(filters.private & filters.command('broadcast'))
async def broadcast_(c, m):
    print(f"📢 Broadcast triggered by {m.from_user.id}")

    # Owner check
    if m.from_user.id != Config.OWNER_ID:
        await m.reply_text("❌ You are not authorized to use this command.")
        return

    # Reply check
    if not m.reply_to_message:
        await m.reply_text("⚠️ Please reply to a message to broadcast.")
        return

    all_users = [user async for user in db.get_all_users()]
    broadcast_msg = m.reply_to_message

    broadcast_id = ''.join(random.choice(string.ascii_letters) for _ in range(3))
    out = await m.reply_text(f"📡 Broadcast started with batch size = {BATCH_SIZE}... You’ll get log after completion.")

    start_time = time.time()
    total_users = await db.total_users_count()
    done = failed = success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)

    log_file = open('broadcast.txt', 'w')

    # Batch Processing
    for i in range(0, len(all_users), BATCH_SIZE):
        batch = all_users[i:i+BATCH_SIZE]

        tasks = [send_msg(int(user['id']), broadcast_msg) for user in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, sts in enumerate(results):
            if isinstance(sts, tuple):
                status, msg = sts
            else:
                status, msg = 500, f"{batch[idx]['id']} : {str(sts)}\n"

            if msg is not None:
                log_file.write(msg)

            if status == 200:
                success += 1
            else:
                failed += 1
                if status == 400:
                    await db.delete_user(batch[idx]['id'])

            done += 1
            broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

        print(f"✅ Progress: {done}/{total_users} users done (Batch {i//BATCH_SIZE + 1})")
        await asyncio.sleep(1)  # ✅ छोटे delay से load कम होगा

    log_file.close()

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await out.delete()

    if failed == 0:
        await m.reply_text(
            text=f"✅ Broadcast completed in `{completed_in}`\n\nTotal users: {total_users}\nDone: {done}, Success: {success}, Failed: {failed}.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"📊 Broadcast completed in `{completed_in}`\n\nTotal users: {total_users}\nDone: {done}, Success: {success}, Failed: {failed}.",
            quote=True
        )

    os.remove('broadcast.txt')
    print("🎯 Broadcast finished successfully")
