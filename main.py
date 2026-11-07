#!/usr/bin/env python3
"""
🛡️ Ghost Protocol - 24/7 Telegram MTProxy Channel Poster Bot (Modern Çudo Edition)
Framework: pyTelegramBotAPI (telebot) + Flask (Keep-Alive Server)
Host Target: Render.com / GitHub / VPS
Exclusively authorized for Admin ID: 6640701495

Aýratynlyklar (Features):
  - 🎨 Kämil Post Redaktory (Çudo Panel):
      • Galereýadan göni surat ýüklemek (1 basyşda custom_banner.jpg hökmünde bellenýär)
      • Tekst şrift stilleri (Monospace kiber kod, Galyň Bold, Ýapgyt, Elite Unicode)
      • 9 sany täze bezeg çyzyklary (Blind Proxy Altyn, Kiber Zolaklar, Neon, Almaz, Galkan)
      • Ýaşyl "Connect ↗" düwme stilleri (🟢 Status, ⚡ Ýyldyrym, 🛡️ Galkan, Klassiki)
      • Düwme sütünleri: 3 sütünli, 2 sütünli, 1 sütünli ýa-da sanyna görä awtomatiki
      • Esasy teksti, kanaly, şygary we heştegleri doly redaktirlemek
      • Deslapky syn (Live Preview) bota iberip görmek
      • 1 basyşda taýýar stiller (Blind Proxy, Kiber Monospace, Elite Neon)
  - 💾 Sazlamalary 'post_config.json' faýlynda hemişelik ýatda saklaýar
  - 🔒 Admin ID goragy (Diňe 6640701495 ulanyp bilýär)
  - ⚡ Ygtybarly MTProxy parser (t.me/proxy, tg://proxy we IP:PORT:SECRET)
  - 🌐 Flask Keep-Alive Web Server + Arka fondaky awtomatiki oýaryjy (Self-Pinger)
"""

import os
import re
import json
import time
import logging
import threading
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify
import requests

import telebot
from telebot import types

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GhostProtocol")

# ---------------------------------------------------------
# Environment Variables & Base Paths
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8643237203:AAF5V_shvCNWoAyKBZkhnE8aOgQVTD8TVV0").strip()
DEFAULT_CHANNEL = "@ghost_protocolI"
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6640701495").strip() or "6640701495")
PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").strip()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "post_config.json")
CUSTOM_BANNER_PATH = os.path.join(BASE_DIR, "custom_banner.jpg")
WIDE_BANNER_PATH = os.path.join(BASE_DIR, "ghost_banner_wide.jpg")
LOGO_PATH = os.path.join(BASE_DIR, "ghost_profile_logo.jpg")
LOGO_CLEAN_PATH = os.path.join(BASE_DIR, "ghost_logo_clean.jpg")
LOGO_BRANDED_PATH = os.path.join(BASE_DIR, "ghost_logo_branded.jpg")

start_time = time.time()
ping_counter = 0

# ---------------------------------------------------------
# Default Post Configuration & Modern Styles
# ---------------------------------------------------------
DEFAULT_POST_CONFIG = {
    "post_text": "Используйте Telegram без VPN, нажмите кнопку (connect)",
    "channel_mention": DEFAULT_CHANNEL,
    "slogan": "Самый быстрый канал прокси в Туркменистане",
    "font_style": "bold",          # bold, monospace, italic, elite, clean
    "ornament_style": "default",    # default, gold_crest, cyber, cyber_matrix, diamond, fleur, glow, tech_dots, laser_shield, none
    "button_style": "green_dot",    # green_dot (🟢 Connect ↗), green_bolt (⚡ Connect ↗), shield (🛡️ Connect ↗), classic (Connect ↗)
    "button_columns": "3",          # 3, 2, 1, auto
    "hashtags": "#ghostprotocol #proxy #freeproxy\n#mtproxy #socks5 #vpn #turkmenistan",
    "use_custom_banner": False,
    "banner_type": "wide"
}

ORNAMENT_STYLES = {
    "default": "════════ ◖⚚◗ ════════",
    "gold_crest": "⚜️ ═══ ◖⚚◗ ═══ ⚜️",
    "cyber": "━━━━━━━━━━━━━━━━━━",
    "cyber_matrix": "░▒▓█ 🛡️ GHOST PROTOCOL 🛡️ █▓▒░",
    "diamond": "─── ❖ ─── ❖ ───",
    "fleur": "⚜️ ────────────── ⚜️",
    "glow": "✧･ﾟ: *✧･ﾟ:* ⚡ *:･ﾟ✧*:･ﾟ✧",
    "tech_dots": "• • • ┈┈┈┈┈┈┈┈┈┈ • • •",
    "laser_shield": "╾── 🛡️ SHIELD SECURED 🛡️ ──╼",
    "none": ""
}

