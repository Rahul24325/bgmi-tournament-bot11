"""
Configuration settings for BGMI Tournament Bot
"""

import os
from typing import List

class Config:
    """Bot configuration class"""
    
    # Bot credentials
    BOT_TOKEN: str = "8341741465:AAG81VWIc84evKwBR1IIbwMoaHQJwgLXLsY"
    
    # Admin settings
    ADMIN_ID: int = 5558853984
    ADMIN_USERNAME: str = "@Owner_ji_bgmi"
    
    # Channel settings
    CHANNEL_ID: int = -1002880573048
    CHANNEL_URL: str = "https://t.me/KyaTereSquadMeinDumHai"
    
    # Payment settings
    UPI_ID: str = "8435010927@ybl"
    
    # Database settings
    MONGODB_URI: str = "mongodb+srv://rahul7241146384:rahul7241146384@cluster0.qeaogc4.mongodb.net/"
    DATABASE_NAME: str = "bgmi_tournament_bot"
    
    # AI API settings
    AI_API_KEY: str = os.getenv("AI_API_KEY", "d96a2478-7fde-4d76-a28d-b8172e561077")
    
    # Contact information
    SUPPORT_EMAILS: List[str] = [
        "dumwalasquad.in@zohomail.in",
        "rahul72411463@gmail.com"
    ]
    
    # Social media
    INSTAGRAM_HANDLE: str = "@ghostinside.me"
    
    # Tournament settings
    DEFAULT_ENTRY_FEE: int = 50
    REFERRAL_REWARD: str = "FREE ENTRY"
    
    # Message templates
    WELCOME_MESSAGE = """🚨 Oye {first_name}! Tere jaise player ka welcome hai is killer lobby mein! 🔥
Yaha kill count bolta hai, aur noobs chup rehte hain! 😎
👑 Game jeetne ka sirf ek rasta – Kya Tere Squad Mein Dum Hai? join karo, squad banao, aur kill machine ban jao!
💸 Paisa nahi?
👉 Toh bhai referral bhej! Dost ko bula, aur FREE ENTRY kama!
🤑 Referral se naam bhi banega aur game bhi chalega!
📧 Need help? Contact support:
🔹 dumwalasquad.in@zohomail.in
🔹 rahul72411463@gmail.com
🔹 @Owner_ji_bgmi
📢 Channel join karna mandatory hai warna result miss ho jayega:
👉 Official Channel – Kya Tere Squad Mein Dum Hai?
📸 Insta pe bhi connect ho ja bhai:
👉 @ghostinside.me
💬 Respect dega toh squad respect degi... warna bot bhi ban kar dega 🤨
#DumWalaSquad #ReferAurJeet #GhostInsideMe"""

    MAIN_MENU_MESSAGE = """🔥 Lobby Access Granted! 🔥

Ab kya plan hai bhai {first_name}?

Tera Personal Referral Code: `{referral_code}`
Dost ko bhej, aur FREE ENTRY pa!"""

    ADMIN_WELCOME = """👑 *Welcome, Boss!*  
"Tere aane se system bhi alert ho gaya hai!"

🕐 *Login Time:* `{current_time}`  
📢 *Live Tournaments:* `{live_tournament_count}`  
📈 *Next Match In:* `{next_match_in} minutes`

🛠 *ADMIN PANEL:*  
/createtournament - 🎯 New tournament  
/sendroom - 📤 Send room details  
/confirm - ✅ Approve players  
/listplayers - 📋 Participant list  
/declarewinners - 🏆 Announce winners  
/clear - 🧹 Edit/remove entries  
/today - 📅 Today's collection  
/thisweek - 📈 Weekly collection  
/thismonth - 📊 Monthly collection  
/squad - 👑 Squad victory  
/duo - 🔥 Duo victory  
/solo - 🧍 Solo victory  
/special - 💥 Custom notifications

Sab kuch tere haath mein hai Bhai... aur haath garam hai! 🔥"""

    WHATSAPP_STATUS_TEMPLATE = """🎮 BGMI TOURNAMENTS LIVE!
🔥 Daily Cash 💰 | 💀 Kill Rewards | 👑 VIP Matches
💥 FREE ENTRY with my code 👉 {referral_code}
📲 Click & Join:
https://t.me/KyaTereSquadMeinDumHaiBot?start={user_id}
⚡ Limited Slots! Fast join karo!

#BGMI #EarnWithKills"""
