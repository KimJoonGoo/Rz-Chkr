import json
import aiohttp
from pyrogram import Client

api_id = 24731793  # your real one
api_hash = "0148f18095a6ef0964e84eac46f1fae1"  # your real one
bot_token = "8047243030:AAFD96sgHDN5rWZf_W5MAPXEQQDKKuTKBvA"  # your bot token

app = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

app = Client("rz_checker_bot", bot_token=BOT_TOKEN, api_id=api_id, api_hash=api_hash)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Welcome to Razorpay CC Checker Bot\n\n🔐 Only Premium Users Allowed.\n\nContact @KIMxGOO for access.")

@app.on_message(filters.command("addpremium") & filters.user(ADMIN_ID))
async def add_premium(client, message):
    try:
        user_id = int(message.text.split()[1])
        data = load_users()
        if user_id not in data["premium"]:
            data["premium"].append(user_id)
            save_users(data)
            await message.reply(f"✅ User `{user_id}` added to premium list.")
        else:
            await message.reply("⚠️ Already premium.")
    except:
        await message.reply("❌ Usage: /addpremium <user_id>")

@app.on_message(filters.command("removepremium") & filters.user(ADMIN_ID))
async def remove_premium(client, message):
    try:
        user_id = int(message.text.split()[1])
        data = load_users()
        if user_id in data["premium"]:
            data["premium"].remove(user_id)
            save_users(data)
            await message.reply(f"🗑️ User `{user_id}` removed from premium.")
        else:
            await message.reply("⚠️ Not found in premium list.")
    except:
        await message.reply("❌ Usage: /removepremium <user_id>")

@app.on_message(filters.command("listpremium") & filters.user(ADMIN_ID))
async def list_premium(client, message):
    data = load_users()
    if data["premium"]:
        users = "\n".join([f"`{u}`" for u in data["premium"]])
        await message.reply(f"👥 *Premium Users List:*\n{users}")
    else:
        await message.reply("⚠️ No premium users added yet.")

@app.on_message(filters.command("rz"))
async def rz_check(client, message):
    data = load_users()
    if message.from_user.id not in data["premium"]:
        return await message.reply("⛔ *Premium Only*\nContact @KIMxGOO", quote=True)

    try:
        parts = message.text.split()[1].split("|")
        cc, mm, yy, cvv = parts
    except:
        return await message.reply("❌ Format: `/rz 4111111111111111|12|2026|123`", quote=True)

    await message.reply("🔍 Checking Card on Razorpay...", quote=True)

    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(RAZORPAY_KEY, RAZORPAY_SECRET)) as session:
            async with session.post("https://api.razorpay.com/v1/tokens", json={
                "method": "card",
                "card": {
                    "number": cc,
                    "expiry_month": mm,
                    "expiry_year": yy,
                    "cvv": cvv,
                    "name": "Test User"
                }
            }) as resp:
                rjson = await resp.json()

        if 'authentication' in rjson:
            if rjson['authentication']['type'] == "auto":
                status = "✅ Auth Success (No 3D Secure)"
            else:
                status = "🔐 3D Secure Required"
        else:
            status = "❌ Declined"

        result = f"""
💳 *Razorpay Check Result*
━━━━━━━━━━━━━━
*Status:* {status}
*Card:* `**** **** **** {cc[-4:]}`
*Checked by:* @{message.from_user.username}
"""
        await message.reply(result, quote=True)

    except Exception as e:
        await message.reply(f"⚠️ Error: `{str(e)}`", quote=True)

app.run()
