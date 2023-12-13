import time
import asyncio
from os import environ as evn
from database import Database
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid


app = Client(
    name='requestBot',
    bot_token=evn.get("BOT_TOKEN"),
    api_id=evn.get("API_ID"),
    api_hash=evn.get("API_HASH")
)
app.db = Database()


@app.on_chat_join_request(filters.group | filters.channel)
async def autoapprove(c, m):
    await c.db.add_user(m.from_user.id)
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
        button = [[
            InlineKeyboardButton("📮 𝗨𝗣𝗗𝗔𝗧𝗘𝗦 📮", url="https://t.me/M_MOVIES_23"), InlineKeyboardButton("🎭 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 🎭", url="https://t.me/mallumovies_1")
        ]]
        markup = InlineKeyboardMarkup(button)
        caption = f'<b>𝐇𝐞𝐲 {m.from_user.mention()}\n\n𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐅𝐨𝐫 {m.chat.title} 𝐈𝐬 𝐀𝐜𝐜𝐞𝐩𝐭𝐞𝐝 ✅</b>'
        await c.send_photo(
            m.from_user.id, 
            photo='https://telegra.ph/file/d3028731972d2e0f64252.jpg', 
            caption=caption, 
            reply_markup=markup
        )
    except UserIsBlocked:
        print(f"{m.from_user.first_name} blocked the bot")
    except PeerIdInvalid:
        print(f"User {m.from_user.first_name} haven't started the bot yet")
    except Exception as e:
        print('Error:', e)


@app.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c, m):
    text = f'''<b>🤝 𝐇𝐞𝐥𝐥𝐨 {m.from_user.mention()} \n\n🐞 𝐈 𝐚𝐦 𝐀𝐮𝐭𝐨 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐀𝐜𝐜𝐞𝐩𝐭 𝐁𝐨𝐭 𝐖𝐢𝐭𝐡 𝐖𝐨𝐫𝐤𝐢𝐧𝐠 𝐅𝐨𝐫 𝐀𝐥𝐥 𝐂𝐡𝐚𝐧𝐧𝐞𝐥. 𝐀𝐝𝐝 𝐌𝐞 𝐈𝐧 𝐘𝐨𝐮𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐓𝐨 𝐔𝐬𝐞 😍</b>'''
    button = [[        
       InlineKeyboardButton('⚚ 𝗔𝗱𝗱 𝘁𝗼 𝗚𝗿𝗼𝘂𝗽 ⚚', url='https://t.me/MM_Accept_bot?startgroup=Bots4Sale&admin=invite_users+manage_chat'),
       InlineKeyboardButton('⚚ 𝗔𝗱𝗱 𝘁𝗼 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 ⚚', url='https://t.me/MM_Accept_bot?startchannel=Bots4Sale&admin=invite_users+manage_chat')
    ],[  
       InlineKeyboardButton("📮 𝗨𝗣𝗗𝗔𝗧𝗘𝗦 📮", url="https://t.me/M_MOVIES_23"), InlineKeyboardButton("🎭 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 🎭", url="https://t.me/mallumovies_1") 
    ]]
    m = await m.reply_sticker("CAACAgUAAxkBAAI8T2VkLQxCimPbyxhJuXINXsnjKyNsAAKnAAMEgnsg9bWbdDtN4EEeBA") 
    await asyncio.sleep(2)
    await m.reply_photo('https://telegra.ph/file/f466c02f7c390996d83ec.jpg', 
        caption=text,
        reply_markup=InlineKeyboardMarkup(button),
        quote=True
    )
    return await m.delete()


AUTH_USER = [int(user) for user in evn.get('AUTH_USERS', 0).split(' ')]
@app.on_message(filters.command('broadcast') & filters.private & filters.incoming & filters.chat(AUTH_USER))
async def broadcast(c, m):
    if not m.reply_to_message:
        return await m.reply_text('Reply to a message that i need to broadast.', quote=True)

    msg = m.reply_to_message
    users = await c.db.get_all_users()

    start = time.time()
    last_edited = 0
    failed = 0
    success = 0
    total = await c.db.total_users_count()
    sts = await m.reply_text(f'Board Cast Started\n\nTotal no of users: {total}', quote=True)


    async def send_msg(c, user_id):
        try:
            return await msg.copy(user_id)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            return await send_msg(c, user_id)
        except InputUserDeactivated:
            await c.db.delete_user(user_id)
            print(f"{user_id} : deactivated")
        except UserIsBlocked:
            await c.db.delete_user(user_id)
            print(f"{user_id} : blocked the bot")
        except PeerIdInvalid:
            await c.db.delete_user(user_id)
            print(f"{user_id} : user id invalid")
        except Exception as e:
            print(f"{user_id} : {e}")

    async for user in users:
        user = await send_msg(c, user['id'])
        if user:
            success += 1
        else:
            failed += 1
        if last_edited - start == 5:
            try:
                await sts.edit(f'Total: {total}\nSuccess: {success}\nFailed: {failed}') 
                last_edited = time.time()
            except:
                pass
        await asyncio.sleep(0.5)

    await sts.edit(f'**BroadCast Completed:**\n\nTotal: {total}\nSuccess: {success}\nFailed: {failed}')

if __name__ == '__main__':
    app.run()
