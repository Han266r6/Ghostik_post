#!/usr/bin/env python3
"""
Ghost Protocol - 24/7 Telegram MTProxy Channel Poster Bot
Framework: pyTelegramBotAPI (telebot) + Flask (Keep-Alive Server)
Host Target: Render.com / GitHub / VPS
High-End Design Matching Screenshot 2:
  - 16:9 Compact Cinematic Wide Banner
  - Rich Stylized Caption with Ornaments & Hashtags
  - 3-Column Compact "Connect ↗" Buttons Grid
Exclusively authorized for Admin ID: 6640701495
"""

import os
import re
import time
import logging
import threading
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify
import requests

import telebot
from telebot import types

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GhostProtocol")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8643237203:AAF5V_shvCNWoAyKBZkhnE8aOgQVTD8TVV0").strip()
DEFAULT_CHANNEL = "@ghost_protocolI"
CHANNEL_ID = os.environ.get("CHANNEL_ID", DEFAULT_CHANNEL).strip() or DEFAULT_CHANNEL
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6640701495").strip() or "6640701495")
PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").strip()

start_time = time.time()
ping_counter = 0

def normalize_channel(raw_input: str) -> str:
    if not raw_input:
        return DEFAULT_CHANNEL
    s = raw_input.strip()
    if "t.me/" in s:
        s = s.split("t.me/")[-1].split("/")[0].split("?")[0]
    s = s.strip()
    if s.startswith("-100") or (s.startswith("-") and s[1:].isdigit()):
        return s
    s = s.lstrip("@").strip()
    return f"@{s}"

current_channel = normalize_channel(CHANNEL_ID)
pending_posts = {}

# 2-nji Suratdaky Ýaly Nagşly we Hestegli Mazmun
def generate_channel_caption(channel: str) -> str:
    return (
        "<b>Используйте Telegram без VPN, нажмите кнопку (connect)</b>\n"
        "════════ ◖⚚◗ ════════\n"
        f"💎 <b>{channel}</b>\n"
        "════════ ◖⚚◗ ════════\n"
        "🥇 <i>Самый быстрый канал прокси в Туркменистане</i>\n\n"
        "#ghostprotocol #proxy #freeproxy\n"
        "#mtproxy #socks5 #vpn #turkmenistan"
    )

app = Flask(__name__)

@app.route("/")
def index():
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"""
    <html><body style="background:#080c14;color:#10b981;font-family:sans-serif;text-align:center;padding:50px;">
        <div style="background:#0f172a;border:1px solid #10b981;border-radius:16px;padding:30px;display:inline-block;box-shadow:0 0 30px rgba(16,185,129,0.2);">
            <h1 style="color:#34d399;">🛡️ Ghost Protocol Bot</h1>
            <p style="color:#10b981;font-weight:bold;">🟢 24/7 OÝA WE IŞLEÝÄR (PRO DESIGN)</p>
            <p style="color:#94a3b8;">Admin ID: <b>{ADMIN_ID}</b></p>
            <p style="color:#94a3b8;">Kanal: <b>{current_channel}</b></p>
            <p style="color:#94a3b8;">Uptime: <b>{hours}h {minutes}m {seconds}s</b></p>
            <p style="color:#94a3b8;">Auto-Ping: <b>{ping_counter} gezek</b></p>
        </div>
    </body></html>
    """, 200

@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "healthy",
        "service": "Ghost Protocol MTProxy Bot",
        "admin_id": ADMIN_ID,
        "uptime": int(time.time() - start_time),
        "channel": current_channel,
        "self_pings": ping_counter
    }), 200

def start_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

def auto_keep_alive_pinger():
    global ping_counter
    time.sleep(15)
    while True:
        try:
            urls = []
            if RENDER_EXTERNAL_URL:
                urls.append(f"{RENDER_EXTERNAL_URL.rstrip('/')}/healthz")
            urls.append(f"http://127.0.0.1:{PORT}/healthz")

            for u in urls:
                try:
                    res = requests.get(u, timeout=10)
                    if res.status_code == 200:
                        ping_counter += 1
                        break
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Oýaryjy säwligi: {e}")
        time.sleep(240)

def parse_mtproxy_links(text: str) -> list[str]:
    valid_links = []
    url_pattern = re.compile(r'(?:https?://t\.me/proxy\?[^\s\<\>"\']+|tg://proxy\?[^\s\<\>"\']+)', re.IGNORECASE)
    for url in url_pattern.findall(text):
        clean_url = url.replace("tg://proxy?", "https://t.me/proxy?")
        parsed = urlparse(clean_url)
        params = parse_qs(parsed.query)
        s, p, sec = params.get("server", [""])[0], params.get("port", [""])[0], params.get("secret", [""])[0]
        if s and p and sec:
            norm = f"https://t.me/proxy?server={s}&port={p}&secret={sec}"
            if norm not in valid_links:
                valid_links.append(norm)

    raw_pattern = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b):(\d{2,5}):([a-fA-F0-9]{32,64}|ee[a-fA-F0-9]+|dd[a-fA-F0-9]+)', re.IGNORECASE)
    for s, p, sec in raw_pattern.findall(text):
        norm = f"https://t.me/proxy?server={s}&port={p}&secret={sec}"
        if norm not in valid_links:
            valid_links.append(norm)

    return valid_links

