"""
User model for BGMI Tournament Bot
Defines user data structure and validation methods
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User model class"""
    user_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    paid: bool = False
    confirmed: bool = False
    balance: float = 0.0
    referral_code: str = ""
    referred_by: Optional[str] = None
    total_tournaments: int = 0
    total_wins: int = 0
    total_kills: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_banned: bool = False
    ban_reason: str = ""
    referral_count: int = 0
    total_earnings: float = 0.0
    payment_history: List[str] = field(default_factory=list)
    tournament_history: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for MongoDB storage"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "paid": self.paid,
            "confirmed": self.confirmed,
            "balance": self.balance,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "total_tournaments": self.total_tournaments,
            "total_wins": self.total_wins,
            "total_kills": self.total_kills,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_active": self.last_active,
            "is_banned": self.is_banned,
            "ban_reason": self.ban_reason,
            "referral_count": self.referral_count,
            "total_earnings": self.total_earnings,
            "payment_history": self.payment_history,
            "tournament_history": self.tournament_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user object from dictionary"""
        return cls(
            user_id=data.get('user_id', 0),
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            paid=data.get('paid', False),
            confirmed=data.get('confirmed', False),
            balance=data.get('balance', 0.0),
            referral_code=data.get('referral_code', ''),
            referred_by=data.get('referred_by'),
            total_tournaments=data.get('total_tournaments', 0),
            total_wins=data.get('total_wins', 0),
            total_kills=data.get('total_kills', 0),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            last_active=data.get('last_active', datetime.utcnow()),
            is_banned=data.get('is_banned', False),
            ban_reason=data.get('ban_reason', ''),
            referral_count=data.get('referral_count', 0),
            total_earnings=data.get('total_earnings', 0.0),
            payment_history=data.get('payment_history', []),
            tournament_history=data.get('tournament_history', [])
        )
    
    def validate(self) -> Dict[str, Any]:
        """Validate user data"""
        errors = []
        warnings = []
        
        # Validate user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            errors.append("Invalid user_id: must be a positive integer")
        
        # Validate usernames
        if self.username and len(self.username) > 32:
            warnings.append("Username is very long")
        
        if not self.first_name:
            warnings.append("First name is empty")
        
        # Validate balance
        if self.balance < 0:
            warnings.append("Negative balance detected")
        
        # Validate referral code format
        if self.referral_code and not self.referral_code.startswith('REF'):
            errors.append("Invalid referral code format")
        
        # Validate stats
        if self.total_tournaments < 0:
            errors.append("Total tournaments cannot be negative")
        
        if self.total_wins > self.total_tournaments:
            errors.append("Total wins cannot exceed total tournaments")
        
        if self.total_kills < 0:
            errors.append("Total kills cannot be negative")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name
    
    def get_display_name(self) -> str:
        """Get user's display name (username or first name)"""
        if self.username:
            return f"@{self.username}"
        return self.first_name or f"User{self.user_id}"
    
    def is_eligible_for_tournament(self) -> bool:
        """Check if user is eligible to join tournaments"""
        return (
            not self.is_banned and
            self.paid and
            self.confirmed
        )
    
    def get_win_rate(self) -> float:
        """Calculate user's win rate percentage"""
        if self.total_tournaments == 0:
            return 0.0
        return (self.total_wins / self.total_tournaments) * 100
    
    def get_average_kills(self) -> float:
        """Calculate average kills per tournament"""
        if self.total_tournaments == 0:
            return 0.0
        return self.total_kills / self.total_tournaments
    
    def add_tournament_participation(self, tournament_id: str):
        """Add tournament to user's history"""
        if tournament_id not in self.tournament_history:
            self.tournament_history.append(tournament_id)
            self.total_tournaments += 1
            self.updated_at = datetime.utcnow()
    
    def add_tournament_win(self, tournament_id: str, kills: int = 0, earnings: float = 0.0):
        """Record a tournament win"""
        self.total_wins += 1
        self.total_kills += kills
        self.total_earnings += earnings
        self.balance += earnings
        self.updated_at = datetime.utcnow()
        
        logger.info(f"User {self.user_id} won tournament {tournament_id} with {kills} kills, earned ₹{earnings}")
    
    def add_referral(self):
        """Increment referral count"""
        self.referral_count += 1
        self.updated_at = datetime.utcnow()
        
        logger.info(f"User {self.user_id} referral count increased to {self.referral_count}")
    
    def ban_user(self, reason: str):
        """Ban user with reason"""
        self.is_banned = True
        self.ban_reason = reason
        self.updated_at = datetime.utcnow()
        
        logger.warning(f"User {self.user_id} banned: {reason}")
    
    def unban_user(self):
        """Unban user"""
        self.is_banned = False
        self.ban_reason = ""
        self.updated_at = datetime.utcnow()
        
        logger.info(f"User {self.user_id} unbanned")
    
    def update_activity(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
    
    def confirm_payment(self, amount: float = 0.0):
        """Confirm user payment"""
        self.paid = True
        self.confirmed = True
        if amount > 0:
            self.balance += amount
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Payment confirmed for user {self.user_id}, amount: ₹{amount}")
    
    def deduct_balance(self, amount: float) -> bool:
        """Deduct amount from user balance"""
        if self.balance >= amount:
            self.balance -= amount
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        return {
            "user_id": self.user_id,
            "display_name": self.get_display_name(),
            "total_tournaments": self.total_tournaments,
            "total_wins": self.total_wins,
            "total_kills": self.total_kills,
            "win_rate": round(self.get_win_rate(), 2),
            "average_kills": round(self.get_average_kills(), 2),
            "total_earnings": self.total_earnings,
            "current_balance": self.balance,
            "referral_count": self.referral_count,
            "account_status": "Banned" if self.is_banned else "Active",
            "payment_status": "Confirmed" if self.confirmed else "Pending",
            "member_since": self.created_at.strftime("%B %Y")
        }

class UserValidator:
    """User data validation utilities"""
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate Telegram username format"""
        if not username:
            return True  # Username is optional
        
        # Remove @ if present
        username = username.replace('@', '')
        
        # Check length (5-32 characters for Telegram)
        if len(username) < 5 or len(username) > 32:
            return False
        
        # Check valid characters (alphanumeric and underscores)
        return username.replace('_', '').isalnum()
    
    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        """Validate Telegram user ID"""
        # Telegram user IDs are positive integers
        return isinstance(user_id, int) and user_id > 0
    
    @staticmethod
    def validate_referral_code(code: str) -> bool:
        """Validate referral code format"""
        if not code:
            return False
        
        # Should start with REF followed by user ID
        if not code.startswith('REF'):
            return False
        
        # Extract user ID part
        user_id_part = code[3:]
        return user_id_part.isdigit()
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize user name"""
        if not name:
            return ""
        
        # Remove potentially harmful characters
        import re
        sanitized = re.sub(r'[<>"\']', '', name)
        
        # Limit length
        return sanitized[:50]

class UserPermissions:
    """User permission management"""
    
    ADMIN_PERMISSIONS = [
        'create_tournament',
        'delete_tournament',
        'confirm_payment',
        'ban_user',
        'view_analytics',
        'send_broadcast',
        'manage_prizes'
    ]
    
    USER_PERMISSIONS = [
        'join_tournament',
        'view_profile',
        'refer_friends',
        'submit_payment'
    ]
    
    @classmethod
    def get_user_permissions(cls, user: User, is_admin: bool = False) -> List[str]:
        """Get user permissions based on status"""
        permissions = []
        
        if is_admin:
            permissions.extend(cls.ADMIN_PERMISSIONS)
        
        if not user.is_banned:
            permissions.extend(cls.USER_PERMISSIONS)
        
        return permissions
    
    @classmethod
    def can_user_perform(cls, user: User, action: str, is_admin: bool = False) -> bool:
        """Check if user can perform specific action"""
        user_permissions = cls.get_user_permissions(user, is_admin)
        return action in user_permissions

