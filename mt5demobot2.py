import MetaTrader5 as mt5

# Connect to the MT5 platform
mt5.initialize()

# Define the function to copy a trade signal
def copy_trade_signal(trade_signal, max_risk=0.003):
    # Parse the trade signal
    parts = trade_signal.split('\n')
    symbol = parts[0].split()[0]
    action = parts[0].split()[1]
    price = float(parts[0].split()[3])
    stop_loss = float(parts[1].split()[1])
    take_profit = float(parts[2].split()[1])
    
    # Get the current account balance
    account_info = mt5.account_info()
    balance = account_info.balance
    
    # Calculate the lot size based on the max risk per trade
    lot_size = round((balance * max_risk) / abs(price - stop_loss), 2)
    
    # Execute the trade on the MT5 platform
    order = mt5.orders_send(
        symbol=symbol,
        action=mt5.TRADE_ACTION_DEAL,
        type=mt5.ORDER_TYPE_LIMIT,
        volume=lot_size,
        price=price,
        deviation=10,
        sl=stop_loss,
        tp=take_profit
    )
    
    # Check if the order was executed successfully
    if order.retcode == mt5.TRADE_RETCODE_DONE:
        print("Trade executed successfully!")
    else:
        print("Failed to execute trade: ", order.comment)

# Define the function to listen for trade signals from Telegram
def telegram_listener(bot_token, channel_name):
    import telegram
    from telegram.ext import Updater, CommandHandler
    
    # Define the function to handle the /start command
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Listening for trade signals...")

    # Define the function to handle incoming messages
    def handle_message(update, context):
        text = update.message.text
        chat_id = update.effective_chat.id
        
        # Check if the message is a valid trade signal
        if len(text.split('\n')) == 3 and 'buy' in text.lower() or 'sell' in text.lower():
            # Copy the trade signal to the MT5 platform
            copy_trade_signal(text, max_risk=0.003)
            
            # Send a confirmation message to Telegram
            context.bot.send_message(chat_id=chat_id, text="Trade signal copied!")
        else:
            # Send an error message to Telegram
            context.bot.send_message(chat_id=chat_id, text="Invalid trade signal.")

    # Set up the Telegram bot and start listening for messages
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(None, handle_message))
    updater.start_polling()
    updater.idle()

# Run the Telegram listener
telegram_listener(bot_token='YOUR_BOT_TOKEN_HERE', channel_name='YOUR_CHANNEL_NAME_HERE')
