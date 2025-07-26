"""
User command handlers for BGMI Tournament Bot
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config
from utils.messages import MessageTemplates
from utils.helpers import generate_referral_code, is_admin
import logging

logger = logging.getLogger(__name__)

class UserHandlers:
    """Handle user-related commands and interactions"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.messages = MessageTemplates()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with force channel join"""
        user = update.effective_user
        
        # Check if user is starting with referral code
        referral_code = None
        if context.args:
            referral_code = context.args[0]
        
        # Check if user exists in database
        user_data = await self.db.get_user(user.id)
        if not user_data:
            # Create new user
            referral_code_user = f"REF{user.id}"
            new_user_data = {
                "user_id": user.id,
                "username": user.username or "",
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "paid": False,
                "confirmed": False,
                "balance": 0,
                "referral_code": referral_code_user,
                "referred_by": referral_code if referral_code else None
            }
            
            await self.db.create_user(new_user_data)
            
            # Handle referral if provided
            if referral_code:
                referrer = await self.db.get_user_by_referral_code(referral_code)
                if referrer:
                    await self.db.add_referral(referrer['user_id'], user.id)
        
        # Check channel membership
        try:
            member = await context.bot.get_chat_member(chat_id=self.config.CHANNEL_ID, user_id=user.id)
            if member.status in ["member", "administrator", "creator"]:
                # User is member - show main menu
                await self.show_main_menu(update, context)
            else:
                # Force join channel
                await self.show_force_join(update, context)
        except Exception as e:
            logger.error(f"Membership check error: {e}")
            await self.show_force_join(update, context)
    
    async def show_force_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show force join message"""
        user = update.effective_user
        welcome_msg = self.config.WELCOME_MESSAGE.format(first_name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton("✅ Join Channel", url=self.config.CHANNEL_URL)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.edit_message_text(welcome_msg, reply_markup=reply_markup, parse_mode='HTML')
    
    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check channel membership callback"""
        query = update.callback_query
        await query.answer()
        user = query.from_user
        
        try:
            member = await context.bot.get_chat_member(chat_id=self.config.CHANNEL_ID, user_id=user.id)
            if member.status in ["member", "administrator", "creator"]:
                await self.show_main_menu(update, context)
            else:
                await query.edit_message_text(
                    text="❌ Abhi bhi channel join nahi kiya? 😠\n\n" + 
                         "Jaldi se join karo warna entry milegi hi nahi!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Join Channel", url=self.config.CHANNEL_URL)],
                        [InlineKeyboardButton("✅ I've Joined", callback_data="check_membership")]
                    ])
                )
        except Exception as e:
            logger.error(f"Membership recheck error: {e}")
            await query.edit_message_text("⚠️ System error! Try again later.")
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu after successful channel join"""
        user = update.effective_user
        user_data = await self.db.get_user(user.id)
        
        if not user_data:
            await self.start_command(update, context)
            return
        
        # Check if user is admin
        if is_admin(user.id):
            await self.show_admin_menu(update, context)
            return
        
        referral_code = user_data.get('referral_code', f'REF{user.id}')
        menu_msg = self.config.MAIN_MENU_MESSAGE.format(
            first_name=user.first_name,
            referral_code=referral_code
        )
        
        keyboard = [
            [InlineKeyboardButton("🎮 Active Tournament", callback_data="active_tournament")],
            [InlineKeyboardButton("📜 Terms & Condition", callback_data="show_terms")],
            [InlineKeyboardButton("👥 Invite Friends", callback_data="invite_friends")],
            [InlineKeyboardButton("📱 Share WhatsApp Status", callback_data="share_whatsapp")],
            [InlineKeyboardButton("📜 My Referrals", callback_data="my_referrals")],
            [InlineKeyboardButton("📜 Match History", callback_data="match_history")],
            [InlineKeyboardButton("📜 Help", callback_data="help_menu")],
            [InlineKeyboardButton("💰 Payment Status", callback_data="payment_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(menu_msg, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.callback_query:
            await update.callback_query.edit_message_text(menu_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin menu for admin users"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tournaments = await self.db.get_active_tournaments()
        live_tournament_count = len(tournaments)
        
        # Calculate next match time (simplified)
        next_match_in = "N/A"
        if tournaments:
            # Find the earliest tournament
            earliest = min(tournaments, key=lambda x: x.get('datetime', datetime.max))
            if 'datetime' in earliest:
                time_diff = earliest['datetime'] - datetime.utcnow()
                if time_diff.total_seconds() > 0:
                    next_match_in = str(int(time_diff.total_seconds() / 60))
        
        admin_msg = self.config.ADMIN_WELCOME.format(
            current_time=current_time,
            live_tournament_count=live_tournament_count,
            next_match_in=next_match_in
        )
        
        keyboard = [
            [InlineKeyboardButton("🎯 Create Tournament", callback_data="create_tournament")],
            [InlineKeyboardButton("📋 List Players", callback_data="list_players")],
            [InlineKeyboardButton("💰 Today's Collection", callback_data="today_collection")],
            [InlineKeyboardButton("📈 Weekly Collection", callback_data="weekly_collection")],
            [InlineKeyboardButton("📊 Monthly Collection", callback_data="monthly_collection")],
            [InlineKeyboardButton("🏆 Declare Winners", callback_data="declare_winners")],
            [InlineKeyboardButton("📤 Send Room Details", callback_data="send_room")],
            [InlineKeyboardButton("👤 User Menu", callback_data="user_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(admin_msg, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.callback_query:
            await update.callback_query.edit_message_text(admin_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def active_tournament(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show active tournaments"""
        query = update.callback_query
        await query.answer()
        
        tournaments = await self.db.get_active_tournaments()
        
        if not tournaments:
            await query.edit_message_text(
                "🚫 Koi active tournament nahi hai abhi!\n\n"
                "Boss tournaments create kar raha hai... thoda wait karo! 🕐",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]])
            )
            return
        
        # Show first tournament (can be expanded to show all)
        tournament = tournaments[0]
        tournament_msg = self.messages.format_tournament_info(tournament)
        
        keyboard = [
            [InlineKeyboardButton("✅ Join Tournament", callback_data=f"join_tournament_{tournament.get('tournament_id', tournament.get('_id', 'unknown'))}")],
            [InlineKeyboardButton("📜 Rules", callback_data="show_terms")],
            [InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(tournament_msg, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_terms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show terms and conditions"""
        query = update.callback_query
        await query.answer()
        
        terms_msg = """📜 **TOURNAMENT RULES**

1. 🚫 No emulators allowed - Only mobile devices
2. 🚫 No teaming/hacking/cheating
3. 🎯 Kill + Rank = Points calculation
4. ⏰ Be punctual - Late entry not allowed
5. 📱 Screenshots required for verification
6. 🎮 Follow room guidelines strictly
7. 💬 Respect other players and admins
8. 🏆 Admin decisions are final

**POINT SYSTEM:**
• Each Kill = Points
• Final Rank = Bonus Points
• Winner = Highest Total Points

Violation = Instant Ban! 🔨"""

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(terms_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_disclaimer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show disclaimer"""
        query = update.callback_query
        await query.answer()
        
        disclaimer_msg = """⚠️ **DISCLAIMER**

1. 💸 No refunds after room details are shared
2. 📡 Not responsible for network lag/disconnection
3. 🚫 Cheaters will be permanently banned
4. 🎮 Join at your own risk
5. 📱 Payment confirmation required before participation
6. 🏆 Prize distribution within 24 hours of result
7. 💼 Management reserves right to cancel/postpone
8. ⚖️ All disputes subject to admin review

**By joining, you accept all terms!**

Contact Support:
📧 dumwalasquad.in@zohomail.in
📧 rahul72411463@gmail.com
👤 @Owner_ji_bgmi"""

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(disclaimer_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def invite_friends(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show invite friends message"""
        query = update.callback_query
        await query.answer()
        
        user_data = await self.db.get_user(query.from_user.id)
        referral_code = user_data.get('referral_code', f'REF{query.from_user.id}')
        
        invite_msg = f"""👥 **INVITE FRIENDS & EARN FREE ENTRY!**

Tera Referral Code: `{referral_code}`

📤 **Share this message:**

🎮 BGMI TOURNAMENTS LIVE!
🔥 Daily Cash Prizes | Kill Rewards | VIP Matches
💥 FREE ENTRY with my code: {referral_code}
📲 Join: https://t.me/KyaTereSquadMeinDumHaiBot?start={referral_code}
⚡ Limited Slots Available!

**Benefits:**
• Friend gets FREE ENTRY
• You get referral rewards
• Build your squad network
• More friends = More tournaments!

#DumWalaSquad #ReferAurJeet"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(invite_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def share_whatsapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show WhatsApp status sharing"""
        query = update.callback_query
        await query.answer()
        
        user_data = await self.db.get_user(query.from_user.id)
        referral_code = user_data.get('referral_code', f'REF{query.from_user.id}')
        
        whatsapp_status = self.config.WHATSAPP_STATUS_TEMPLATE.format(
            referral_code=referral_code,
            user_id=query.from_user.id
        )
        
        status_msg = f"""📱 **WHATSAPP STATUS READY!**

Copy karke WhatsApp status mein daal do:

{whatsapp_status}

💡 **How to share:**
1. Copy the above text
2. Open WhatsApp
3. Post as your status
4. More people will join using your code!

🎯 **Benefits:**
• Every person who joins = Rewards for you
• Build your gaming network
• Help friends get FREE ENTRY

📞 **Need help?** Contact @Owner_ji_bgmi"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """📜 **HELP & SUPPORT**

🤖 **Bot Commands:**
• /start - Start the bot and join channel
• /paid <UTR> - Submit payment UTR number
• /help - Show this help message
• /referrals - View your referrals
• /matchhistory - View tournament history

📋 **How to Play:**
1. Join our official Telegram channel
2. Pay entry fee via UPI
3. Send payment screenshot to admin
4. Use /paid command with UTR number
5. Wait for confirmation
6. Join tournaments and win prizes!

💰 **Payment Process:**
• UPI ID: 8435010927@ybl
• Send screenshot to @Owner_ji_bgmi
• Use /paid command after payment

🎮 **Tournament Types:**
• Solo: Individual gameplay
• Duo: 2-player teams
• Squad: 4-player teams

📞 **Contact Support:**
• Admin: @Owner_ji_bgmi
• Email: dumwalasquad.in@zohomail.in
• Email: rahul72411463@gmail.com

#DumWalaSquad #BGMITournaments"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def referrals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /referrals command"""
        user = update.effective_user
        user_data = await self.db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found! Please start the bot with /start")
            return
        
        referrals = await self.db.get_user_referrals(user.id)
        referral_code = user_data.get('referral_code', f'REF{user.id}')
        
        referrals_msg = f"""👥 **YOUR REFERRALS**

🔗 **Your Referral Code:** `{referral_code}`
📊 **Total Referrals:** {len(referrals)}

📋 **Recent Referrals:**"""

        if referrals:
            for i, referral in enumerate(referrals[-10:], 1):  # Last 10 referrals
                referred_user = await self.db.get_user(referral['referred_id'])
                if referred_user:
                    username = referred_user.get('username', 'Unknown')
                    date = referral['created_at'].strftime('%d/%m/%Y')
                    referrals_msg += f"\n{i}. @{username} - {date}"
        else:
            referrals_msg += "\nNo referrals yet! Start inviting friends! 🚀"

        referrals_msg += f"""

💰 **How to Earn:**
• Share your referral code
• Friends get FREE ENTRY
• You get referral rewards

📲 **Share Link:**
https://t.me/KyaTereSquadMeinDumHaiBot?start={referral_code}

#ReferralRewards #DumWalaSquad"""

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            referrals_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def match_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /matchhistory command"""
        user = update.effective_user
        user_data = await self.db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found! Please start the bot with /start")
            return

        tournament_history = user_data.get('tournament_history', [])
        
        history_msg = f"""📊 **MATCH HISTORY**

👤 **Player:** @{user_data.get('username', 'N/A')}
🎮 **Total Tournaments:** {user_data.get('total_tournaments', 0)}
🏆 **Total Wins:** {user_data.get('total_wins', 0)}
💀 **Total Kills:** {user_data.get('total_kills', 0)}
💰 **Total Earnings:** ₹{user_data.get('total_earnings', 0)}

📈 **Performance Stats:**
• Win Rate: {((user_data.get('total_wins', 0) / max(user_data.get('total_tournaments', 1), 1)) * 100):.1f}%
• Average Kills: {(user_data.get('total_kills', 0) / max(user_data.get('total_tournaments', 1), 1)):.1f}
• Current Balance: ₹{user_data.get('balance', 0)}

📋 **Recent Tournaments:**"""

        if tournament_history:
            history_msg += "\n".join([f"• {t_id}" for t_id in tournament_history[-5:]])  # Last 5
        else:
            history_msg += "\nNo tournament history yet! Join your first tournament! 🎮"

        history_msg += "\n\n🎯 **Keep Playing to Improve Your Stats!**\n#MatchHistory #DumWalaSquad"

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            history_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle back to menu callback"""
        query = update.callback_query
        await query.answer()
        
        # Show the main menu with inline buttons
        welcome_msg = f"""🔥 **Welcome to DUM WALA SQUAD!** 🔥

🎮 Ready to dominate BGMI tournaments?
👑 Join the most exciting gaming community!

🎯 **What we offer:**
• Daily BGMI tournaments
• Instant prize money
• Fair gameplay guaranteed
• Professional room management

💰 **Quick Stats:**
• Entry Fee: ₹10-₹100
• Instant payouts via UPI
• 24/7 customer support

Choose an option below to get started:"""

        keyboard = [
            [InlineKeyboardButton("🎮 Active Tournaments", callback_data="active_tournament")],
            [InlineKeyboardButton("👥 Invite Friends", callback_data="invite_friends")],
            [InlineKeyboardButton("📱 Share WhatsApp Status", callback_data="share_whatsapp")],
            [InlineKeyboardButton("📜 Terms & Rules", callback_data="show_terms")],
            [InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
