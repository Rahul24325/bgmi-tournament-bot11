"""
Tournament-related handlers for BGMI Tournament Bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config
from utils.messages import MessageTemplates
import logging

logger = logging.getLogger(__name__)

class TournamentHandlers:
    """Handle tournament-related operations"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.messages = MessageTemplates()
    
    async def join_tournament(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament join callback"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        tournament_id = query.data.replace("join_tournament_", "")
        
        # Get user data
        user_data = await self.db.get_user(user.id)
        if not user_data:
            await query.edit_message_text(
                "❌ User not found! Please start the bot first with /start",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
                ]])
            )
            return
        
        # Get tournament data
        tournament = await self.db.get_tournament(tournament_id)
        if not tournament:
            await query.edit_message_text(
                "❌ Tournament not found!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
                ]])
            )
            return
        
        # Check if user is already registered
        if user.id in tournament.get('participants', []):
            await query.edit_message_text(
                f"✅ **Already Registered!**\n\n"
                f"Tournament: {tournament['name']}\n"
                f"Your spot is confirmed! 🎮\n\n"
                f"Room details will be sent before match.\n"
                f"Stay tuned! 📢",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]]),
                parse_mode='Markdown'
            )
            return
        
        # Check payment status
        if not user_data.get('paid') or not user_data.get('confirmed'):
            payment_msg = f"""💰 **PAYMENT REQUIRED**

Tournament: **{tournament['name']}**
Entry Fee: **₹{tournament['entry_fee']}**

📝 **Payment Process:**
1. Pay ₹{tournament['entry_fee']} to UPI: `{self.config.UPI_ID}`
2. Send payment screenshot to {self.config.ADMIN_USERNAME}
3. Use /paid command with UTR number
4. Wait for admin confirmation

⚠️ **Important:** Payment must be confirmed before joining!

Need help? Contact {self.config.ADMIN_USERNAME}"""

            keyboard = [
                [InlineKeyboardButton("💸 Payment Done", callback_data="payment_done")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                payment_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Add user to tournament
        success = await self.db.add_participant_to_tournament(tournament_id, user.id)
        
        if success:
            # Create success message
            join_msg = f"""🎉 **TOURNAMENT JOINED SUCCESSFULLY!** 🎉

🎮 **Tournament:** {tournament['name']}
📅 **Date:** {tournament['date']}
🕘 **Time:** {tournament['time']}
📍 **Map:** {tournament['map']}
💰 **Entry Fee:** ₹{tournament['entry_fee']} ✅

🏆 **Next Steps:**
• Room details will be sent 15 minutes before match
• Be ready with your squad/duo (if applicable)
• Follow all tournament rules
• Take screenshots for verification

⚡ **Pro Tips:**
• Charge your device fully
• Stable internet connection required
• Keep the bot chat open for updates

Good luck warrior! May the best player win! 🔥

#DumWalaSquad #TournamentReady"""

            keyboard = [
                [InlineKeyboardButton("📜 Tournament Rules", callback_data="show_terms")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                join_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"User {user.id} joined tournament {tournament_id}")
        else:
            await query.edit_message_text(
                "❌ Failed to join tournament! Please try again later.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
                ]])
            )
    
    async def show_tournament_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tournament_id: str):
        """Show detailed tournament information"""
        tournament = await self.db.get_tournament(tournament_id)
        
        if not tournament:
            await update.callback_query.edit_message_text(
                "❌ Tournament not found!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
                ]])
            )
            return
        
        details_msg = self.messages.format_detailed_tournament_info(tournament)
        
        keyboard = [
            [InlineKeyboardButton("✅ Join Tournament", callback_data=f"join_tournament_{tournament_id}")],
            [InlineKeyboardButton("📜 Rules", callback_data="show_terms")],
            [InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            details_msg,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def tournament_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show tournament status and participants"""
        query = update.callback_query
        await query.answer()
        
        tournaments = await self.db.get_active_tournaments()
        
        if not tournaments:
            await query.edit_message_text(
                "📊 **TOURNAMENT STATUS**\n\n"
                "No active tournaments at the moment.\n"
                "Check back later for new tournaments! 🎮",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
                ]])
            )
            return
        
        # Show status for first active tournament
        tournament = tournaments[0]
        participants = tournament.get('participants', [])
        
        status_msg = f"""📊 **TOURNAMENT STATUS**

🎮 **{tournament['name']}**
📅 Date: {tournament['date']}
🕘 Time: {tournament['time']}
📍 Map: {tournament['map']}

👥 **Participants:** {len(participants)}
💰 **Prize Pool:** ₹{self._calculate_prize_pool(tournament)}
🎯 **Status:** {tournament['status'].upper()}

🔥 **Recent Registrations:**"""

        # Show last 5 participants
        recent_participants = participants[-5:] if len(participants) > 5 else participants
        
        for i, participant_id in enumerate(recent_participants, 1):
            user = await self.db.get_user(participant_id)
            if user:
                username = user.get('username', 'Player')
                status_msg += f"\n{i}. @{username}"
        
        if not participants:
            status_msg += "\nNo participants yet! Be the first to join! 🚀"
        
        keyboard = [
            [InlineKeyboardButton("✅ Join Now", callback_data=f"join_tournament_{tournament['tournament_id']}")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="tournament_status")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def _calculate_prize_pool(self, tournament):
        """Calculate total prize pool for tournament"""
        prize_details = tournament.get('prize_details', {})
        
        if tournament.get('prize_type') == 'fixed':
            return prize_details.get('winners_amount', 0)
        elif tournament.get('prize_type') == 'rank_based':
            return sum([
                prize_details.get('first', 0),
                prize_details.get('second', 0),
                prize_details.get('third', 0)
            ])
        elif tournament.get('prize_type') == 'kill_based':
            # Estimate based on participants and average kills
            participants = len(tournament.get('participants', []))
            estimated_kills = participants * 3  # Average 3 kills per player
            per_kill = prize_details.get('per_kill', 0)
            bonus = prize_details.get('top_killer_bonus', 0)
            return (estimated_kills * per_kill) + bonus
        
        return 0
    
    async def leave_tournament(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament leave request"""
        query = update.callback_query
        await query.answer()
        
        tournament_id = query.data.replace("leave_tournament_", "")
        user_id = query.from_user.id
        
        # Get tournament
        tournament = await self.db.get_tournament(tournament_id)
        if not tournament:
            await query.edit_message_text("❌ Tournament not found!")
            return
        
        # Check if user is in tournament
        if user_id not in tournament.get('participants', []):
            await query.edit_message_text("❌ You are not registered for this tournament!")
            return
        
        # Remove user from tournament
        participants = tournament.get('participants', [])
        participants.remove(user_id)
        
        success = await self.db.update_tournament(tournament_id, {'participants': participants})
        
        if success:
            await query.edit_message_text(
                f"✅ **Left Tournament Successfully!**\n\n"
                f"Tournament: {tournament['name']}\n"
                f"You have been removed from the participant list.\n\n"
                f"You can rejoin anytime before the tournament starts.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]]),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Failed to leave tournament! Try again later.")
