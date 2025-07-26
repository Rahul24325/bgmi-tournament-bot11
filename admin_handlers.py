"""
Admin command handlers for BGMI Tournament Bot
"""

import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config
from utils.helpers import is_admin, generate_tournament_id
from utils.messages import MessageTemplates
import logging

logger = logging.getLogger(__name__)

class AdminHandlers:
    """Handle admin-related commands and operations"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.messages = MessageTemplates()
    
    def admin_required(func):
        """Decorator to check admin permissions"""
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if not is_admin(user_id):
                await update.message.reply_text("🚫 Access Denied! Only admins can use this command.")
                return
            return await func(self, update, context)
        return wrapper
    
    @admin_required
    async def create_tournament_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournament command"""
        keyboard = [
            [InlineKeyboardButton("🧍 Solo Tournament", callback_data="create_solo")],
            [InlineKeyboardButton("👥 Duo Tournament", callback_data="create_duo")],
            [InlineKeyboardButton("👨‍👩‍👧‍👦 Squad Tournament", callback_data="create_squad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **CREATE NEW TOURNAMENT**\n\nChoose tournament type:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def create_tournament_solo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle create_solo callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await self._create_solo_tournament(query)
    
    @admin_required
    async def create_tournament_solo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamentsolo command"""
        tournament_id = generate_tournament_id()
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "HEADSHOT KING CHALLENGE",
            "type": "solo",
            "date": current_date,
            "time": current_time,
            "map": "Livik",
            "entry_fee": 50,
            "prize_type": "kill_based",
            "prize_details": {
                "per_kill": 25,
                "top_killer_bonus": 200
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            await self._send_tournament_created_message(update.message, tournament_data, "SOLO")
        else:
            await update.message.reply_text("❌ Failed to create tournament. Try again!")
    
    async def _create_solo_tournament(self, query):
        """Create solo tournament (shared logic for command and callback)"""
        tournament_id = generate_tournament_id()
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "HEADSHOT KING CHALLENGE",
            "type": "solo",
            "date": current_date,
            "time": current_time,
            "map": "Livik",
            "entry_fee": 50,
            "prize_type": "kill_based",
            "prize_details": {
                "per_kill": 25,
                "top_killer_bonus": 200
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            await self._send_tournament_created_message(query, tournament_data, "SOLO")
        else:
            await query.edit_message_text("❌ Failed to create tournament. Try again!")
    
    async def _send_tournament_created_message(self, message_or_query, tournament_data, tournament_type):
        """Send tournament created message"""
        tournament_msg = self.messages.format_tournament_post(tournament_data)
        
        keyboard = [
            [InlineKeyboardButton("✅ Join Now", callback_data=f"join_tournament_{tournament_data['tournament_id']}")],
            [InlineKeyboardButton("📜 Rules", callback_data="show_terms")],
            [InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"✅ **{tournament_type} TOURNAMENT CREATED!**\n\n{tournament_msg}"
        
        if hasattr(message_or_query, 'edit_message_text'):
            # It's a callback query
            await message_or_query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            # It's a regular message
            await message_or_query.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    async def create_tournament_duo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle create_duo callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await self._create_duo_tournament(query)
    
    async def create_tournament_squad_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle create_squad callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await self._create_squad_tournament(query)
    
    @admin_required
    async def create_tournament_duo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamentduo command"""
        tournament_id = generate_tournament_id()
        current_date = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "DYNAMIC DUOS",
            "type": "duo",
            "date": current_date,
            "time": "20:00",
            "map": "Sanhok",
            "entry_fee": 100,
            "prize_type": "position_based",
            "prize_details": {
                "first": 600,
                "second": 300,
                "third": 100
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            await self._send_tournament_created_message(update.message, tournament_data, "DUO")
        else:
            await update.message.reply_text("❌ Failed to create tournament. Try again!")
    
    async def _create_duo_tournament(self, query):
        """Create duo tournament (shared logic for command and callback)"""
        tournament_id = generate_tournament_id()
        current_date = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "DYNAMIC DUOS",
            "type": "duo",
            "date": current_date,
            "time": "20:00",
            "map": "Sanhok",
            "entry_fee": 100,
            "prize_type": "position_based",
            "prize_details": {
                "first": 600,
                "second": 300,
                "third": 100
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            await self._send_tournament_created_message(query, tournament_data, "DUO")
        else:
            await query.edit_message_text("❌ Failed to create tournament. Try again!")
    
    async def _create_squad_tournament(self, query):
        """Create squad tournament (shared logic for command and callback)"""
        tournament_id = generate_tournament_id()
        current_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "ROYALE RUMBLE",
            "type": "squad",
            "date": current_date,
            "time": "20:00",
            "map": "Erangel",
            "entry_fee": 200,
            "prize_type": "rank_based",
            "prize_details": {
                "first": 2000,
                "second": 1200,
                "third": 800
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            await self._send_tournament_created_message(query, tournament_data, "SQUAD")
        else:
            await query.edit_message_text("❌ Failed to create tournament. Try again!")
    
    @admin_required
    async def create_tournament_squad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamentsquad command"""
        tournament_id = generate_tournament_id()
        current_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        
        tournament_data = {
            "tournament_id": tournament_id,
            "name": "ROYALE RUMBLE",
            "type": "squad",
            "date": current_date,
            "time": "20:00",
            "map": "Erangel",
            "entry_fee": 200,
            "prize_type": "rank_based",
            "prize_details": {
                "first": 2000,
                "second": 1200,
                "third": 800
            },
            "upi_id": self.config.UPI_ID,
            "room_id": "",
            "room_password": "",
            "status": "upcoming"
        }
        
        success = await self.db.create_tournament(tournament_data)
        
        if success:
            tournament_msg = self.messages.format_tournament_post(tournament_data)
            
            keyboard = [
                [InlineKeyboardButton("✅ Join Now", callback_data=f"join_tournament_{tournament_id}")],
                [InlineKeyboardButton("📜 Rules", callback_data="show_terms")],
                [InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **SQUAD TOURNAMENT CREATED!**\n\n{tournament_msg}",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text("❌ Failed to create tournament. Try again!")
    
    @admin_required
    async def send_room_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sendroom command"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "📤 **SEND ROOM DETAILS**\n\n"
                "Usage: `/sendroom <tournament_id> <room_id> <password>`\n\n"
                "Example: `/sendroom SOLO123 456789 pass123`",
                parse_mode='Markdown'
            )
            return
        
        tournament_id = context.args[0]
        room_id = context.args[1]
        room_password = context.args[2]
        
        # Update tournament with room details
        update_data = {
            "room_id": room_id,
            "room_password": room_password,
            "status": "live"
        }
        
        success = await self.db.update_tournament(tournament_id, update_data)
        
        if success:
            tournament = await self.db.get_tournament(tournament_id)
            if tournament:
                # Send room details to all participants
                participants = tournament.get('participants', [])
                
                room_msg = f"""🎮 **ROOM DETAILS - {tournament['name']}**

🆔 **Room ID:** `{room_id}`
🔑 **Password:** `{room_password}`
📍 **Map:** {tournament['map']}
🕘 **Time:** {tournament['time']}

⚠️ **IMPORTANT:**
• Join exactly at {tournament['time']}
• No late entries allowed
• Screenshot your gameplay
• Follow all rules strictly

🏆 Good luck warriors! May the best player win! 💀"""

                sent_count = 0
                for participant_id in participants:
                    try:
                        await context.bot.send_message(
                            chat_id=participant_id,
                            text=room_msg,
                            parse_mode='Markdown'
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send room details to {participant_id}: {e}")
                
                await update.message.reply_text(
                    f"✅ **ROOM DETAILS SENT!**\n\n"
                    f"Tournament: {tournament['name']}\n"
                    f"Room ID: {room_id}\n"
                    f"Password: {room_password}\n"
                    f"Sent to: {sent_count}/{len(participants)} players"
                )
            else:
                await update.message.reply_text("❌ Tournament not found!")
        else:
            await update.message.reply_text("❌ Failed to update tournament!")
    
    @admin_required
    async def confirm_payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /confirm command"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "✅ **CONFIRM PAYMENT**\n\n"
                "Usage: `/confirm @username` or `/confirm user_id`\n\n"
                "Example: `/confirm @rahul123`",
                parse_mode='Markdown'
            )
            return
        
        username_or_id = context.args[0].replace('@', '')
        
        # Find user by username or ID
        user = None
        if username_or_id.isdigit():
            user = await self.db.get_user(int(username_or_id))
        else:
            # Search by username (need to implement this in database)
            pass
        
        if user:
            # Update user confirmation status
            await self.db.update_user(user['user_id'], {
                "confirmed": True,
                "paid": True
            })
            
            await update.message.reply_text(
                f"✅ **PAYMENT CONFIRMED!**\n\n"
                f"User: @{user.get('username', 'N/A')}\n"
                f"ID: {user['user_id']}\n"
                f"Status: Confirmed ✅"
            )
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text="🎉 **PAYMENT CONFIRMED!** 🎉\n\n"
                         "Your payment has been verified by admin.\n"
                         "You can now participate in tournaments!\n\n"
                         "Room details will be sent before match starts. Good luck! 🔥"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {user['user_id']}: {e}")
        else:
            await update.message.reply_text("❌ User not found!")
    
    @admin_required
    async def list_players_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listplayers command"""
        tournaments = await self.db.get_active_tournaments()
        
        if not tournaments:
            await update.message.reply_text("📋 No active tournaments found!")
            return
        
        # Show players for the first active tournament
        tournament = tournaments[0]
        participants = tournament.get('participants', [])
        
        players_msg = f"📋 **PLAYERS LIST - {tournament['name']}**\n\n"
        players_msg += f"Total Players: **{len(participants)}**\n\n"
        
        if participants:
            for i, participant_id in enumerate(participants, 1):
                user = await self.db.get_user(participant_id)
                if user:
                    status = "✅ Confirmed" if user.get('confirmed') else "⏳ Pending"
                    username = user.get('username', 'N/A')
                    players_msg += f"{i}. @{username} - {status}\n"
        else:
            players_msg += "No players registered yet!"
        
        await update.message.reply_text(players_msg, parse_mode='Markdown')
    
    @admin_required
    async def declare_winners_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /declarewinners command"""
        keyboard = [
            [InlineKeyboardButton("🧍 Solo Winner", callback_data="declare_solo")],
            [InlineKeyboardButton("👥 Duo Winners", callback_data="declare_duo")],
            [InlineKeyboardButton("👨‍👩‍👧‍👦 Squad Winners", callback_data="declare_squad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🏆 **DECLARE WINNERS**\n\nSelect tournament type:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def declare_solo_winner_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle declare_solo callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await query.edit_message_text("Please use the command: /solo <username> <kills> <prize_amount>")
    
    async def declare_duo_winner_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle declare_duo callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await query.edit_message_text("Please use the command: /duo <username1> <username2> <kills> <prize_amount>")
    
    async def declare_squad_winner_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle declare_squad callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("🚫 Access Denied! Only admins can use this command.")
            return
        
        await query.edit_message_text("Please use the command: /squad <username1> <username2> <username3> <username4> <kills> <prize_amount>")
    
    @admin_required
    async def declare_solo_winner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /solo command"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "🧍 **DECLARE SOLO WINNER**\n\n"
                "Usage: `/solo @username kills damage`\n\n"
                "Example: `/solo @rahul123 15 2540`",
                parse_mode='Markdown'
            )
            return
        
        username = context.args[0]
        kills = context.args[1]
        damage = context.args[2]
        
        # Get current tournament (simplified)
        tournaments = await self.db.get_active_tournaments()
        if tournaments:
            tournament = tournaments[0]
            
            winner_msg = self.messages.format_solo_winner(
                tournament['name'], username, kills, damage
            )
            
            # Send to channel
            try:
                await context.bot.send_message(
                    chat_id=self.config.CHANNEL_ID,
                    text=winner_msg,
                    parse_mode='HTML'
                )
                
                await update.message.reply_text(
                    f"🏆 **SOLO WINNER DECLARED!**\n\n"
                    f"Winner: {username}\n"
                    f"Kills: {kills}\n"
                    f"Damage: {damage}\n\n"
                    f"Result posted to channel! ✅"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to post result: {e}")
        else:
            await update.message.reply_text("❌ No active tournament found!")
    
    @admin_required
    async def declare_duo_winner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /duo command"""
        if len(context.args) < 4:
            await update.message.reply_text(
                "👥 **DECLARE DUO WINNERS**\n\n"
                "Usage: `/duo @player1 @player2 total_kills damage`\n\n"
                "Example: `/duo @rahul123 @amit456 25 4580`",
                parse_mode='Markdown'
            )
            return
        
        player1 = context.args[0]
        player2 = context.args[1]
        total_kills = context.args[2]
        damage = context.args[3]
        
        tournaments = await self.db.get_active_tournaments()
        if tournaments:
            tournament = tournaments[0]
            
            winner_msg = self.messages.format_duo_winner(
                tournament['name'], player1, player2, total_kills, damage
            )
            
            try:
                await context.bot.send_message(
                    chat_id=self.config.CHANNEL_ID,
                    text=winner_msg,
                    parse_mode='HTML'
                )
                
                await update.message.reply_text(
                    f"🏆 **DUO WINNERS DECLARED!**\n\n"
                    f"Winners: {player1} & {player2}\n"
                    f"Total Kills: {total_kills}\n"
                    f"Damage: {damage}\n\n"
                    f"Result posted to channel! ✅"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to post result: {e}")
        else:
            await update.message.reply_text("❌ No active tournament found!")
    
    @admin_required
    async def declare_squad_winner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /squad command"""
        if len(context.args) < 6:
            await update.message.reply_text(
                "👨‍👩‍👧‍👦 **DECLARE SQUAD WINNERS**\n\n"
                "Usage: `/squad squad_name @p1 @p2 @p3 @p4 total_kills damage`\n\n"
                "Example: `/squad \"Team Dum\" @rahul @amit @rohit @dev 35 6540`",
                parse_mode='Markdown'
            )
            return
        
        squad_name = context.args[0]
        players = context.args[1:5]  # 4 players
        total_kills = context.args[5] if len(context.args) > 5 else "0"
        damage = context.args[6] if len(context.args) > 6 else "0"
        
        tournaments = await self.db.get_active_tournaments()
        if tournaments:
            tournament = tournaments[0]
            
            winner_msg = self.messages.format_squad_winner(
                tournament['name'], squad_name, players, total_kills, damage
            )
            
            try:
                await context.bot.send_message(
                    chat_id=self.config.CHANNEL_ID,
                    text=winner_msg,
                    parse_mode='HTML'
                )
                
                await update.message.reply_text(
                    f"🏆 **SQUAD WINNERS DECLARED!**\n\n"
                    f"Squad: {squad_name}\n"
                    f"Players: {' '.join(players)}\n"
                    f"Total Kills: {total_kills}\n"
                    f"Damage: {damage}\n\n"
                    f"Result posted to channel! ✅"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to post result: {e}")
        else:
            await update.message.reply_text("❌ No active tournament found!")
    
    @admin_required
    async def clear_entries_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        await update.message.reply_text(
            "🧹 **CLEAR ENTRIES**\n\n"
            "This feature is under development.\n"
            "Contact developer for manual clearing."
        )
    
    @admin_required
    async def today_collection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /today command"""
        collection = await self.db.get_today_collection()
        
        await update.message.reply_text(
            f"📅 **TODAY'S COLLECTION**\n\n"
            f"💰 Amount: ₹{collection:.2f}\n"
            f"📊 Date: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"Keep up the good work! 🔥"
        )
    
    @admin_required
    async def weekly_collection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /thisweek command"""
        collection = await self.db.get_weekly_collection()
        
        await update.message.reply_text(
            f"📈 **THIS WEEK'S COLLECTION**\n\n"
            f"💰 Amount: ₹{collection:.2f}\n"
            f"📊 Week: {datetime.now().strftime('%W')} of {datetime.now().year}\n\n"
            f"Excellent progress! 📈"
        )
    
    @admin_required
    async def monthly_collection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /thismonth command"""
        collection = await self.db.get_monthly_collection()
        
        await update.message.reply_text(
            f"📊 **THIS MONTH'S COLLECTION**\n\n"
            f"💰 Amount: ₹{collection:.2f}\n"
            f"📊 Month: {datetime.now().strftime('%B %Y')}\n\n"
            f"Outstanding performance! 🚀"
        )
    
    @admin_required
    async def special_notification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /special command"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "💥 **SPECIAL NOTIFICATION**\n\n"
                "Usage: `/special <message>`\n\n"
                "Example: `/special Server maintenance at 10 PM`",
                parse_mode='Markdown'
            )
            return
        
        message = ' '.join(context.args)
        special_msg = f"""💥 **SPECIAL ANNOUNCEMENT** 💥

{message}

- Management Team
#DumWalaSquad #SpecialUpdate"""
        
        try:
            await context.bot.send_message(
                chat_id=self.config.CHANNEL_ID,
                text=special_msg,
                parse_mode='Markdown'
            )
            
            await update.message.reply_text(
                f"💥 **SPECIAL NOTIFICATION SENT!**\n\n"
                f"Message: {message}\n\n"
                f"Posted to channel! ✅"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send notification: {e}")
