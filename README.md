# 🛡️ Ghost Protocol - 24/7 Telegram MTProxy Channel Bot

Awtomatiki MTProxy postlaryny Telegram kanalyňyza 24/7 tertipde iberýän we **Render.com** mugt hostinginde uka gitmän (Keep-Alive + Awtomatiki Oýaryjy) işleýän kämil Python boty.

---

## ⚡ Aýratynlyklary (Features)

1. **Doly Goragly (Strict Admin Security)**:
   - Bot **DIŇE WE DIŇE** Administrator ID: `6640701495` üçin işleýär. Başga hiç kim bota girip ýa-da kanala post ugradyp bilmeýär!
2. **24/7 Iş Ulgamy & Içine Gurlan Awtomatiki Oýaryjy (Self-Pinger)**:
   - Içine gurlan **Flask Web Server** we arka fondaky **Auto-Pinger** sahypany her 4 minutdan oýaryp durýar. Netijede Render-iň 15 minutlyk uky wagty hiç haçan dolmaýar we bot 7/24 hiç durman işleýär.
3. **Dinamiki "Connect ↗" Düwmeleri**:
   - Siz näçe MTProxy linkini ugratsaňyz (1, 2, 3, 4, 6 ýa-da islendik mukdarda), bot şonça düwmäni owadan 2 sütünli tertipde düzýär.
4. **Universal Link Parser**:
   - `https://t.me/proxy?...`
   - `tg://proxy?...`
   - `IP:PORT:SECRET`
   - Bulaşyk tekstiň arasyndan hem ähli proxy-leri awtomatiki saýlap alýar!
5. **Gara Fondaky Ghost Protocol Logotipi**:
   - Postlar suraty bilen bilelikde ýaşyl kiber arwah logotipinde owadan çykýar.

---

## 🚀 GitHub we Render.com-da 24/7 Gurnamak

### 1-nji Ädim: GitHub Repository Döretmek
1. GitHub-da täze repository dörediň (meselem: `ghost-protocol-bot`).
2. Şu faýllary şol ýere goşuň:
   - `main.py`
   - `requirements.txt`
   - `Procfile`
   - `ghost_profile_logo.jpg`

### 2-nji Ädim: Render.com-da Web Service Döretmek
1. [Render.com](https://render.com) sahypasyna girip **New +** -> **Web Service** basyň.
2. GitHub-daky `ghost-protocol-bot` repository-ňyzy saýlaň.
3. Sazlamalar:
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`
4. **Environment Variables** (Gurşaw üýtgeýjileri) bölümine goşuň:
   - `BOT_TOKEN` = `8643237203:AAF5V_shvCNWoAyKBZkhnE8aOgQVTD8TVV0`
   - `ADMIN_ID` = `6640701495`
   - `CHANNEL_ID` = `@sizin_kanalyňyz`
   - `PORT` = `5000`
5. **Create Web Service** basyň.

### 3-nji Ädim: Kanala Administrasiýa
- Kanalyňyza girip, **@ghostik_postt_bot** bota Administrator ygtyýarlylygyny beriň (Iň bolmanda "Post Messages" açyk bolmaly).

---

## 🎮 Telegramdan Ulanyş

1. Bota girip `/start` ýazyň.
2. Eger kanalyňyzy üýtgetmek isleseňiz: `/setchannel @kanalyňyz`
3. Linkleri göni bota ugratsaňyz, bot olary derrew kanala paýlaşar!
