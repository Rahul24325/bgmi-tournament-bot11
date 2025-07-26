#!/usr/bin/env python3
"""
BGMI Tournament Management Bot - Main Entry Point
Bot Name: Kya Tere Squad Mein Dum Hai?
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import Config
from database import Database
from handlers.user_handlers import UserHandlers
from handlers.admin_handlers import AdminHandlers
from handlers.tournament_handlers import TournamentHandlers
from handlers.payment_handlers import PaymentHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BGMITournamentBot:
    def __init__(self):
        self.config = Config()
        self.database = Database()
        self.user_handlers = UserHandlers(self.database)
        self.admin_handlers = AdminHandlers(self.database)
        self.tournament_handlers = TournamentHandlers(self.database)
        self.payment_handlers = PaymentHandlers(self.database)

    async def setup_handlers(self, application):
        """Setup all bot handlers"""
        
        # User command handlers
        application.add_handler(CommandHandler("start", self.user_handlers.start_command))
        application.add_handler(CommandHandler("help", self.user_handlers.help_command))
        application.add_handler(CommandHandler("referrals", self.user_handlers.referrals_command))
        application.add_handler(CommandHandler("matchhistory", self.user_handlers.match_history_command))
        application.add_handler(CommandHandler("paid", self.payment_handlers.paid_command))
        
        # Admin command handlers (restricted to admin users)
        application.add_handler(CommandHandler("createtournament", self.admin_handlers.create_tournament_command))
        application.add_handler(CommandHandler("createtournamentsolo", self.admin_handlers.create_tournament_solo))
        application.add_handler(CommandHandler("createtournamentduo", self.admin_handlers.create_tournament_duo))
        application.add_handler(CommandHandler("createtournamentsquad", self.admin_handlers.create_tournament_squad))
        application.add_handler(CommandHandler("sendroom", self.admin_handlers.send_room_command))
        application.add_handler(CommandHandler("confirm", self.admin_handlers.confirm_payment_command))
        application.add_handler(CommandHandler("listplayers", self.admin_handlers.list_players_command))
        application.add_handler(CommandHandler("declarewinners", self.admin_handlers.declare_winners_command))
        application.add_handler(CommandHandler("clear", self.admin_handlers.clear_entries_command))
        application.add_handler(CommandHandler("today", self.admin_handlers.today_collection_command))
        application.add_handler(CommandHandler("thisweek", self.admin_handlers.weekly_collection_command))
        application.add_handler(CommandHandler("thismonth", self.admin_handlers.monthly_collection_command))
        application.add_handler(CommandHandler("solo", self.admin_handlers.declare_solo_winner))
        application.add_handler(CommandHandler("duo", self.admin_handlers.declare_duo_winner))
        application.add_handler(CommandHandler("squad", self.admin_handlers.declare_squad_winner))
        application.add_handler(CommandHandler("special", self.admin_handlers.special_notification))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(self.user_handlers.check_membership, pattern="check_membership"))
        application.add_handler(CallbackQueryHandler(self.tournament_handlers.join_tournament, pattern="join_tournament_"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.show_terms, pattern="show_terms"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.show_disclaimer, pattern="show_disclaimer"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.invite_friends, pattern="invite_friends"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.share_whatsapp, pattern="share_whatsapp"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.active_tournament, pattern="active_tournament"))
        application.add_handler(CallbackQueryHandler(self.user_handlers.back_to_menu, pattern="back_to_menu"))
        
        # Admin callback handlers for tournament creation
        application.add_handler(CallbackQueryHandler(self.admin_handlers.create_tournament_solo_callback, pattern="create_solo"))
        application.add_handler(CallbackQueryHandler(self.admin_handlers.create_tournament_duo_callback, pattern="create_duo"))
        application.add_handler(CallbackQueryHandler(self.admin_handlers.create_tournament_squad_callback, pattern="create_squad"))
        
        # Admin callback handlers for winner declaration
        application.add_handler(CallbackQueryHandler(self.admin_handlers.declare_solo_winner_callback, pattern="declare_solo"))
        application.add_handler(CallbackQueryHandler(self.admin_handlers.declare_duo_winner_callback, pattern="declare_duo"))
        application.add_handler(CallbackQueryHandler(self.admin_handlers.declare_squad_winner_callback, pattern="declare_squad"))
        
        # Message handlers for payment screenshots
        application.add_handler(MessageHandler(filters.PHOTO, self.payment_handlers.handle_payment_screenshot))
        
        logger.info("All handlers setup completed")

    async def initialize(self):
        """Initialize the bot"""
        await self.database.connect()
        logger.info("Database connected successfully")
        
        # Create application
        self.application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Initialize the application properly
        await self.application.initialize()
        
        # Setup handlers
        await self.setup_handlers(self.application)
        logger.info("All handlers setup completed")

async def main():
    """Main entry point"""
    bot = BGMITournamentBot()
    await bot.initialize()
    
    logger.info("Starting BGMI Tournament Bot...")
    await bot.application.start()
    await bot.application.updater.start_polling(allowed_updates=["message", "callback_query"])
    
    # Keep the bot running indefinitely
    try:
        import signal
        import asyncio
        
        stop_event = asyncio.Event()
        
        def signal_handler():
            stop_event.set()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: signal_handler())
        
        await stop_event.wait()
    finally:
        await bot.application.stop()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
