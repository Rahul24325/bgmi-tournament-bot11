"""
Helper utilities for BGMI Tournament Bot
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

config = Config()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.ADMIN_ID

def generate_referral_code(user_id: int) -> str:
    """Generate referral code for user"""
    return f"REF{user_id}"

def generate_tournament_id() -> str:
    """Generate unique tournament ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TOUR_{timestamp}_{random_suffix}"

def generate_room_credentials() -> Dict[str, str]:
    """Generate random room ID and password"""
    room_id = ''.join(random.choices(string.digits, k=6))
    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    return {
        "room_id": room_id,
        "password": password
    }

def validate_utr_number(utr: str) -> bool:
    """Validate UTR number format"""
    if not utr.isdigit():
        return False
    
    if len(utr) < 10 or len(utr) > 16:
        return False
    
    return True

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f"₹{amount:,.2f}"

def calculate_time_difference(target_time: datetime) -> str:
    """Calculate time difference and return human readable format"""
    now = datetime.utcnow()
    diff = target_time - now
    
    if diff.total_seconds() < 0:
        return "Already started"
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def parse_date_time(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse date and time strings into datetime object"""
    try:
        # Assuming date format: DD/MM/YYYY and time format: HH:MM
        date_time_str = f"{date_str} {time_str}"
        return datetime.strptime(date_time_str, "%d/%m/%Y %H:%M")
    except ValueError as e:
        logger.error(f"Failed to parse datetime: {e}")
        return None

def get_tournament_status(tournament: Dict[str, Any]) -> str:
    """Determine tournament status based on current time"""
    tournament_datetime = parse_date_time(
        tournament.get('date', ''),
        tournament.get('time', '')
    )
    
    if not tournament_datetime:
        return "unknown"
    
    now = datetime.utcnow()
    
    if tournament_datetime > now:
        return "upcoming"
    elif tournament_datetime <= now < tournament_datetime + timedelta(hours=2):
        return "live"
    else:
        return "completed"

def sanitize_username(username: str) -> str:
    """Sanitize username for display"""
    if not username:
        return "Unknown"
    
    # Remove @ if present
    username = username.replace('@', '')
    
    # Limit length
    if len(username) > 20:
        username = username[:20] + "..."
    
    return username

def generate_share_link(referral_code: str) -> str:
    """Generate sharing link with referral code"""
    bot_username = "KyaTereSquadMeinDumHaiBot"  # Replace with actual bot username
    return f"https://t.me/{bot_username}?start={referral_code}"

def format_participant_list(participants: List[int], users_data: Dict[int, Dict]) -> str:
    """Format participant list for display"""
    if not participants:
        return "No participants yet!"
    
    formatted_list = ""
    for i, participant_id in enumerate(participants, 1):
        user_data = users_data.get(participant_id, {})
        username = sanitize_username(user_data.get('username', ''))
        status = "✅" if user_data.get('confirmed') else "⏳"
        formatted_list += f"{i}. @{username} {status}\n"
    
    return formatted_list

def calculate_prize_distribution(tournament: Dict[str, Any], participants_count: int) -> Dict[str, Any]:
    """Calculate prize distribution based on tournament type"""
    prize_details = tournament.get('prize_details', {})
    prize_type = tournament.get('prize_type', 'fixed')
    
    if prize_type == 'kill_based':
        per_kill = prize_details.get('per_kill', 0)
        bonus = prize_details.get('top_killer_bonus', 0)
        estimated_total_kills = participants_count * 3  # Average kills
        
        return {
            "type": "kill_based",
            "per_kill_reward": per_kill,
            "top_killer_bonus": bonus,
            "estimated_total": (estimated_total_kills * per_kill) + bonus
        }
    
    elif prize_type == 'rank_based':
        return {
            "type": "rank_based",
            "first_place": prize_details.get('first', 0),
            "second_place": prize_details.get('second', 0),
            "third_place": prize_details.get('third', 0),
            "total": sum([
                prize_details.get('first', 0),
                prize_details.get('second', 0),
                prize_details.get('third', 0)
            ])
        }
    
    elif prize_type == 'fixed':
        return {
            "type": "fixed",
            "winner_amount": prize_details.get('winners_amount', 0),
            "total": prize_details.get('winners_amount', 0)
        }
    
    return {"type": "unknown", "total": 0}

def get_gaming_emoji_sequence() -> str:
    """Get random gaming emoji sequence"""
    sequences = [
        "🎮🔥💀👑",
        "⚡🎯💥🏆",
        "🚀💣⚔️🛡️",
        "👾🎲🎪🎨",
        "🌟⭐✨💫",
        "💀👻🔥💥",
        "🎯🎪🎨🎭",
        "🚀🛸⚡💥"
    ]
    return random.choice(sequences)

def create_tournament_hashtags(tournament_type: str) -> List[str]:
    """Create relevant hashtags for tournament"""
    base_tags = ["#DumWalaSquad", "#BGMITournament", "#GamingCommunity"]
    
    type_specific_tags = {
        "solo": ["#SoloWarrior", "#LobbyCleaner", "#OneManArmy"],
        "duo": ["#DuoPartners", "#TeamWork", "#KhatarnakJodi"],
        "squad": ["#SquadGoals", "#TeamSpirit", "#SquadDomination"]
    }
    
    return base_tags + type_specific_tags.get(tournament_type, [])

def validate_tournament_data(tournament_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tournament data and return validation result"""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['name', 'type', 'date', 'time', 'entry_fee']
    for field in required_fields:
        if not tournament_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate tournament type
    valid_types = ['solo', 'duo', 'squad']
    if tournament_data.get('type') not in valid_types:
        errors.append(f"Invalid tournament type. Must be one of: {valid_types}")
    
    # Validate entry fee
    entry_fee = tournament_data.get('entry_fee')
    if entry_fee is not None:
        if not isinstance(entry_fee, (int, float)) or entry_fee < 0:
            errors.append("Entry fee must be a positive number")
        elif entry_fee < 10:
            warnings.append("Entry fee is very low")
        elif entry_fee > 1000:
            warnings.append("Entry fee is quite high")
    
    # Validate date format
    date_str = tournament_data.get('date')
    time_str = tournament_data.get('time')
    if date_str and time_str:
        tournament_datetime = parse_date_time(date_str, time_str)
        if not tournament_datetime:
            errors.append("Invalid date/time format")
        elif tournament_datetime <= datetime.utcnow():
            errors.append("Tournament time must be in the future")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def create_backup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create backup data with timestamp"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
        "backup_type": "automated"
    }

def log_user_action(user_id: int, action: str, details: str = ""):
    """Log user action for analytics"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details
    }
    
    logger.info(f"User Action: {log_entry}")

def generate_qr_payment_data(amount: int, upi_id: str, name: str = "Tournament Entry") -> str:
    """Generate UPI payment QR code data"""
    return f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR&tn=Tournament%20Entry%20Fee"

def format_leaderboard(participants_data: List[Dict[str, Any]]) -> str:
    """Format leaderboard display"""
    if not participants_data:
        return "No data available for leaderboard."
    
    # Sort by some criteria (kills, points, etc.)
    sorted_participants = sorted(
        participants_data, 
        key=lambda x: x.get('kills', 0), 
        reverse=True
    )
    
    leaderboard = "🏆 **LEADERBOARD** 🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, participant in enumerate(sorted_participants[:10]):  # Top 10
        medal = medals[i] if i < 3 else f"{i+1}."
        username = sanitize_username(participant.get('username', 'Unknown'))
        kills = participant.get('kills', 0)
        
        leaderboard += f"{medal} @{username} - {kills} kills\n"
    
    return leaderboard
