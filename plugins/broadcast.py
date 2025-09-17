# ©️ Tg @yeah_new | YEAR-NEW | @UrlProUploaderBot

import traceback, datetime, asyncio, string, random, time, os, aiofiles, aiofiles.os
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from plugins.database.database import db
from plugins.config import Config

broadcast_ids = {}
DEFAULT_BATCH = 50
LOG_INTERVAL = 10  # seconds for periodic Koyeb log

# --------------------------
# Send message helper
# --------------------------
async def send_msg(client: Client, user_id: int, text: str):
    try:
        await client.send_message(chat_id=user_id, text=text)
        return 200, None
    except FloodWait as e:
        print(f"[BROADCAST] ⏳ FloodWait {e.x}s for {user_id}")
        await asyncio.sleep(e.x + 1)
        return await send_msg(client, user_id, text)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : invalid user id\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"

# --------------------------
# Broadcast command
# --------------------------
@Client.on_message(filters.private & filters.command('broadcast'))
async def broadcast_(client: Client, m):
    if m.from_user.id != Config.OWNER_ID:
        return

    # --------------------------
    # Parse message & batch size
    # --------------------------
    text = m.text
    if len(text.split()) == 1:
        await m.reply_text(
            "❌ Please provide message to broadcast.\nExample: /broadcast Hello all users! batch:50"
        )
        return

    parts = text.split(" batch:")
    broadcast_msg = parts[0].split(maxsplit=1)[1]
    batch_size = DEFAULT_BATCH
    if len(parts) > 1 and parts[1].isdigit():
        batch_size = int(parts[1])
        if batch_size < 10: batch_size = 10
        if batch_size > 500: batch_size = 500

    # --------------------------
    # Fetch users (async cursor fix)
    # --------------------------
    all_users_cursor = await db.get_all_users()  # async cursor
    all_users = [u async for u in all_users_cursor]  # convert to list
    total_users = len(all_users)
    print(f"[BROADCAST] 🚀 Broadcast started by {m.from_user.id} to {total_users} users | Batch size: {batch_size}")

    done = success = failed = 0
    broadcast_id = ''.join(random.choices(string.ascii_letters, k=3))
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)
    start_time = time.time()
    last_log_time = time.time()

    # --------------------------
    # Open log file
    # --------------------------
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        batch_users = []
        for user in all_users:
            batch_users.append(user)
            if len(batch_users) >= batch_size:
                for u in batch_users:
                    sts, msg = await send_msg(client, int(u['id']), broadcast_msg)
                    if msg:
                        await broadcast_log_file.write(msg)
                    if sts == 200:
                        success += 1
                    else:
                        failed += 1
                        if sts == 400:
                            await db.delete_user(int(u['id']))
                    done += 1
                    if broadcast_ids.get(broadcast_id):
                        broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

                    # Periodic Koyeb log
                    if time.time() - last_log_time > LOG_INTERVAL:
                        elapsed = time.time() - start_time
                        progress_percent = int(done / total_users * 100)
                        eta = int(elapsed / done * (total_users - done)) if done else 0
                        eta_str = str(datetime.timedelta(seconds=eta))
                        print(f"[BROADCAST] Progress: {done}/{total_users} | {progress_percent}% | ✅ {success} | ❌ {failed} | ETA: {eta_str}")
                        last_log_time = time.time()

                batch_users = []

        # Remaining users
        if batch_users:
            for u in batch_users:
                sts, msg = await send_msg(client, int(u['id']), broadcast_msg)
                if msg:
                    await broadcast_log_file.write(msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                    if sts == 400:
                        await db.delete_user(int(u['id']))
                done += 1
                if broadcast_ids.get(broadcast_id):
                    broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

    # --------------------------
    # Finish
    # --------------------------
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await m.reply_text(
        f"✅ Broadcast completed in `{completed_in}`\n\n"
        f"Total users: {total_users}\n"
        f"Total done: {done}, ✅ Success: {success}, ❌ Failed: {failed}"
    )

    if os.path.exists("broadcast.txt"):
        await aiofiles.os.remove("broadcast.txt")
        print("[BROADCAST] broadcast.txt removed")
    else:
        print("[BROADCAST] broadcast.txt not found, skipping remove")
