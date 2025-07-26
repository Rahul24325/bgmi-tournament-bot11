"""
Database operations for BGMI Tournament Bot using MongoDB
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database operations"""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.config.MONGODB_URI)
            self.db = self.client[self.config.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("referral_code", unique=True)
            await self.db.users.create_index("username")
            
            # Tournaments collection indexes
            await self.db.tournaments.create_index("tournament_id", unique=True)
            await self.db.tournaments.create_index("date")
            await self.db.tournaments.create_index("status")
            
            # Payments collection indexes
            await self.db.payments.create_index("user_id")
            await self.db.payments.create_index("utr_number", unique=True)
            await self.db.payments.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            await self.db.users.insert_one(user_data)
            logger.info(f"User created: {user_data['user_id']}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"User already exists: {user_data['user_id']}")
            return False
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        try:
            user = await self.db.users.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    async def get_user_by_referral_code(self, referral_code: str) -> Optional[Dict[str, Any]]:
        """Get user by referral code"""
        try:
            user = await self.db.users.find_one({"referral_code": referral_code})
            return user
        except Exception as e:
            logger.error(f"Failed to get user by referral code {referral_code}: {e}")
            return None
    
    # Tournament operations
    async def create_tournament(self, tournament_data: Dict[str, Any]) -> bool:
        """Create a new tournament"""
        try:
            tournament_data['created_at'] = datetime.utcnow()
            tournament_data['updated_at'] = datetime.utcnow()
            tournament_data['participants'] = []
            tournament_data['status'] = 'upcoming'
            
            await self.db.tournaments.insert_one(tournament_data)
            logger.info(f"Tournament created: {tournament_data['tournament_id']}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"Tournament already exists: {tournament_data['tournament_id']}")
            return False
        except Exception as e:
            logger.error(f"Failed to create tournament: {e}")
            return False
    
    async def get_tournament(self, tournament_id: str) -> Optional[Dict[str, Any]]:
        """Get tournament by ID"""
        try:
            tournament = await self.db.tournaments.find_one({"tournament_id": tournament_id})
            return tournament
        except Exception as e:
            logger.error(f"Failed to get tournament {tournament_id}: {e}")
            return None
    
    async def get_active_tournaments(self) -> List[Dict[str, Any]]:
        """Get all active tournaments"""
        try:
            tournaments = await self.db.tournaments.find({
                "status": {"$in": ["upcoming", "live"]}
            }).to_list(length=None)
            return tournaments
        except Exception as e:
            logger.error(f"Failed to get active tournaments: {e}")
            return []
    
    async def add_participant_to_tournament(self, tournament_id: str, user_id: int) -> bool:
        """Add participant to tournament"""
        try:
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$addToSet": {"participants": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add participant to tournament: {e}")
            return False
    
    async def update_tournament(self, tournament_id: str, update_data: Dict[str, Any]) -> bool:
        """Update tournament data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update tournament {tournament_id}: {e}")
            return False
    
    # Payment operations
    async def create_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Create a payment record"""
        try:
            payment_data['created_at'] = datetime.utcnow()
            payment_data['status'] = 'pending'
            
            await self.db.payments.insert_one(payment_data)
            logger.info(f"Payment record created for user: {payment_data['user_id']}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"Payment with UTR already exists: {payment_data['utr_number']}")
            return False
        except Exception as e:
            logger.error(f"Failed to create payment record: {e}")
            return False
    
    async def confirm_payment(self, utr_number: str, admin_id: int) -> bool:
        """Confirm a payment"""
        try:
            result = await self.db.payments.update_one(
                {"utr_number": utr_number},
                {"$set": {
                    "status": "confirmed",
                    "confirmed_by": admin_id,
                    "confirmed_at": datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to confirm payment {utr_number}: {e}")
            return False
    
    async def get_payment_by_utr(self, utr_number: str) -> Optional[Dict[str, Any]]:
        """Get payment by UTR number"""
        try:
            payment = await self.db.payments.find_one({"utr_number": utr_number})
            return payment
        except Exception as e:
            logger.error(f"Failed to get payment by UTR {utr_number}: {e}")
            return None
    
    # Financial tracking operations
    async def get_collection_by_period(self, start_date: datetime, end_date: datetime) -> float:
        """Get total collection for a period"""
        try:
            pipeline = [
                {
                    "$match": {
                        "status": "confirmed",
                        "confirmed_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            result = await self.db.payments.aggregate(pipeline).to_list(length=1)
            if result:
                return float(result[0]['total'])
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get collection for period: {e}")
            return 0.0
    
    async def get_today_collection(self) -> float:
        """Get today's collection"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        return await self.get_collection_by_period(today, tomorrow)
    
    async def get_weekly_collection(self) -> float:
        """Get this week's collection"""
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        return await self.get_collection_by_period(start_of_week, today)
    
    async def get_monthly_collection(self) -> float:
        """Get this month's collection"""
        today = datetime.utcnow()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return await self.get_collection_by_period(start_of_month, today)
    
    # Referral operations
    async def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Add a referral record"""
        try:
            referral_data = {
                "referrer_id": referrer_id,
                "referred_id": referred_id,
                "created_at": datetime.utcnow(),
                "reward_given": False
            }
            
            await self.db.referrals.insert_one(referral_data)
            logger.info(f"Referral added: {referrer_id} -> {referred_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add referral: {e}")
            return False
    
    async def get_user_referrals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all referrals made by a user"""
        try:
            referrals = await self.db.referrals.find({"referrer_id": user_id}).to_list(length=None)
            return referrals
        except Exception as e:
            logger.error(f"Failed to get referrals for user {user_id}: {e}")
            return []
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