ORNAMENT_NAMES = {
    "default": "◖⚚◗ Altyn Gerb (Blind Proxy)",
    "gold_crest": "⚜️ Altyn Şalyk (Luxury Gold)",
    "cyber": "━ Kiber Zolak (Clean Cyber)",
    "cyber_matrix": "▓ Kiber Matrisa (Matrix Grid)",
    "diamond": "❖ Almaz / Diamond",
    "fleur": "⚜️ Patyşalyk / Royal Fleur",
    "glow": "✧ Neon Ýagtylyk (Neon Stars)",
    "tech_dots": "• Inçe Kiber Nokatlar (Tech Dots)",
    "laser_shield": "🛡️ Lazer Galkan (Laser Shield)",
    "none": "🚫 Arakesmesiz (Ýönekeý)"
}

FONT_NAMES = {
    "bold": "𝐁 Galyň (Modern Bold) [Maslahat]",
    "monospace": "📟 Monospace (Kiber Kod)",
    "italic": "𝘐 Ýapgyt (Italic Sleek)",
    "elite": "💎 Elite Unicode (Stilli)",
    "clean": "Aa Ýönekeý (Standard Clean)"
}

BUTTON_STYLE_NAMES = {
    "green_dot": "🟢 Connect ↗ (Ýaşyl Status Nyşanly)",
    "green_bolt": "⚡ Connect ↗ (Kiber Ýyldyrymly)",
    "shield": "🛡️ Connect ↗ (Galkanly)",
    "classic": "Connect ↗ (Klassiki Standart)"
}

COLUMN_NAMES = {
    "3": "3 Sütünli (3 Columns) - [Maslahat]",
    "2": "2 Sütünli (2 Columns) - Giňişleýin",
    "1": "1 Sütünli (1 Column) - Doly Setir",
    "auto": "Awtomatiki (Link sanyna görä)"
}

def to_unicode_bold(text: str) -> str:
    normal_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold_chars = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    trans = str.maketrans(normal_chars, bold_chars)
    return text.translate(trans)

def load_post_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg = DEFAULT_POST_CONFIG.copy()
                cfg.update(saved)
                return cfg
        except Exception as e:
            logger.error(f"Sazlama faýly okalmady: {e}")
    return DEFAULT_POST_CONFIG.copy()

def save_post_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Sazlama faýly ýazylyp bolmady: {e}")

post_config = load_post_config()

current_channel = post_config.get("channel_mention", DEFAULT_CHANNEL)
pending_posts = {}
user_states = {}

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

def generate_channel_caption(channel: str = None) -> str:
    cfg = load_post_config()
    target_channel = channel or cfg.get("channel_mention", DEFAULT_CHANNEL)
    ornament_key = cfg.get("ornament_style", "default")
    ornament = ORNAMENT_STYLES.get(ornament_key, ORNAMENT_STYLES["default"])

    raw_text = cfg.get("post_text", DEFAULT_POST_CONFIG["post_text"])
    font_style = cfg.get("font_style", "bold")
    slogan = cfg.get("slogan", DEFAULT_POST_CONFIG["slogan"])
    tags = cfg.get("hashtags", DEFAULT_POST_CONFIG["hashtags"])

    if font_style == "monospace":
        styled_text = f"<code>{raw_text}</code>"
        channel_display = f"💎 <code>{target_channel}</code>"
    elif font_style == "italic":
        styled_text = f"<i>{raw_text}</i>"
        channel_display = f"💎 <b>{target_channel}</b>"
    elif font_style == "elite":
        styled_text = f"<b>{to_unicode_bold(raw_text)}</b>"
        channel_display = f"💎 <b>[ {target_channel} ]</b>"
    elif font_style == "clean":
        styled_text = raw_text
        channel_display = f"💎 {target_channel}"
    else:
        styled_text = f"<b>{raw_text}</b>"
        channel_display = f"💎 <b>{target_channel}</b>"

    if ornament:
        caption = (
            f"{styled_text}\n"
            f"{ornament}\n"
            f"{channel_display}\n"
            f"{ornament}\n"
            f"🥇 <i>{slogan}</i>\n\n"
            f"{tags}"
        )
    else:
        caption = (
            f"{styled_text}\n\n"
            f"{channel_display}\n\n"
            f"🥇 <i>{slogan}</i>\n\n"
            f"{tags}"
        )
    return caption

