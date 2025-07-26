"""
Payment-related handlers for BGMI Tournament Bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config
import logging

logger = logging.getLogger(__name__)

class PaymentHandlers:
    """Handle payment-related operations"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
    
    async def paid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /paid command"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "💰 **PAYMENT VERIFICATION**\n\n"
                "Usage: `/paid <UTR_NUMBER>`\n\n"
                "Example: `/paid 123456789012`\n\n"
                "⚠️ **Steps before using this command:**\n"
                f"1. Pay entry fee to: `{self.config.UPI_ID}`\n"
                f"2. Send payment screenshot to {self.config.ADMIN_USERNAME}\n"
                "3. Use this command with your UTR number\n"
                "4. Wait for admin confirmation\n\n"
                "Need help? Contact support!",
                parse_mode='Markdown'
            )
            return
        
        utr_number = context.args[0]
        user = update.effective_user
        
        # Validate UTR number format (basic validation)
        if not utr_number.isdigit() or len(utr_number) < 10:
            await update.message.reply_text(
                "❌ **Invalid UTR Number!**\n\n"
                "UTR number should be at least 10 digits.\n"
                "Please check and try again.\n\n"
                "Format: `/paid 123456789012`",
                parse_mode='Markdown'
            )
            return
        
        # Check if UTR already exists
        existing_payment = await self.db.get_payment_by_utr(utr_number)
        if existing_payment:
            await update.message.reply_text(
                "⚠️ **UTR Already Used!**\n\n"
                "This UTR number has already been submitted.\n"
                "If this is an error, contact admin.\n\n"
                f"Support: {self.config.ADMIN_USERNAME}",
                parse_mode='Markdown'
            )
            return
        
        # Get user data
        user_data = await self.db.get_user(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ **User not found!**\n\n"
                "Please start the bot first with /start"
            )
            return
        
        # Create payment record
        payment_data = {
            "user_id": user.id,
            "username": user.username or "",
            "utr_number": utr_number,
            "amount": self.config.DEFAULT_ENTRY_FEE,  # Default amount
            "status": "pending"
        }
        
        success = await self.db.create_payment(payment_data)
        
        if success:
            # Update user payment status
            await self.db.update_user(user.id, {"paid": True})
            
            confirmation_msg = f"""✅ **PAYMENT SUBMITTED SUCCESSFULLY!**

👤 **User:** @{user.username or 'N/A'}
🆔 **UTR Number:** `{utr_number}`
💰 **Amount:** ₹{self.config.DEFAULT_ENTRY_FEE}
📊 **Status:** Pending Admin Verification

⏳ **Next Steps:**
• Admin will verify your payment
• You'll get confirmation message once approved
• After confirmation, you can join tournaments

⚠️ **Important:**
• Make sure you sent screenshot to {self.config.ADMIN_USERNAME}
• Verification usually takes 5-10 minutes
• Keep this chat open for updates

Contact support if no response in 30 minutes.
Support: {self.config.ADMIN_USERNAME}

#PaymentSubmitted #DumWalaSquad"""

            keyboard = [
                [InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{self.config.ADMIN_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirmation_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Notify admin about new payment
            admin_notification = f"""💰 **NEW PAYMENT SUBMISSION**

👤 **User:** @{user.username or 'N/A'} ({user.id})
🆔 **UTR:** {utr_number}
💰 **Amount:** ₹{self.config.DEFAULT_ENTRY_FEE}
⏰ **Time:** {payment_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}

Use `/confirm {user.username or user.id}` to approve this payment."""
            
            try:
                await context.bot.send_message(
                    chat_id=self.config.ADMIN_ID,
                    text=admin_notification,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify admin: {e}")
            
            logger.info(f"Payment submitted by user {user.id} with UTR {utr_number}")
        else:
            await update.message.reply_text(
                "❌ **Payment submission failed!**\n\n"
                "Please try again or contact support.\n\n"
                f"Support: {self.config.ADMIN_USERNAME}"
            )
    
    async def handle_payment_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment screenshot uploads"""
        user = update.effective_user
        
        # Check if user has sent to admin
        if update.message.chat.type == 'private':
            screenshot_msg = f"""📸 **PAYMENT SCREENSHOT RECEIVED!**

Thank you for sending the payment screenshot!

📝 **Next Steps:**
1. Forward this screenshot to {self.config.ADMIN_USERNAME}
2. Use `/paid <UTR_NUMBER>` command with your transaction UTR
3. Wait for admin confirmation

💡 **UTR Number Location:**
• Check your payment app transaction history
• UTR is usually 12 digits long
• It's also called Reference Number in some apps

⚠️ **Important:**
• Screenshot must be sent to {self.config.ADMIN_USERNAME} first
• Then use /paid command with UTR number
• Both steps are mandatory for verification

Need help finding UTR? Contact {self.config.ADMIN_USERNAME}"""

            keyboard = [
                [InlineKeyboardButton("💬 Send to Admin", url=f"https://t.me/{self.config.ADMIN_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("💰 Submit UTR", callback_data="submit_utr")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                screenshot_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def payment_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment status for user"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = await self.db.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text(
                "❌ User data not found! Please start the bot with /start"
            )
            return
        
        # Get user's payment history
        payments = await self.db.payments.find({"user_id": user_id}).to_list(length=None)
        
        status_msg = f"""💰 **PAYMENT STATUS**

👤 **User:** @{user_data.get('username', 'N/A')}
💳 **Payment Status:** {'✅ Confirmed' if user_data.get('confirmed') else '⏳ Pending'}
💰 **Balance:** ₹{user_data.get('balance', 0)}

📊 **Payment History:**"""

        if payments:
            for payment in payments[-5:]:  # Last 5 payments
                status_icon = "✅" if payment['status'] == "confirmed" else "⏳"
                date = payment['created_at'].strftime('%d/%m/%Y')
                status_msg += f"\n{status_icon} ₹{payment['amount']} - {date} - UTR: {payment['utr_number'][-4:]}"
        else:
            status_msg += "\nNo payment history found."
        
        status_msg += f"""

💡 **Payment Process:**
1. Pay to UPI: `{self.config.UPI_ID}`
2. Send screenshot to {self.config.ADMIN_USERNAME}
3. Use /paid command with UTR
4. Wait for confirmation

Need help? Contact {self.config.ADMIN_USERNAME}"""

        keyboard = [
            [InlineKeyboardButton("💸 Make Payment", callback_data="make_payment")],
            [InlineKeyboardButton("💰 Submit UTR", callback_data="submit_utr")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def make_payment_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment information"""
        query = update.callback_query
        await query.answer()
        
        payment_info = f"""💸 **MAKE PAYMENT**

🏦 **Payment Details:**
• UPI ID: `{self.config.UPI_ID}`
• Amount: ₹{self.config.DEFAULT_ENTRY_FEE}
• Account Name: Tournament Entry

📱 **Supported Payment Apps:**
• Google Pay
• PhonePe
• Paytm
• BHIM UPI
• Any UPI app

📝 **Payment Steps:**
1. Open your UPI app
2. Send ₹{self.config.DEFAULT_ENTRY_FEE} to `{self.config.UPI_ID}`
3. Take screenshot of payment
4. Send screenshot to {self.config.ADMIN_USERNAME}
5. Use /paid command with UTR number

⚠️ **Important Notes:**
• Payment must be exactly ₹{self.config.DEFAULT_ENTRY_FEE}
• Keep screenshot for verification
• UTR number is mandatory
• No refunds after room details shared

Need help? Contact {self.config.ADMIN_USERNAME}"""

        keyboard = [
            [InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{self.config.ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("💰 I've Paid", callback_data="submit_utr")],
            [InlineKeyboardButton("🔙 Back", callback_data="payment_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            payment_info,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def submit_utr_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prompt user to submit UTR"""
        query = update.callback_query
        await query.answer()
        
        utr_prompt = f"""💰 **SUBMIT UTR NUMBER**

After making payment, use this command:

`/paid YOUR_UTR_NUMBER`

**Example:** `/paid 123456789012`

🔍 **How to find UTR:**
• Open your payment app
• Go to transaction history
• Find your recent payment
• UTR/Reference number is usually 12 digits

⚠️ **Before submitting UTR:**
✅ Payment made to `{self.config.UPI_ID}`
✅ Screenshot sent to {self.config.ADMIN_USERNAME}
✅ UTR number copied correctly

📞 **Need Help?**
Contact {self.config.ADMIN_USERNAME} if you can't find UTR number."""

        keyboard = [
            [InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{self.config.ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔙 Back", callback_data="payment_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            utr_prompt,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