# 2-nji Suratdaky Ýaly 3 Sütünli Connect Düwmeleri
def build_channel_keyboard(links: list[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    count = len(links)
    row_size = 3 if count >= 3 else (2 if count == 2 else 1)
    buttons = [types.InlineKeyboardButton(text="Connect ↗", url=l) for l in links]
    
    for i in range(0, count, row_size):
        markup.row(*buttons[i:i + row_size])
        
    return markup

def get_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("📢 Kanala Post Ibermek"), types.KeyboardButton("⚡ Tizlik (Ping)"))
    markup.add(types.KeyboardButton("⚙️ Kanaly Sazlamak"), types.KeyboardButton("📊 24/7 Status"))
    markup.add(types.KeyboardButton("ℹ️ Gollanma"))
    return markup

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def check_admin(message_or_query) -> bool:
    user_id = message_or_query.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(message_or_query, types.CallbackQuery):
            bot.answer_callback_query(message_or_query.id, "⛔ Giriş gadagan!", show_alert=True)
        else:
            bot.reply_to(message_or_query, "⛔ <b>Giriş gadagan edildi!</b> Bu bot diňe administratoryň özi üçin goralandyr.")
        return False
    return True

try:
    bot.set_my_commands([
        types.BotCommand("start", "Baş menýuny we düwmeleri açmak"),
        types.BotCommand("post", "Kanala MTProxy postuny ugratmak"),
        types.BotCommand("setchannel", "Post iberiljek kanaly sazlamak"),
        types.BotCommand("status", "24/7 iş wagty we serwer ýagdaýy"),
        types.BotCommand("ping", "Botuň jogap tizligini barlamak"),
    ])
except Exception:
    pass

@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message):
    if not check_admin(message):
        return
    welcome_text = (
        "🛡️ <b>Ghost Protocol Dolandyryş Paneli (Pro Design)</b>\n\n"
        "Aşakdaky taýyn düwmeler arkaly ähli amallary <b>1 basyşda</b> ýerine ýetirip bilersiňiz!\n\n"
        f"📢 <b>Häzirki Kanal:</b> <code>{current_channel}</code> (Taýýar)\n"
        f"👤 <b>Admin ID:</b> <code>{ADMIN_ID}</code> (Doly Goralan)\n"
        "⚡ <b>Ýagdaýy:</b> 7/48 Oýa, düwmä basan badyňyza jogap bermäge taýýar!"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "⚡ Tizlik (Ping)" or msg.text == "/ping")
def handle_ping(message: types.Message):
    if not check_admin(message):
        return
    t0 = time.time()
    msg = bot.reply_to(message, "⚡ <i>Barlanýar...</i>")
    dt = round((time.time() - t0) * 1000, 1)
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.message_id,
        text=f"⚡ <b>Bot Oýa we Tiz Jogap Berýär!</b>\n\n• Jogap tizligi: <b>{dt} ms</b>\n• Ýagdaýy: 🟢 7/48 Durman Işleýär!",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda msg: msg.text == "📊 24/7 Status" or msg.text == "/status")
def handle_status(message: types.Message):
    if not check_admin(message):
        return
    uptime = int(time.time() - start_time)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)
    bot.reply_to(
        message,
        f"🟢 <b>Ghost Protocol 24/7 Status</b>\n\n"
        f"• <b>Admin:</b> <code>{ADMIN_ID}</code>\n"
        f"• <b>Iş wagty:</b> {h} sagat, {m} minut, {s} sekunt\n"
        f"• <b>Awtomatiki Oýaryjy:</b> {ping_counter} gezek oýaryldy\n"
        f"• <b>Birikdirilen Kanal:</b> <code>{current_channel}</code>",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "⚙️ Kanaly Sazlamak")
