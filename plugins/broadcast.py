# ©️ Tg @yeah_new | YEAR-NEW | @UrlProUploaderBot

import traceback, datetime, asyncio, string, random, time, os, aiofiles, aiofiles.os
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from plugins.database.database import db
from plugins.config import Config

broadcast_ids = {}
DEFAULT_BATCH = 50
LOG_INTERVAL = 10  # seconds

# ──────────────────────────
# Send message helper
# ──────────────────────────
async def send_msg(client: Client, user_id: int, message):
    try:
        if isinstance(message, str):
            await client.send_message(chat_id=user_id, text=message)
        else:
            await message.copy(chat_id=user_id)
        return 200, None

    except FloodWait as e:
        print(f"[BROADCAST] ⏳ FloodWait {e.x}s for {user_id}")
        await asyncio.sleep(e.x + 1)
        return await send_msg(client, user_id, message)

    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : invalid user id\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


# ──────────────────────────
# Broadcast Command
# ──────────────────────────
@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast_(client: Client, m):
    if m.from_user.id != Config.OWNER_ID:
        return

    # ── Determine broadcast content ──
    if m.reply_to_message:
        broadcast_content = m.reply_to_message
    else:
        if len(m.command) == 1:
            await m.reply_text(
                "❌ Reply to a message or use:\n"
                "`/broadcast Your message here batch:50`"
            )
            return

        parts = m.text.split(" batch:")
        broadcast_content = parts[0].split(maxsplit=1)[1]

    # ── Batch size ──
    batch_size = DEFAULT_BATCH
    if "batch:" in m.text:
        try:
            batch_size = int(m.text.split("batch:")[1])
            batch_size = max(10, min(batch_size, 500))
        except:
            pass

    # ── Fetch users ──
    all_users_cursor = await db.get_all_users()
    all_users = [u async for u in all_users_cursor]
    total_users = len(all_users)

    print(f"[BROADCAST] 🚀 Started | Users: {total_users} | Batch: {batch_size}")

    done = success = failed = 0
    broadcast_id = ''.join(random.choices(string.ascii_letters, k=4))
    broadcast_ids[broadcast_id] = dict(total=total_users)

    start_time = time.time()
    last_log_time = time.time()

    async with aiofiles.open("broadcast.txt", "w") as log_file:
        batch = []

        for user in all_users:
            batch.append(user)

            if len(batch) >= batch_size:
                for u in batch:
                    sts, msg = await send_msg(client, int(u["id"]), broadcast_content)

                    if msg:
                        await log_file.write(msg)

                    if sts == 200:
                        success += 1
                    else:
                        failed += 1
                        if sts == 400:
                            await db.delete_user(int(u["id"]))

                    done += 1

                    if time.time() - last_log_time > LOG_INTERVAL:
                        percent = int(done / total_users * 100)
                        eta = int((time.time() - start_time) / done * (total_users - done)) if done else 0
                        print(
                            f"[BROADCAST] {done}/{total_users} "
                            f"| {percent}% | ✅ {success} | ❌ {failed} | ETA {datetime.timedelta(seconds=eta)}"
                        )
                        last_log_time = time.time()

                batch = []

        # ── Remaining users ──
        for u in batch:
            sts, msg = await send_msg(client, int(u["id"]), broadcast_content)

            if msg:
                await log_file.write(msg)

            if sts == 200:
                success += 1
            else:
                failed += 1
                if sts == 400:
                    await db.delete_user(int(u["id"]))

            done += 1

    broadcast_ids.pop(broadcast_id, None)

    completed = datetime.timedelta(seconds=int(time.time() - start_time))
    await m.reply_text(
        f"✅ **Broadcast Completed**\n\n"
        f"⏱ Time: `{completed}`\n"
        f"👥 Total: `{total_users}`\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`"
    )

    if os.path.exists("broadcast.txt"):
        await aiofiles.os.remove("broadcast.txt")
