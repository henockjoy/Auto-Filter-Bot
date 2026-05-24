# Use @Get_emojiIDbot to get the premium emoji ID.
# Example of adding a premium emoji to message: "hello <emoji id='5210956306952758910'>👋</emoji> dear"
# If the ID (5210956306952758910) does not work, the normal emoji (👋) will be used as the default.
# The bot owner must have Telegram Premium to use premium emojis in the bot.

class script(object):

    START_TXT = """<emoji id='5210956306952758910'>👋</emoji> <b>안녕하세요 {}, <i>{}</i>
    
ʏᴏᴜʀ sᴍᴀʀᴛ ᴀssɪsᴛᴀɴᴛ 🎬
🔎 ᴊᴜsᴛ sᴇɴᴅ ᴍᴇ ᴀ ᴍᴏᴠɪᴇ/sᴇʀɪᴇs ɴᴀᴍᴇ & ɪ’ʟʟ ғᴇᴛᴄʜ ɪᴛ ғᴏʀ ʏᴏᴜ — ғᴀsᴛ & ᴀᴄᴄᴜʀᴀᴛᴇ ⚡
📌 sɪᴛ ʙᴀᴄᴋ & ᴇɴᴊᴏʏ, ɪ’ʟʟ ʜᴀɴᴅʟᴇ ᴛʜᴇ sᴇᴀʀᴄʜɪɴɢ! 💫 ♻️</b>"""

    MY_ABOUT_TXT = """★ Server: <a href=https://app.koyeb.com/>Koyeb</a>
★ Database: <a href=https://www.mongodb.com>MongoDB</a>
★ Language: <a href=https://www.python.org>Python</a>
★ Library: <a href=https://kurigram.icu/>Kurigram</a>"""

    MY_OWNER_TXT = """★ Name: FT Admin
★ Username: @FTAdminbot
★ Country: India"""

    STATUS_TXT = """👤 Total Users: <code>{}</code>
😎 Premium Users: <code>{}</code>
👥 Total Chats: <code>{}</code>
🗳 Data database used: <code>{}</code>

🗂 1st database Files: <code>{}</code>
🗳 1st files database used: <code>{}</code>

🗂 2nd database Files: <code>{}</code>
🗳 2nd files database used: <code>{}</code>

🚀 Bot Uptime: <code>{}</code>"""

    NEW_GROUP_TXT = """#NewGroup
Title - {}
ID - <code>{}</code>
Username - {}
Total - <code>{}</code>"""

    NEW_USER_TXT = """#NewUser
★ Name: {}
★ ID: <code>{}</code>"""

    NOT_FILE_TXT = """👋 Hello {},

I can't find the <b>{}</b> in my database! 🥲

👉 Google Search and check your spelling is correct.
👉 Please read the Instructions to get better results.
👉 Or not been released yet."""
    
    IMDB_TEMPLATE = """<u><b>{title}</b></u>
    
‣ 𝖸𝖾𝖺𝗋: {year} 
‣ 𝖦𝖾𝗇𝗋𝖾: {genres}
‣ 𝖱𝖺𝗍𝗂𝗇𝗀: {rating} / 10
‣ 𝖱𝗎𝗇𝖳𝗂𝗆𝖾: {runtime} Minutes
‣ 𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝖾𝖽 𝖡𝗒: {message.from_user.mention}

‣ 𝖯𝗅𝗈𝗍: {plot}‌"""

    FILE_CAPTION = """<blockquote><b>{file_name}</b>
    
<code>{file_caption}</code></blockquote>

🚫 ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ sᴇᴇɴ ᴛʜᴇ ᴍᴏᴠɪᴇ 🚫"""

    WELCOME_TEXT = """👋 Hello {mention}, Welcome to {title} group! 💞"""

    HELP_TXT = """👋 Hello {},
    
I can filter movie and series you want
Just type you want movie or series in my PM or adding me in to group
And i have more feature for you
Just try my commands"""

    ADMIN_COMMAND_TXT = """<b>Here is bot admin commands 👇


/index_channels - to check how many index channel id added
/stats - to get bot status
/delete - to delete files using query
/delete_all - to delete all indexed file
/broadcast - to send message to all bot users
/grp_broadcast - to send message to all groups
/pin_broadcast - to send message as pin to all bot users.
/pin_grp_broadcast - to send message as pin to all groups.
/restart - to restart bot
/leave - to leave your bot from particular group
/users - to get all users details
/chats - to get all groups
/invite_link - to generate invite link
/index - to index bot accessible channels
/add_prm - to add new premium user
/rm_prm - to add remove premium user
/delreq - to delete join request in db (if change REQUEST_FORCE_SUB_CHANNELS using /set_req_fsub then must need use this command)
/set_req_fsub - to set request force subscribe channel
/set_fsub - to set force subscribe channels
/repairmode - to enable/disable maintenance mode in bot</b>"""
    
    PLAN_TXT = """Activate any premium plan to get exclusive features.

You can activate any premium plan and then you can get exclusive features.

Basic premium features:
Ad free experience
Online watch and fast download
No need joind channels
No need verify
No shortlink
Admins support
And more...

Available Plans:
<blockquote>{}</blockquote>

Support: @{}"""

    USER_COMMAND_TXT = """<b>Here is bot user commands 👇

/start - to check bot alive or not
/myplan - to check my activated premium plan
/plan - to view premium plan details
/img_2_link - upload image to uguu.se and get link
/settings - to change group settings as your wish
/connect - to connect group settings to PM
/id - to check group or channel id
/download - Download videos from YouTube, Facebook, TikTok, Instagram, and more platforms.</b>"""
    
    SOURCE_TXT = """<b>ʙᴏᴛ ɢɪᴛʜᴜʙ ʀᴇᴘᴏsɪᴛᴏʀʏ -

- ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀɴ ᴏᴘᴇɴ ꜱᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.

- ꜱᴏᴜʀᴄᴇ - <a href=https://github.com/HA-Bots/Auto-Filter-Bot>ʜᴇʀᴇ</a>

- ᴅᴇᴠʟᴏᴘᴇʀ - @HA_Bots"""


    NEW_ADDED_TEMPLATE = """<b>✅{title} {year}</b>
<code>⏱ {runtime} Min | ⭐ {rating}</code>

<blockquote><b>🎙 {language}</b></blockquote>
📽 Genre:</b> {genres}"""
