"""
Message templates and formatting utilities for BGMI Tournament Bot
"""

import random
from datetime import datetime
from typing import Dict, Any, List

class MessageTemplates:
    """Message formatting and template utilities"""
    
    def __init__(self):
        self.victory_numbers = ["❶", "➊", "⓵", "🥇", "👑"]
        self.hashtags = [
            "#DumWalaSquad", "#LobbyCleaner", "#KhatarnakJodi", 
            "#SquadGoals", "#WinnerWinner", "#ChickenDinner",
            "#BGMIChampion", "#TournamentKing", "#KillMachine"
        ]
    
    def format_tournament_post(self, tournament: Dict[str, Any]) -> str:
        """Format tournament announcement post"""
        prize_info = self._format_prize_info(tournament)
        
        return f"""🎮 <b>TOURNAMENT ALERT</b>

🏆 <b>{tournament['name']}</b>
📅 Date: {tournament['date']}
🕘 Time: {tournament['time']}
📍 Map: {tournament['map']}
💰 Entry Fee: ₹{tournament['entry_fee']}
🎁 {prize_info}

🔽 <b>JOIN & DETAILS</b> 🔽"""
    
    def format_tournament_info(self, tournament: Dict[str, Any]) -> str:
        """Format tournament information for display"""
        prize_info = self._format_prize_info(tournament)
        participant_count = len(tournament.get('participants', []))
        
        return f"""🎮 <b>{tournament['name']}</b>

📊 <b>Tournament Details:</b>
• Type: {tournament['type'].upper()}
• Date: {tournament['date']}
• Time: {tournament['time']}
• Map: {tournament['map']}
• Entry Fee: ₹{tournament['entry_fee']}

🎁 <b>Prize Structure:</b>
{prize_info}

👥 <b>Participants:</b> {participant_count}
📊 <b>Status:</b> {tournament['status'].upper()}

⚡ Limited slots! Join fast!"""
    
    def format_detailed_tournament_info(self, tournament: Dict[str, Any]) -> str:
        """Format detailed tournament information"""
        base_info = self.format_tournament_info(tournament)
        
        additional_info = f"""

📋 <b>Additional Information:</b>
• Room details will be shared 15 minutes before start
• Screenshots required for verification
• No late entries allowed
• Follow all tournament rules

💳 <b>Payment Info:</b>
• UPI ID: {tournament.get('upi_id', 'N/A')}
• Send screenshot to admin after payment
• Use /paid command with UTR number

⚠️ <b>Important:</b>
• Stable internet connection required
• Device should be fully charged
• Keep bot chat open for updates"""
        
        return base_info + additional_info
    
    def _format_prize_info(self, tournament: Dict[str, Any]) -> str:
        """Format prize information based on tournament type"""
        prize_details = tournament.get('prize_details', {})
        prize_type = tournament.get('prize_type', 'fixed')
        
        if prize_type == 'kill_based':
            return f"""Prize Pool: 💀 Kill-Based
• ₹{prize_details.get('per_kill', 0)} per kill
• Top killer bonus: ₹{prize_details.get('top_killer_bonus', 0)}"""
        
        elif prize_type == 'rank_based':
            return f"""Prize Pool: 🏆 Rank-Based
• #1: ₹{prize_details.get('first', 0)}
• #2: ₹{prize_details.get('second', 0)}
• #3: ₹{prize_details.get('third', 0)}"""
        
        elif prize_type == 'fixed':
            return f"""Prize Pool: 💰 Fixed Amount
• Winners take all: ₹{prize_details.get('winners_amount', 0)}"""
        
        return "Prize Pool: TBD"
    
    def format_solo_winner(self, tournament_name: str, username: str, kills: str, damage: str) -> str:
        """Format solo winner announcement"""
        victory_number = random.choice(self.victory_numbers)
        hashtag = random.choice(self.hashtags)
        
        winner_msg = f"""🎮 <b>{tournament_name}</b>
🎯 Player: {username}
💀 Kills: {kills} | 🎯 Damage: {damage}
👑 Victory: {victory_number} (3D animated style)

{hashtag} #LobbyCleaner"""
        
        return winner_msg
    
    def format_duo_winner(self, tournament_name: str, player1: str, player2: str, total_kills: str, damage: str) -> str:
        """Format duo winner announcement"""
        victory_number = random.choice(self.victory_numbers)
        hashtag = random.choice(self.hashtags)
        
        winner_msg = f"""🎮 <b>{tournament_name}</b>
🎯 Players: {player1} & {player2}
💀 Kills: {total_kills} | 💣 Damage: {damage}
👑 Victory Rank: {victory_number} (3D animated)

{hashtag} #KhatarnakJodi"""
        
        return winner_msg
    
    def format_squad_winner(self, tournament_name: str, squad_name: str, players: List[str], total_kills: str, damage: str) -> str:
        """Format squad winner announcement"""
        victory_number = random.choice(self.victory_numbers)
        hashtag = random.choice(self.hashtags)
        players_str = " ".join(players)
        
        winner_msg = f"""🎮 <b>{tournament_name}</b>
🧨 Winning Squad: {squad_name}
🎯 Players: {players_str}
💀 Total Kills: {total_kills} | 💣 Damage: {damage}
🚁 Victory: {victory_number} (3D animated)

{hashtag} #SquadGoals"""
        
        return winner_msg
    
    def generate_motivational_message(self) -> str:
        """Generate random motivational gaming message"""
        messages = [
            "🔥 Aag laga di bhai! Kill machine activated! 💀",
            "⚡ Speed se khel, smart se jeet! Victory incoming! 👑",
            "🎯 Headshot ki baarish hone wali hai! Ready ho jao! 💥",
            "🚀 Squad assemble! Time to dominate the battlefield! 🏆",
            "💀 Enemies ki khair nahi! Destruction mode ON! 🔥",
            "🎮 Game face on! Victory ya kuch nahi! 👊",
            "⚔️ Weapons ready, strategy set! Let's conquer! 🛡️",
            "🔥 Fire in the hole! Championship loading... 🏅"
        ]
        return random.choice(messages)
    
    def format_room_announcement(self, tournament: Dict[str, Any], room_id: str, password: str) -> str:
        """Format room details announcement"""
        return f"""🎮 <b>ROOM DETAILS - {tournament['name']}</b>

🆔 <b>Room ID:</b> <code>{room_id}</code>
🔑 <b>Password:</b> <code>{password}</code>
📍 <b>Map:</b> {tournament['map']}
🕘 <b>Time:</b> {tournament['time']}

⚠️ <b>IMPORTANT:</b>
• Join exactly at {tournament['time']}
• No late entries allowed
• Screenshot your gameplay
• Follow all rules strictly

🏆 Good luck warriors! May the best player win! 💀

{self.generate_motivational_message()}"""
    
    def format_winner_celebration(self, winner_type: str, details: str) -> str:
        """Format winner celebration message"""
        celebrations = [
            "🎉 WHAT A PERFORMANCE! 🎉",
            "🔥 ABSOLUTELY DESTROYED! 🔥",
            "👑 CROWNED THE CHAMPION! 👑",
            "💥 LEGENDARY GAMEPLAY! 💥",
            "🏆 VICTORY ACHIEVED! 🏆"
        ]
        
        celebration = random.choice(celebrations)
        
        return f"""{celebration}

{details}

🌟 Outstanding performance!
📈 Skills level: LEGENDARY!
🎯 Precision: PERFECT!
💀 Enemies eliminated: COUNTLESS!

Keep dominating the battlefield! 🚀

#Champion #Winner #DumWalaSquad"""
    
    def format_payment_reminder(self, amount: int, upi_id: str) -> str:
        """Format payment reminder message"""
        return f"""💰 <b>PAYMENT REMINDER</b>

Amount: ₹{amount}
UPI ID: <code>{upi_id}</code>

📝 <b>Quick Payment Steps:</b>
1. Open any UPI app
2. Pay ₹{amount} to above UPI ID
3. Take screenshot
4. Send to admin
5. Use /paid command with UTR

⏰ <b>Hurry up!</b> Limited slots available!
🎮 Secure your spot now!"""
    
    def format_error_message(self, error_type: str, context: str = "") -> str:
        """Format error messages"""
        error_messages = {
            "not_found": "❌ Item not found! Please check and try again.",
            "permission_denied": "🚫 Access denied! You don't have permission for this action.",
            "invalid_input": "⚠️ Invalid input! Please check the format and try again.",
            "server_error": "🔧 Server error! Please try again later or contact support.",
            "payment_error": "💳 Payment processing error! Contact admin for assistance.",
            "tournament_full": "🎮 Tournament is full! Check for other available tournaments."
        }
        
        base_message = error_messages.get(error_type, "❌ Something went wrong!")
        
        if context:
            return f"{base_message}\n\nContext: {context}"
        
        return base_message
    
    def format_success_message(self, action: str, details: str = "") -> str:
        """Format success messages"""
        success_messages = {
            "joined": "🎉 Successfully joined! Get ready to dominate! 🔥",
            "payment": "✅ Payment verified! You're all set for tournaments! 💰",
            "created": "🎯 Created successfully! Ready for action! ⚡",
            "updated": "📝 Updated successfully! Changes applied! ✨",
            "confirmed": "✅ Confirmed! Everything looks good! 👍"
        }
        
        base_message = success_messages.get(action, "✅ Success!")
        
        if details:
            return f"{base_message}\n\n{details}"
        
        return base_message