def get_active_banner_path():
    cfg = load_post_config()
    if cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH):
        return CUSTOM_BANNER_PATH

    btype = cfg.get("banner_type", "wide")
    if btype == "clean" and os.path.exists(LOGO_CLEAN_PATH):
        return LOGO_CLEAN_PATH
    if (btype == "square" or btype == "branded") and os.path.exists(LOGO_BRANDED_PATH):
        return LOGO_BRANDED_PATH
    if btype == "wide" and os.path.exists(WIDE_BANNER_PATH):
        return WIDE_BANNER_PATH

    for p in [WIDE_BANNER_PATH, LOGO_BRANDED_PATH, LOGO_CLEAN_PATH, LOGO_PATH]:
        if os.path.exists(p):
            return p
    return None

app = Flask(__name__)

@app.route("/")
def index():
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    cfg = load_post_config()
    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    
    return f"""
    <html><body style="background:#080c14;color:#10b981;font-family:sans-serif;text-align:center;padding:50px;">
        <div style="background:#0f172a;border:1px solid #10b981;border-radius:16px;padding:30px;display:inline-block;max-width:550px;box-shadow:0 0 30px rgba(16,185,129,0.2);">
            <h1 style="color:#34d399;">🛡️ Ghost Protocol Çudo Bot</h1>
            <p style="color:#10b981;font-weight:bold;">🟢 24/7 OÝA WE IŞLEÝÄR (MODERN EDITION)</p>
            <p style="color:#94a3b8;">Admin ID: <b>{ADMIN_ID} (Doly Goralan)</b></p>
            <p style="color:#94a3b8;">Kanal: <b>{cfg.get('channel_mention')}</b></p>
            <p style="color:#94a3b8;">Şrift: <b>{cfg.get('font_style', 'bold').upper()}</b> | Düwme: <b>{cfg.get('button_columns')} sütünli ({cfg.get('button_style')})</b></p>
            <p style="color:#94a3b8;">Post Suraty: <b>{'🖼 Galereýa Suraty' if has_custom else '🖼 16:9 Kiber Banner'}</b></p>
            <p style="color:#94a3b8;">Uptime: <b>{hours}h {minutes}m {seconds}s</b></p>
            <p style="color:#94a3b8;">Auto-Ping: <b>{ping_counter} gezek oýaryldy</b></p>
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
    url_pattern = re.compile(r'(?:https?://t\.me/proxy\?[^\s\<\>\"']+|tg://proxy\?[^\s\<\>\"']+)', re.IGNORECASE)
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

def build_channel_keyboard(links: list[str]) -> types.InlineKeyboardMarkup:
    cfg = load_post_config()
    b_style = cfg.get("button_style", "green_dot")
    col_setting = cfg.get("button_columns", "3")

    def get_btn_label(index: int) -> str:
        if b_style == "green_bolt":
            return "⚡ Connect ↗"
        elif b_style == "shield":
            return "🛡️ Connect ↗"
        elif b_style == "classic":
            return "Connect ↗"
        else:
            return "🟢 Connect ↗"

    count = len(links)
    if col_setting == "1":
        row_size = 1
    elif col_setting == "2":
        row_size = 2
    elif col_setting == "3":
        row_size = 3
    else:
        row_size = 3 if count >= 3 else (2 if count == 2 else 1)

    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=get_btn_label(i + 1), url=l) for i, l in enumerate(links)]
    for i in range(0, count, row_size):
        markup.row(*buttons[i:i + row_size])
    return markup

def get_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("📢 Kanala Post Ibermek"), types.KeyboardButton("🎨 Post Redaktory"))
    markup.add(types.KeyboardButton("⚡ Tizlik (Ping)"), types.KeyboardButton("⚙️ Kanaly Sazlamak"))
    markup.add(types.KeyboardButton("📊 24/7 Status"), types.KeyboardButton("ℹ️ Gollanma"))
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
        types.BotCommand("editor", "Post redaktory (şrift, düwme, nagş, surat)"),
        types.BotCommand("setchannel", "Post iberiljek kanaly sazlamak"),
        types.BotCommand("status", "24/7 iş wagty we serwer ýagdaýy"),
        types.BotCommand("ping", "Botuň jogap tizligini barlamak"),
    ])
except Exception:
    pass

def build_editor_markup():
    cfg = load_post_config()
    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    markup = types.InlineKeyboardMarkup()

    markup.row(types.InlineKeyboardButton("🖼 Galereýadan Täze Surat Ýüklemek", callback_data="ed_upload_photo"))

    markup.row(
        types.InlineKeyboardButton("🔤 Şrift Stili", callback_data="ed_choose_font"),
        types.InlineKeyboardButton("🟢 Connect Düwmesi", callback_data="ed_choose_buttons")
    )

    markup.row(
        types.InlineKeyboardButton("✏️ Esasy Tekst", callback_data="ed_edit_text"),
        types.InlineKeyboardButton("💎 Kanal Linki", callback_data="ed_edit_channel")
    )

    markup.row(
        types.InlineKeyboardButton("🥇 Aşaky Şygar", callback_data="ed_edit_slogan"),
        types.InlineKeyboardButton("🏷 Heştegler", callback_data="ed_edit_hashtags")
    )

    markup.row(types.InlineKeyboardButton("💠 Bezeg Çyzygy (Ornaments)", callback_data="ed_choose_ornament"))

    markup.row(
        types.InlineKeyboardButton("👁 Posty Syn Etmek (Preview)", callback_data="ed_preview_post"),
        types.InlineKeyboardButton("🔄 Standarta Gaýtar", callback_data="ed_reset_defaults")
    )

    if has_custom:
        markup.row(types.InlineKeyboardButton("🗑 Ýüklenen Suraty Aýyr (Standarta Gaýt)", callback_data="ed_remove_custom_photo"))

    return markup

def send_editor_panel(chat_id, message_id=None):
    cfg = load_post_config()
    ornament_key = cfg.get("ornament_style", "default")
    ornament_preview = ORNAMENT_STYLES.get(ornament_key, "════════ ◖⚚◗ ════════")
    if not ornament_preview:
        ornament_preview = "(Arakesmesiz / Ýönekeý)"

    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    photo_status = "🟢 Galereýaňyzdan Ýüklenen Surat" if has_custom else "🔵 16:9 Kiber Banner"
    font_name = FONT_NAMES.get(cfg.get("font_style", "bold"), "Galyň (Modern Bold)")
    btn_name = BUTTON_STYLE_NAMES.get(cfg.get("button_style", "green_dot"), "🟢 Connect ↗")
    col_name = COLUMN_NAMES.get(cfg.get("button_columns", "3"), "3 Sütünli")

    text = (
        "🎨 <b>Ghost Protocol Post Redaktory (Modern Çudo Panel)</b>\n\n"
        "Şu wagtky bellenen post sazlamalary:\n"
        f"• <b>Surat:</b> {photo_status}\n"
        f"• <b>Şrift Stili:</b> <code>{font_name}</code>\n"
        f"• <b>Connect Düwmesi:</b> <code>{btn_name}</code> ({col_name})\n"
        f"• <b>Esasy Tekst:</b> <i>{cfg.get('post_text')}</i>\n"
        f"• <b>Kanal Salgysy:</b> <code>{cfg.get('channel_mention')}</code>\n"
        f"• <b>Aşaky Şygar:</b> <i>{cfg.get('slogan')}</i>\n"
        f"• <b>Bezeg Çyzygy:</b> <code>{ornament_preview}</code>\n"
        f"• <b>Heştegler:</b> <code>{len(cfg.get('hashtags', '').split())} sany heşteg</code>\n\n"
        "👇 <i>Üýtgetmek isleýän zadyňyzyň düwmesine basyň:</i>"
    )

    markup = build_editor_markup()
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="HTML")
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message):
    if not check_admin(message):
        return
    cfg = load_post_config()
    welcome_text = (
        "🛡️ <b>Ghost Protocol Dolandyryş Paneli (Modern Edition)</b>\n\n"
        "✨ <b>Täze Aýratynlyklar:</b>\n"
        "• <i>Şrift stilleri (Monospace kiber kod, Galyň, Ýapgyt, Elite)</i>\n"
        "• <i>9 sany täze bezeg çyzyklary (Blind Proxy altyn, kiber, neon)</i>\n"
        "• <i>Ýaşyl reňkli 'Connect ↗' düwmeleri we 3 sütünli tertip!</i>\n"
        "• <i>Galereýadan 1 basyşda göni surat ýüklemek</i>\n\n"
        f"📢 <b>Häzirki Kanal:</b> <code>{cfg.get('channel_mention')}</code> (Taýýar)\n"
        f"👤 <b>Admin ID:</b> <code>{ADMIN_ID}</code> (Doly Goralan)\n"
        "⚡ <b>Ýagdaýy:</b> 7/48 Oýa, düwmä basan badyňyza jogap bermäge taýýar!"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text in ["🎨 Post Redaktory", "/editor"])
def handle_editor_command(message: types.Message):
    if not check_admin(message):
        return
    send_editor_panel(message.chat.id)

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
    cfg = load_post_config()
    bot.reply_to(
        message,
        f"🟢 <b>Ghost Protocol 24/7 Status</b>\n\n"
        f"• <b>Admin:</b> <code>{ADMIN_ID}</code>\n"
        f"• <b>Iş wagty:</b> {h} sagat, {m} minut, {s} sekunt\n"
        f"• <b>Awtomatiki Oýaryjy:</b> {ping_counter} gezek oýaryldy\n"
        f"• <b>Birikdirilen Kanal:</b> <code>{cfg.get('channel_mention')}</code>\n"
        f"• <b>Şrift:</b> {cfg.get('font_style', 'bold').upper()} | <b>Düwme:</b> {cfg.get('button_columns')} sütün ({cfg.get('button_style')})",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "⚙️ Kanaly Sazlamak")
def handle_channel_menu(message: types.Message):
    if not check_admin(message):
        return
    cfg = load_post_config()
    bot.reply_to(
        message,
        f"📢 <b>Kanal Sazlamalary</b>\n\nHäzirki bellenen kanal: <code>{cfg.get('channel_mention')}</code>\n\n"
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
    cfg = load_post_config()
    cfg["channel_mention"] = current_channel
    save_post_config(cfg)
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
    cfg = load_post_config()
    cfg["channel_mention"] = current_channel
    save_post_config(cfg)
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
        "ℹ️ <b>Ghost Protocol Modern Çudo Bot Gollanmasy</b>\n\n"
        "1. <b>Surat ýüklemek:</b> Galereýaňyzdan suraty bota ugratsaňyz, ol awtomatiki post suraty bolar.\n"
        "2. <b>Post Redaktory:</b> '🎨 Post Redaktory' düwmesinde şriftleri (Monospace, Bold, Elite), bezeg çyzyklaryny we ýaşyl Connect düwme stillerini sazlaň.\n"
        "3. <b>Kanala Post Ibermek:</b> MTProxy linklerini şu ýere ugradyň, bot '🚀 Kanala Göni Ugrat' düwmesini berer.\n"
        "4. Basan badyňyza owadan kiber banner, saýlanan şrift we 3 sütünli ýaşyl düwmeler bilen kanala paýlaşylar!",
        reply_markup=get_main_menu_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "📢 Kanala Post Ibermek" or msg.text == "/post")
def handle_post_prompt(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(message, "📥 <b>MTProxy linkleriňizi şu ýere ugradyň:</b>\n(Islendik format: https://t.me/proxy, tg://, ýa-da IP:PORT:SECRET)", reply_markup=get_main_menu_keyboard())

@bot.message_handler(content_types=["photo"])
def handle_photo_upload(message: types.Message):
    if not check_admin(message):
        return

    try:
        photo_info = message.photo[-1]
        file_info = bot.get_file(photo_info.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)

        with open(CUSTOM_BANNER_PATH, "wb") as f:
            f.write(downloaded_bytes)

        cfg = load_post_config()
        cfg["use_custom_banner"] = True
        save_post_config(cfg)

        user_states.pop(message.from_user.id, None)

        preview_markup = types.InlineKeyboardMarkup()
        preview_markup.row(
            types.InlineKeyboardButton("👁 Posty Syn Etmek (Preview)", callback_data="ed_preview_post"),
            types.InlineKeyboardButton("🎨 Post Redaktoryna Gaýt", callback_data="ed_open_panel")
        )

        bot.reply_to(
            message,
            "🎉 <b>Ajaýyp! Täze surat galereýadan üstünlikli ýüklenildi!</b>\n\n"
            "Indi kanala ugradyljak ähli MTProxy postlaryňyzda şu surat peýdalanylar.\n"
            "Görünüşini barlamak üçin aşakdaky düwmä basyň:",
            reply_markup=preview_markup
        )
    except Exception as e:
        logger.error(f"Surat ýüklemekde säwlik: {e}")
        bot.reply_to(message, f"❌ <b>Suraty ýükläp bolmady:</b> <code>{e}</code>")

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_any_text(message: types.Message):
    if not check_admin(message):
        return

    user_id = message.from_user.id
    current_state = user_states.get(user_id)
    text = message.text.strip()

    if current_state:
        cfg = load_post_config()

        if current_state == "waiting_for_text":
            cfg["post_text"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Esasy tekst üstünlikli üýtgedildi!</b>\n\nTäze tekst: <i>{text}</i>")
            send_editor_panel(message.chat.id)
            return

        elif current_state == "waiting_for_channel":
            normalized = normalize_channel(text)
            cfg["channel_mention"] = normalized
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Kanal salgysy üstünlikli üýtgedildi:</b> <code>{normalized}</code>")
            send_editor_panel(message.chat.id)
            return

        elif current_state == "waiting_for_slogan":
            cfg["slogan"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Aşaky şygar üstünlikli üýtgedildi!</b>\n\nTäze şygar: <i>{text}</i>")
            send_editor_panel(message.chat.id)
            return

        elif current_state == "waiting_for_hashtags":
            cfg["hashtags"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, "✅ <b>Heştegler üstünlikli üýtgedildi!</b>")
            send_editor_panel(message.chat.id)
            return

        elif current_state == "waiting_for_photo":
            bot.reply_to(
                message,
                "⚠️ <b>Siz tekst däl-de, SURAT ibermeli!</b>\n"
                "Galereýaňyzdan suraty saýlap iberiň ýa-da ýatyrmak üçin aşakdaky düwmä basyň.",
                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
            )
            return

    links = parse_mtproxy_links(text)
    if not links:
        bot.reply_to(
            message,
            "⚠️ <b>Hiç hili MTProxy tapylmady!</b>\n"
            "Linkiňizde <code>server</code>, <code>port</code> we <code>secret</code> barlygyny barlaň ýa-da aşakdaky menýudan peýdalanyň.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    pending_posts[user_id] = links
    cfg = load_post_config()
    target_channel = cfg.get("channel_mention", DEFAULT_CHANNEL)
    btn_style_name = BUTTON_STYLE_NAMES.get(cfg.get("button_style", "green_dot"), "🟢 Connect ↗")
    col_name = COLUMN_NAMES.get(cfg.get("button_columns", "3"), "3 Sütünli")

    confirm_markup = types.InlineKeyboardMarkup()
    confirm_markup.row(
        types.InlineKeyboardButton("🚀 Kanala Göni Ugrat", callback_data="do_post_channel"),
        types.InlineKeyboardButton("❌ Ýatyr", callback_data="do_cancel_post")
    )
    confirm_markup.row(
        types.InlineKeyboardButton("🎨 Post Dizaýnyny Redaktirle", callback_data="ed_open_panel")
    )

    bot.reply_to(
        message,
        f"✅ <b>{len(links)} sany MTProxy üstünlikli tapyldy!</b>\n\n"
        f"📢 <b>Ugradyljak Kanal:</b> <code>{target_channel}</code>\n"
        f"🔘 Düwmeler: <b>{btn_style_name} ({len(links)} sany, {col_name})</b>\n\n"
        "Posty kanala paýlaşmak üçin aşakdaky düwmä basyň:",
        reply_markup=confirm_markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: types.CallbackQuery):
    if not check_admin(call):
        return

    user_id = call.from_user.id
    data = call.data

    if data == "do_cancel_post":
        pending_posts.pop(user_id, None)
        bot.edit_message_text("❌ <b>Post ugratmak ýatyryldy.</b>", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Ýatyryldy")
        return

    if data == "ed_open_panel":
        send_editor_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    if data == "ed_cancel":
        user_states.pop(user_id, None)
        send_editor_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Ýatyryldy")
        return

    if data == "ed_upload_photo":
        user_states[user_id] = "waiting_for_photo"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text(
            "📸 <b>Galereýaňyzdan täze suraty saýlap şu söhbete ugradyň!</b>\n\n"
            "Bot ony derrew kabul edip, indiki postlaryňyz üçin esasy banner edip beller.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cancel_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data == "ed_remove_custom_photo":
        cfg = load_post_config()
        cfg["use_custom_banner"] = False
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Standart bannere geçildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data == "ed_choose_font":
        font_markup = types.InlineKeyboardMarkup()
        for key, name in FONT_NAMES.items():
            font_markup.row(types.InlineKeyboardButton(name, callback_data=f"set_font_{key}"))
        font_markup.row(types.InlineKeyboardButton("⬅️ Yza (Redaktora)", callback_data="ed_open_panel"))

        bot.edit_message_text(
            "🔤 <b>Postuň şrift stilini saýlaň:</b>\n\n"
            "• <b>Galyň:</b> Standart bold harplar (ýokary okalşyk)\n"
            "• <b>Monospace:</b> Kiber tehnologik kod srifti\n"
            "• <b>Ýapgyt:</b> Inçe döwrebap stil\n"
            "• <b>Elite:</b> Gözelleşdirilen unicode harplar",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=font_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data.startswith("set_font_"):
        f_key = data.replace("set_font_", "")
        cfg = load_post_config()
        cfg["font_style"] = f_key
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Şrift stili bellenildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data == "ed_choose_buttons":
        btn_markup = types.InlineKeyboardMarkup()
        btn_markup.row(types.InlineKeyboardButton("--- DÜWME NYŞANY SAÝLAŇ ---", callback_data="noop"))
        for key, name in BUTTON_STYLE_NAMES.items():
            btn_markup.row(types.InlineKeyboardButton(name, callback_data=f"set_btnstyle_{key}"))

        btn_markup.row(types.InlineKeyboardButton("--- SÜTÜNLER SANY ---", callback_data="noop"))
        btn_markup.row(
            types.InlineKeyboardButton("3 Sütün", callback_data="set_cols_3"),
            types.InlineKeyboardButton("2 Sütün", callback_data="set_cols_2"),
            types.InlineKeyboardButton("1 Sütün", callback_data="set_cols_1")
        )
        btn_markup.row(types.InlineKeyboardButton("Awtomatiki Sütün", callback_data="set_cols_auto"))
        btn_markup.row(types.InlineKeyboardButton("⬅️ Yza (Redaktora)", callback_data="ed_open_panel"))

        bot.edit_message_text(
            "🟢 <b>Connect Düwmeleriniň Stilini we Tertibini Saýlaň:</b>\n\n"
            "• <b>Nyşanlar:</b> Ýaşyl status (🟢), Ýyldyrym (⚡), Galkan (🛡️) ýa-da arassa (Connect ↗)\n"
            "• <b>Sütünler:</b> 3 sütünli (Telegramdaky ýaly ykjam), 2 sütünli ýa-da 1 sütünli",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=btn_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data.startswith("set_btnstyle_"):
        b_key = data.replace("set_btnstyle_", "")
        cfg = load_post_config()
        cfg["button_style"] = b_key
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Düwme stili bellenildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data.startswith("set_cols_"):
        c_key = data.replace("set_cols_", "")
        cfg = load_post_config()
        cfg["button_columns"] = c_key
        save_post_config(cfg)
        bot.answer_callback_query(call.id, f"{c_key} sütün bellenildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data == "ed_edit_text":
        user_states[user_id] = "waiting_for_text"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text(
            "✏️ <b>Postuň esasy tekstini täze görnüşde ýazyp ugradyň:</b>\n\n"
            "<i>Häzirki mysal: Используйте Telegram без VPN, нажмите кнопку (connect)</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cancel_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data == "ed_edit_channel":
        user_states[user_id] = "waiting_for_channel"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text(
            "💎 <b>Postda görünjek kanal adyny ýazyň:</b>\n\n"
            "<i>Mysal: @ghost_protocolI ýa-da https://t.me/ghost_protocolI</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cancel_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data == "ed_edit_slogan":
        user_states[user_id] = "waiting_for_slogan"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text(
            "🥇 <b>Aşaky şygary ýazyp ugradyň:</b>\n\n"
            "<i>Häzirki mysal: Самый быстрый канал прокси в Туркменистане</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cancel_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data == "ed_edit_hashtags":
        user_states[user_id] = "waiting_for_hashtags"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text(
            "🏷 <b>Postuň aşagyndaky heştegleri ugradyň:</b>\n\n"
            "<i>Mysal: #ghostprotocol #proxy #freeproxy #mtproxy #socks5 #vpn #turkmenistan</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cancel_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data == "ed_choose_ornament":
        ornament_markup = types.InlineKeyboardMarkup()
        for key, name in ORNAMENT_NAMES.items():
            ornament_markup.row(types.InlineKeyboardButton(name, callback_data=f"set_orn_{key}"))
        ornament_markup.row(types.InlineKeyboardButton("⬅️ Yza (Redaktora)", callback_data="ed_open_panel"))

        bot.edit_message_text(
            "💠 <b>Postdaky bezeg çyzygynyň (Ornament) stilini saýlaň:</b>\n\n"
            "Bu çyzyk kanalyň adynyň ýokarsynda we aşagynda döwrebap bolup görünýär.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=ornament_markup
        )
        bot.answer_callback_query(call.id)
        return

    if data.startswith("set_orn_"):
        orn_key = data.replace("set_orn_", "")
        cfg = load_post_config()
        cfg["ornament_style"] = orn_key
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Bezeg stili bellenildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data == "ed_reset_defaults":
        save_post_config(DEFAULT_POST_CONFIG.copy())
        bot.answer_callback_query(call.id, "Standart dizaýna gaýtaryldy!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return

    if data == "ed_preview_post":
        cfg = load_post_config()
        caption = generate_channel_caption()
        banner_path = get_active_banner_path()
        dummy_links = [
            "https://t.me/proxy?server=127.0.0.1&port=443&secret=ee00",
            "https://t.me/proxy?server=127.0.0.1&port=443&secret=ee01",
            "https://t.me/proxy?server=127.0.0.1&port=443&secret=ee02"
        ]
        dummy_markup = build_channel_keyboard(dummy_links)

        try:
            if banner_path and os.path.exists(banner_path):
                with open(banner_path, "rb") as photo:
                    bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=photo,
                        caption=f"👁 <b>[DESLAPKY SYN / PREVIEW]</b>\n\n{caption}",
                        reply_markup=dummy_markup,
                        parse_mode="HTML"
                    )
            else:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"👁 <b>[DESLAPKY SYN / PREVIEW]</b>\n\n{caption}",
                    reply_markup=dummy_markup,
                    parse_mode="HTML"
                )
            bot.answer_callback_query(call.id, "Syn ugradyldy!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Syn säwligi: {e}", show_alert=True)
        return

    if data == "do_post_channel":
        links = pending_posts.get(user_id, [])
        if not links:
            bot.answer_callback_query(call.id, "⚠️ Linkler tapylmady!", show_alert=True)
            return

        cfg = load_post_config()
        target = normalize_channel(cfg.get("channel_mention", DEFAULT_CHANNEL))
        keyboard = build_channel_keyboard(links)
        caption = generate_channel_caption(target)
        banner_path = get_active_banner_path()

        try:
            if banner_path and os.path.exists(banner_path):
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

            col_name = COLUMN_NAMES.get(cfg.get("button_columns", "3"), "3 Sütünli")
            btn_style_name = BUTTON_STYLE_NAMES.get(cfg.get("button_style", "green_dot"), "🟢 Connect ↗")

            bot.edit_message_text(
                f"🚀 <b>Post üstünlikli kanala ugradyldy!</b>\n\n"
                f"• Kanal: <code>{target}</code>\n"
                f"• Goşulan düwmeler: <b>{len(links)} sany ({col_name}, {btn_style_name})</b>\n"
                f"• Ulanylan surat: <b>{'Ýüklenen Surat' if cfg.get('use_custom_banner') else '16:9 Kiber Banner'}</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "🚀 Ugradyldy!")
            del pending_posts[user_id]

        except Exception as e:
            bot.answer_callback_query(call.id, f"Säwlik: {e}", show_alert=True)
            bot.send_message(
                call.message.chat.id,
                f"❌ <b>Post ugradyp bolmady:</b> <code>{e}</code>\n\n"
                f"<i>Bellik: Botuň <code>{target}</code> kanalyňyzda Administrator bolmagy hökmanydyr!</i>"
            )

def main():
    logger.info("Ghost Protocol Modern Çudo Bot işe girizilýär...")
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=auto_keep_alive_pinger, daemon=True).start()
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=10, skip_pending=True)
        except Exception as exc:
            logger.error(f"Polling säwligi: {exc}")
            time.sleep(5)

if __name__ == "__main__":
    main()
