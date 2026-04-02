import os
from telegram import Update
from telegram.ext import ApplicationBuilder,ContextTypes,MessageHandler,filters,CommandHandler
import run_bot
from dotenv import load_dotenv
from memory import extract_memory
import json
load_dotenv()

ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])

async def handle_message(update:Update,context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return
    message = update.message.text
    response = await run_bot.process_message(message)
    await update.message.reply_text(response)

async def stop_command(update:Update,context: ContextTypes.DEFAULT_TYPE):
    run_bot.stop_flag[0]=True
    extract_memory(run_bot.conversation_history) 
    await update.message.reply_text("Stopping.")

async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extract_memory(run_bot.conversation_history)
    await update.message.reply_text(json.dumps(run_bot.conversation_history))
    await update.message.reply_text("Memories saved.")
    

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]                                                                                                             
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  
    app.add_handler(CommandHandler("stop", stop_command)) 
    app.add_handler(CommandHandler("remember",remember_command))                                                                  
    app.run_polling()                                                                                                                                    
                                                                                                                                                           
if __name__ == "__main__":                                                                                                                               
    main()      