import os
import string
import random
import asyncio
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
API_ID = 20924129
API_HASH = "41fa64770dfccb944a7d1397a4c4129b"
BOT_TOKEN = "8226503364:AAFb0gWMBY3PN52KR5bZRQxBXFr0j3puUn4"
MONGO_URL = "mongodb+srv://emptyaddress02:emptyaddress02@knightsxbots.nf0gpri.mongodb.net/?retryWrites=true&w=majority&appName=KnightsXBots"
CHANNEL_ID = -1002857189059  # replace with your private channel ID
OWNER_ID = 6946299352

# ================= INIT =================
client = Client("storage-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URL)
db = mongo["storagebot"]
users_col = db["users"]
files_col = db["files"]

# ================= HELP TEXT =================
HELP_TEXT = """📚 Bot Commands & Usage

Here are the available commands:

👥 User Commands:
• /start - Start the bot
• /help - Show this help message
• /about - About the bot
• /owner - Owner information
• /upload - Upload a file (reply to file)
• /batch - Upload multiple files as a batch

⚠️ Need Help? Ask on @KnightsXBots"""

# ================= UTIL =================
def gen_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

async def add_user(user_id):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id})

# ================= HANDLERS =================
@client.on_message(filters.command("start"))
async def start_cmd(_, m):
    await add_user(m.from_user.id)
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("📚 Help", callback_data="help")]])
    await m.reply_text("👋 Welcome! Forward me a file and reply /upload to get a shareable link.", reply_markup=btn)

@client.on_message(filters.command("help"))
async def help_cmd(_, m):
    await m.reply_text(HELP_TEXT)

@client.on_message(filters.command("about"))
async def about_cmd(_, m):
    await m.reply_text("🤖 This bot stores your files and generates links! Made with ⚡ by @KnightsXBots")

@client.on_message(filters.command("owner"))
async def owner_cmd(_, m):
    await m.reply_text("👑 Owner: @Nagi2308")

# ============ UPLOAD ============
@client.on_message(filters.command("upload") & filters.reply)
async def upload_cmd(_, m):
    replied = m.reply_to_message
    if not (replied.document or replied.video or replied.photo):
        return await m.reply_text("❌ Please reply to a media file.")

    msg = await replied.copy(CHANNEL_ID)
    file_id = gen_id()
    files_col.insert_one({"_id": file_id, "file_msg": msg.id})

    link = f"https://t.me/{(await client.get_me()).username}?start={file_id}"
    await m.reply_text(f"✅ Uploaded! Here is your link:\n{link}")

# ============ BATCH ============
@client.on_message(filters.command("batch"))
async def batch_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("Reply with /batch to multiple media (album).")
    album = m.reply_to_message
    msgs = [album]
    batch_id = gen_id()
    ids = []
    for msg in msgs:
        cp = await msg.copy(CHANNEL_ID)
        fid = gen_id()
        ids.append(fid)
        files_col.insert_one({"_id": fid, "file_msg": cp.id})
    files_col.insert_one({"_id": batch_id, "batch": ids})
    link = f"https://t.me/{(await client.get_me()).username}?start={batch_id}"
    await m.reply_text(f"✅ Batch Uploaded! Link:\n{link}")

# ============ START PARAM (OPEN LINKS) ============
@client.on_message(filters.private & filters.command("start") & filters.regex(r"start (.+)"))
async def fetch_link(_, m):
    file_id = m.command[1]
    data = files_col.find_one({"_id": file_id})
    if not data:
        return await m.reply_text("❌ Invalid link!")

    if "batch" in data:
        for fid in data["batch"]:
            d = files_col.find_one({"_id": fid})
            if d:
                await client.copy_message(m.chat.id, CHANNEL_ID, d["file_msg"])
    else:
        await client.copy_message(m.chat.id, CHANNEL_ID, data["file_msg"])

# ============ BROADCAST ============
@client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("Reply to a message to broadcast.")
    count = 0
    for user in users_col.find():
        try:
            await m.reply_to_message.copy(user["_id"])
            count += 1
        except:
            pass
    await m.reply_text(f"✅ Broadcast sent to {count} users.")

@client.on_message(filters.command("del_cast") & filters.user(OWNER_ID))
async def del_cast_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("Reply to a broadcast to delete.")
    # Not directly possible to delete broadcasted messages from user chats.
    await m.reply_text("⚠️ Can't delete user messages. Only channel/group messages can be deleted.")

# ================= RUN =================
print("Bot Started ⚡")
client.run()