def handle_channel_menu(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(
        message,
        f"📢 <b>Kanal Sazlamalary</b>\n\nHäzirki bellenen kanal: <code>{current_channel}</code>\n\n"
        "Kanaly üýtgetmegiň 2 sany aňsat ýoly bar:\n"
        "1. Kanalyňyzdan islendik bir posty göni şu bota <b>Forward (Переслать)</b> ediň.\n"
        "2. Ýa-da buýruk ýazyň: <code>/setchannel @ghost_protocolI</code>",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(commands=["setchannel"])
def cmd_set_channel(message: types.Message):
    global current_channel
    if not check_admin(message):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Mysal: <code>/setchannel @ghost_protocolI</code>")
        return
    current_channel = normalize_channel(parts[1].strip())
    bot.reply_to(message, f"✅ <b>Kanal üstünlikli bellenildi:</b> <code>{current_channel}</code>", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.forward_from_chat is not None)
def handle_forwarded_post(message: types.Message):
    global current_channel
    if not check_admin(message):
        return
    chat = message.forward_from_chat
    if chat.username:
        current_channel = f"@{chat.username}"
    else:
        current_channel = str(chat.id)
    bot.reply_to(
        message,
        f"🎉 <b>Kanal derrew tanaldy we bellenildi!</b>\n\n"
        f"• Ady: <b>{chat.title}</b>\n"
        f"• Salgysy: <code>{current_channel}</code>\n\n"
        "Indi ugradýan MTProxy postlaryňyz göni şu kanala iberiler!",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Gollanma")
def handle_help(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(
        message,
        "ℹ️ <b>Nädip Ulanmaly?</b>\n\n"
        "1. MTProxy linkleriňizi şu söhbete ugradyň.\n"
        "2. Bot aşagynda <b>'🚀 Kanala Göni Ugrat'</b> düwmesini berer.\n"
        "3. Basan badyňyza 16:9 owadan banner, hestegler we 3 sütünli Connect düwmeleri bilen kanala paýlaşylar!",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "📢 Kanala Post Ibermek" or msg.text == "/post")
def handle_post_prompt(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(message, "📥 <b>MTProxy linkleriňizi şu ýere ugradyň:</b>", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_any_text(message: types.Message):
    if not check_admin(message):
        return
    text = message.text.strip()
    links = parse_mtproxy_links(text)

    if not links:
        bot.reply_to(message, "⚠️ <b>Hiç hili MTProxy tapylmady!</b>\nLinkiňizde server, port we secret barlygyny barlaň.", reply_markup=get_main_menu_keyboard())
        return

    user_id = message.from_user.id
    pending_posts[user_id] = links

    confirm_markup = types.InlineKeyboardMarkup()
    confirm_markup.row(
        types.InlineKeyboardButton("🚀 Kanala Göni Ugrat", callback_data="do_post_channel"),
        types.InlineKeyboardButton("❌ Ýatyr", callback_data="do_cancel_post")
    )

    bot.reply_to(
        message,
        f"✅ <b>{len(links)} sany MTProxy üstünlikli tapyldy!</b>\n\n"
        f"📢 <b>Ugradyljak Kanal:</b> <code>{current_channel}</code>\n"
        f" Düwmeler: <b>Connect ↗ ({len(links)} sany, 3 sütünli)</b>\n\n"
        "Posty kanala paýlaşmak üçin aşakdaky düwmä basyň:",
        reply_markup=confirm_markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: types.CallbackQuery):
    if not check_admin(call):
        return
    user_id = call.from_user.id

    if call.data == "do_cancel_post":
        if user_id in pending_posts:
            del pending_posts[user_id]
        bot.edit_message_text("❌ <b>Post ugratmak ýatyryldy.</b>", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Ýatyryldy")
        return

    if call.data == "do_post_channel":
        links = pending_posts.get(user_id, [])
        if not links:
            bot.answer_callback_query(call.id, "⚠️ Linkler tapylmady!", show_alert=True)
            return

        target = normalize_channel(current_channel)
        keyboard = build_channel_keyboard(links)
        caption = generate_channel_caption(target)

        # 16:9 ykjam we owadan kese banner
        banner_path = os.path.join(os.path.dirname(__file__), "ghost_banner_wide.jpg")
        if not os.path.exists(banner_path):
            banner_path = os.path.join(os.path.dirname(__file__), "ghost_profile_logo.jpg")

        try:
            if os.path.exists(banner_path):
                with open(banner_path, "rb") as photo:
                    bot.send_photo(
                        chat_id=target,
                        photo=photo,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            else:
                bot.send_message(
                    chat_id=target,
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

            bot.edit_message_text(
                f"🚀 <b>Post üstünlikli kanala ugradyldy!</b>\n\n"
                f"• Kanal: <code>{target}</code>\n"
                f"• Goşulan Connect düwmeleri: <b>{len(links)} sany (3 sütün)</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "🚀 Ugradyldy!")
            del pending_posts[user_id]

        except Exception as e:
            bot.answer_callback_query(call.id, f"Säwlik: {e}", show_alert=True)
            bot.send_message(call.message.chat.id, f"❌ <b>Post ugradyp bolmady:</b> <code>{e}</code>")

def main():
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=auto_keep_alive_pinger, daemon=True).start()
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    main()
