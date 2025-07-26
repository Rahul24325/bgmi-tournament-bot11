"""
Tournament model for BGMI Tournament Bot
Defines tournament data structure and management methods
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TournamentType(Enum):
    """Tournament types"""
    SOLO = "solo"
    DUO = "duo"
    SQUAD = "squad"

class TournamentStatus(Enum):
    """Tournament status"""
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PrizeType(Enum):
    """Prize distribution types"""
    KILL_BASED = "kill_based"
    RANK_BASED = "rank_based"
    FIXED = "fixed"

@dataclass
class PrizeStructure:
    """Prize structure data"""
    prize_type: PrizeType
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prize_type": self.prize_type.value,
            "details": self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrizeStructure':
        return cls(
            prize_type=PrizeType(data.get('prize_type', 'fixed')),
            details=data.get('details', {})
        )

@dataclass
class Tournament:
    """Tournament model class"""
    tournament_id: str
    name: str
    tournament_type: TournamentType
    date: str  # DD/MM/YYYY format
    time: str  # HH:MM format
    map: str
    entry_fee: float
    prize_structure: PrizeStructure
    upi_id: str
    room_id: str = ""
    room_password: str = ""
    status: TournamentStatus = TournamentStatus.UPCOMING
    participants: List[int] = field(default_factory=list)
    max_participants: int = 100
    min_participants: int = 10
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: int = 0  # Admin user ID
    description: str = ""
    rules: List[str] = field(default_factory=list)
    winners: List[Dict[str, Any]] = field(default_factory=list)
    total_prize_pool: float = 0.0
    registration_deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tournament object to dictionary for MongoDB storage"""
        return {
            "tournament_id": self.tournament_id,
            "name": self.name,
            "tournament_type": self.tournament_type.value,
            "date": self.date,
            "time": self.time,
            "map": self.map,
            "entry_fee": self.entry_fee,
            "prize_structure": self.prize_structure.to_dict(),
            "upi_id": self.upi_id,
            "room_id": self.room_id,
            "room_password": self.room_password,
            "status": self.status.value,
            "participants": self.participants,
            "max_participants": self.max_participants,
            "min_participants": self.min_participants,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "description": self.description,
            "rules": self.rules,
            "winners": self.winners,
            "total_prize_pool": self.total_prize_pool,
            "registration_deadline": self.registration_deadline
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tournament':
        """Create tournament object from dictionary"""
        prize_structure_data = data.get('prize_structure', {})
        if isinstance(prize_structure_data, dict):
            prize_structure = PrizeStructure.from_dict(prize_structure_data)
        else:
            # Handle legacy format
            prize_structure = PrizeStructure(
                prize_type=PrizeType(data.get('prize_type', 'fixed')),
                details=data.get('prize_details', {})
            )
        
        return cls(
            tournament_id=data.get('tournament_id', ''),
            name=data.get('name', ''),
            tournament_type=TournamentType(data.get('tournament_type', 'solo')),
            date=data.get('date', ''),
            time=data.get('time', ''),
            map=data.get('map', ''),
            entry_fee=data.get('entry_fee', 0.0),
            prize_structure=prize_structure,
            upi_id=data.get('upi_id', ''),
            room_id=data.get('room_id', ''),
            room_password=data.get('room_password', ''),
            status=TournamentStatus(data.get('status', 'upcoming')),
            participants=data.get('participants', []),
            max_participants=data.get('max_participants', 100),
            min_participants=data.get('min_participants', 10),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            created_by=data.get('created_by', 0),
            description=data.get('description', ''),
            rules=data.get('rules', []),
            winners=data.get('winners', []),
            total_prize_pool=data.get('total_prize_pool', 0.0),
            registration_deadline=data.get('registration_deadline')
        )
    
    def validate(self) -> Dict[str, Any]:
        """Validate tournament data"""
        errors = []
        warnings = []
        
        # Validate required fields
        if not self.tournament_id:
            errors.append("Tournament ID is required")
        
        if not self.name:
            errors.append("Tournament name is required")
        
        if not self.date:
            errors.append("Tournament date is required")
        
        if not self.time:
            errors.append("Tournament time is required")
        
        # Validate entry fee
        if self.entry_fee < 0:
            errors.append("Entry fee cannot be negative")
        elif self.entry_fee < 10:
            warnings.append("Entry fee is very low")
        elif self.entry_fee > 1000:
            warnings.append("Entry fee is quite high")
        
        # Validate participant limits
        if self.min_participants <= 0:
            errors.append("Minimum participants must be positive")
        
        if self.max_participants <= self.min_participants:
            errors.append("Maximum participants must be greater than minimum")
        
        if self.max_participants > 500:
            warnings.append("Very large tournament (>500 players)")
        
        # Validate date/time
        tournament_datetime = self.get_datetime()
        if tournament_datetime and tournament_datetime <= datetime.utcnow():
            warnings.append("Tournament time is in the past")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_datetime(self) -> Optional[datetime]:
        """Get tournament datetime object"""
        try:
            date_time_str = f"{self.date} {self.time}"
            return datetime.strptime(date_time_str, "%d/%m/%Y %H:%M")
        except ValueError:
            return None
    
    def add_participant(self, user_id: int) -> bool:
        """Add participant to tournament"""
        if self.is_full():
            return False
        
        if user_id in self.participants:
            return False  # Already registered
        
        if self.status != TournamentStatus.UPCOMING:
            return False  # Registration closed
        
        self.participants.append(user_id)
        self.updated_at = datetime.utcnow()
        
        logger.info(f"User {user_id} added to tournament {self.tournament_id}")
        return True
    
    def remove_participant(self, user_id: int) -> bool:
        """Remove participant from tournament"""
        if user_id not in self.participants:
            return False
        
        if self.status not in [TournamentStatus.UPCOMING, TournamentStatus.LIVE]:
            return False  # Cannot remove after completion
        
        self.participants.remove(user_id)
        self.updated_at = datetime.utcnow()
        
        logger.info(f"User {user_id} removed from tournament {self.tournament_id}")
        return True
    
    def is_full(self) -> bool:
        """Check if tournament is full"""
        return len(self.participants) >= self.max_participants
    
    def is_registration_open(self) -> bool:
        """Check if registration is still open"""
        if self.status != TournamentStatus.UPCOMING:
            return False
        
        if self.is_full():
            return False
        
        if self.registration_deadline:
            return datetime.utcnow() < self.registration_deadline
        
        # Default: registration closes 1 hour before tournament
        tournament_datetime = self.get_datetime()
        if tournament_datetime:
            registration_cutoff = tournament_datetime - timedelta(hours=1)
            return datetime.utcnow() < registration_cutoff
        
        return True
    
    def get_participant_count(self) -> int:
        """Get current participant count"""
        return len(self.participants)
    
    def get_available_slots(self) -> int:
        """Get available slots"""
        return max(0, self.max_participants - self.get_participant_count())
    
    def calculate_total_prize_pool(self) -> float:
        """Calculate total prize pool"""
        participant_count = self.get_participant_count()
        
        if self.prize_structure.prize_type == PrizeType.KILL_BASED:
            details = self.prize_structure.details
            estimated_kills = participant_count * 3  # Average kills estimate
            per_kill = details.get('per_kill', 0)
            bonus = details.get('top_killer_bonus', 0)
            return (estimated_kills * per_kill) + bonus
        
        elif self.prize_structure.prize_type == PrizeType.RANK_BASED:
            details = self.prize_structure.details
            return sum([
                details.get('first', 0),
                details.get('second', 0),
                details.get('third', 0)
            ])
        
        elif self.prize_structure.prize_type == PrizeType.FIXED:
            return self.prize_structure.details.get('winners_amount', 0)
        
        return 0.0
    
    def start_tournament(self, room_id: str, room_password: str) -> bool:
        """Start the tournament"""
        if self.status != TournamentStatus.UPCOMING:
            return False
        
        if self.get_participant_count() < self.min_participants:
            return False
        
        self.room_id = room_id
        self.room_password = room_password
        self.status = TournamentStatus.LIVE
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Tournament {self.tournament_id} started with {self.get_participant_count()} participants")
        return True
    
    def complete_tournament(self, winners: List[Dict[str, Any]]) -> bool:
        """Complete the tournament with winners"""
        if self.status != TournamentStatus.LIVE:
            return False
        
        self.winners = winners
        self.status = TournamentStatus.COMPLETED
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Tournament {self.tournament_id} completed with {len(winners)} winners")
        return True
    
    def cancel_tournament(self, reason: str = "") -> bool:
        """Cancel the tournament"""
        if self.status in [TournamentStatus.COMPLETED, TournamentStatus.CANCELLED]:
            return False
        
        self.status = TournamentStatus.CANCELLED
        self.description = f"Cancelled: {reason}" if reason else "Cancelled"
        self.updated_at = datetime.utcnow()
        
        logger.warning(f"Tournament {self.tournament_id} cancelled: {reason}")
        return True
    
    def get_tournament_info(self) -> Dict[str, Any]:
        """Get comprehensive tournament information"""
        tournament_datetime = self.get_datetime()
        
        return {
            "tournament_id": self.tournament_id,
            "name": self.name,
            "type": self.tournament_type.value,
            "date": self.date,
            "time": self.time,
            "datetime": tournament_datetime,
            "map": self.map,
            "entry_fee": self.entry_fee,
            "prize_structure": self.prize_structure.to_dict(),
            "status": self.status.value,
            "participants": {
                "current": self.get_participant_count(),
                "maximum": self.max_participants,
                "minimum": self.min_participants,
                "available_slots": self.get_available_slots()
            },
            "registration_open": self.is_registration_open(),
            "is_full": self.is_full(),
            "total_prize_pool": self.calculate_total_prize_pool(),
            "created_at": self.created_at,
            "room_details": {
                "room_id": self.room_id,
                "password": self.room_password
            } if self.room_id else None
        }
    
    def get_prize_distribution_text(self) -> str:
        """Get formatted prize distribution text"""
        if self.prize_structure.prize_type == PrizeType.KILL_BASED:
            details = self.prize_structure.details
            return f"💀 Kill-Based: ₹{details.get('per_kill', 0)} per kill + ₹{details.get('top_killer_bonus', 0)} top killer bonus"
        
        elif self.prize_structure.prize_type == PrizeType.RANK_BASED:
            details = self.prize_structure.details
            return f"🏆 Rank-Based: 1st: ₹{details.get('first', 0)}, 2nd: ₹{details.get('second', 0)}, 3rd: ₹{details.get('third', 0)}"
        
        elif self.prize_structure.prize_type == PrizeType.FIXED:
            amount = self.prize_structure.details.get('winners_amount', 0)
            return f"💰 Fixed Prize: ₹{amount} for winners"
        
        return "Prize structure not defined"
    
    def get_time_until_start(self) -> str:
        """Get human-readable time until tournament starts"""
        tournament_datetime = self.get_datetime()
        if not tournament_datetime:
            return "Invalid date/time"
        
        now = datetime.utcnow()
        if tournament_datetime <= now:
            return "Already started"
        
        diff = tournament_datetime - now
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_status_based_on_time(self):
        """Update tournament status based on current time"""
        tournament_datetime = self.get_datetime()
        if not tournament_datetime:
            return
        
        now = datetime.utcnow()
        
        # If tournament time has passed and it's still upcoming, mark as live
        if self.status == TournamentStatus.UPCOMING and tournament_datetime <= now:
            if self.get_participant_count() >= self.min_participants:
                self.status = TournamentStatus.LIVE
            else:
                self.status = TournamentStatus.CANCELLED
                self.description = "Cancelled due to insufficient participants"
        
        # Auto-complete tournaments after 3 hours
        elif self.status == TournamentStatus.LIVE and tournament_datetime + timedelta(hours=3) <= now:
            self.status = TournamentStatus.COMPLETED
        
        self.updated_at = datetime.utcnow()

class TournamentValidator:
    """Tournament data validation utilities"""
    
    VALID_MAPS = [
        "Erangel", "Miramar", "Sanhok", "Vikendi", 
        "Livik", "Karakin", "Paramo", "Taego"
    ]
    
    @staticmethod
    def validate_tournament_name(name: str) -> bool:
        """Validate tournament name"""
        if not name or len(name.strip()) < 3:
            return False
        
        if len(name) > 100:
            return False
        
        # Check for inappropriate content (basic check)
        inappropriate_words = ['hack', 'cheat', 'spam', 'fake']
        name_lower = name.lower()
        
        for word in inappropriate_words:
            if word in name_lower:
                return False
        
        return True
    
    @staticmethod
    def validate_map_name(map_name: str) -> bool:
        """Validate BGMI map name"""
        return map_name in TournamentValidator.VALID_MAPS
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate date format DD/MM/YYYY"""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_entry_fee(fee: float) -> Dict[str, Any]:
        """Validate entry fee amount"""
        errors = []
        warnings = []
        
        if fee < 0:
            errors.append("Entry fee cannot be negative")
        elif fee == 0:
            warnings.append("Free tournament - no entry fee")
        elif fee < 10:
            warnings.append("Very low entry fee")
        elif fee > 1000:
            warnings.append("Very high entry fee")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

class TournamentManager:
    """Tournament management utilities"""
    
    @staticmethod
    def create_default_rules() -> List[str]:
        """Create default tournament rules"""
        return [
            "🚫 No emulators allowed - Only mobile devices",
            "🚫 No teaming/hacking/cheating",
            "🎯 Kill + Rank = Points calculation",
            "⏰ Be punctual - Late entry not allowed",
            "📱 Screenshots required for verification",
            "🎮 Follow room guidelines strictly",
            "💬 Respect other players and admins",
            "🏆 Admin decisions are final"
        ]
    
    @staticmethod
    def generate_tournament_brackets(participants: List[int], tournament_type: TournamentType) -> Dict[str, Any]:
        """Generate tournament brackets based on type"""
        participant_count = len(participants)
        
        if tournament_type == TournamentType.SOLO:
            return {
                "type": "solo",
                "total_players": participant_count,
                "matches": [{"players": participants}]
            }
        
        elif tournament_type == TournamentType.DUO:
            teams = []
            for i in range(0, participant_count, 2):
                if i + 1 < participant_count:
                    teams.append([participants[i], participants[i + 1]])
                else:
                    # Odd player gets a bye or paired with bot
                    teams.append([participants[i]])
            
            return {
                "type": "duo",
                "total_teams": len(teams),
                "teams": teams
            }
        
        elif tournament_type == TournamentType.SQUAD:
            squads = []
            for i in range(0, participant_count, 4):
                squad = participants[i:i + 4]
                squads.append(squad)
            
            return {
                "type": "squad",
                "total_squads": len(squads),
                "squads": squads
            }
        
        return {}
    
    @staticmethod
    def calculate_tournament_revenue(tournament: Tournament) -> Dict[str, float]:
        """Calculate tournament revenue breakdown"""
        participant_count = tournament.get_participant_count()
        total_collection = participant_count * tournament.entry_fee
        total_prize_pool = tournament.calculate_total_prize_pool()
        
        return {
            "total_collection": total_collection,
            "total_prize_pool": total_prize_pool,
            "net_profit": total_collection - total_prize_pool,
            "profit_margin": ((total_collection - total_prize_pool) / total_collection * 100) if total_collection > 0 else 0
        }

