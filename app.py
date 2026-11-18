import html
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("MESSAGES_DB", APP_DIR / "messages.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="اليوم العالمي للطفل | صوت الطفولة", page_icon="🧸", layout="wide")

RIGHTS = [
    ("📚", "حقي في التعليم", "من حقي أن أتعلم وأكتشف أشياء جديدة كل يوم."),
    ("⚽", "حقي في اللعب", "اللعب يجعلني سعيدة ويساعدني على النمو والتعلّم."),
    ("🛡️", "حقي في الأمان", "من حقي أن أعيش وأتعلم في مكان آمن ومطمئن."),
    ("🩺", "حقي في الصحة", "من حقي أن أحصل على الرعاية الصحية والغذاء المفيد."),
    ("💗", "حقي في الرعاية والحب", "من حقي أن أجد من يرعاني ويعاملني بلطف ومحبة."),
    ("🗣️", "حقي في التعبير عن رأيي", "من حقي أن أعبّر عن رأيي وأن يستمع الآخرون إليّ باحترام."),
]
POST_TYPES = ["رسالة لأطفال العالم", "أمنيتي لكل طفل", "من حقي أن…"]


def connect_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT NOT NULL,
        body TEXT NOT NULL,
        approved INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def save_message(kind: str, body: str):
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO messages(kind, body, approved, created_at) VALUES (?, ?, 1, ?)",
            (kind, body.strip(), datetime.utcnow().isoformat(timespec="seconds")),
        )


def get_messages():
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, kind, body FROM messages WHERE approved=1 ORDER BY id DESC"
        ).fetchall()


connect_db().close()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"], button, input, textarea {font-family:'Cairo', sans-serif !important;}
.stApp {background:linear-gradient(150deg,rgba(255,222,238,.22),rgba(208,238,255,.16)), url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-background.jpeg") center top / cover fixed no-repeat; color:#342747;}
.block-container {max-width:1100px; padding:1.5rem 2rem 3rem; margin-top:1rem; margin-bottom:1rem; background:rgba(255,255,255,.78); border:2px solid rgba(255,255,255,.85); border-radius:30px; box-shadow:0 12px 34px #1d4d6a30; backdrop-filter:blur(3px);}
@media (max-width:700px) {.block-container {padding:1rem .9rem 2rem !important; margin:.5rem; border-radius:22px;}}
.hero {background:linear-gradient(115deg,#ff79a8,#ff9e78 55%,#ffd36f); border:3px solid rgba(255,255,255,.7); border-radius:30px; padding:2.1rem 2rem; text-align:center; color:white; box-shadow:0 14px 35px #de6d6c33; margin-bottom:1.2rem;}
.hero h1 {font-size:clamp(2rem,5vw,3.35rem); margin:0; font-weight:900;}
.hero p {font-size:1.1rem; margin:.55rem 0 0;}
.school {background:rgba(255,255,255,.94); border:2px solid #f7c6dc; color:#684782; border-radius:22px; padding:1rem; text-align:center; margin-bottom:1.5rem; box-shadow:0 7px 20px #543c4d16;}
.teacher-credit {display:inline-block; margin:.35rem auto; padding:.4rem 1rem; border-radius:999px; background:linear-gradient(100deg,#fff2a8,#ffd9ec); color:#4b2c68 !important; font-size:1.12rem; font-weight:900; border:2px solid #f2c466; box-shadow:0 4px 10px #d39e2d33;}
.section-title {font-size:1.8rem; font-weight:900; color:#673f8e; margin:.5rem 0 .2rem;}
.section-hint {color:#59425e; margin-bottom:1rem;} [data-testid="stRadio"] label, [data-testid="stRadio"] label p, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p {color:#3f2d4a !important; opacity:1 !important;} [data-testid="stTextArea"] textarea {color:#342747 !important;} [data-testid="stTextArea"] textarea::placeholder {color:#76667d !important; opacity:1 !important;} [data-testid="stFormSubmitButton"] button {background:linear-gradient(100deg,#c94674,#8044a2) !important; color:#fff !important;}
div[data-testid="stButton"] button {border:0; border-radius:16px; font-weight:900 !important; min-height:3.25rem; font-size:1.05rem !important; color:#fff !important; background:linear-gradient(100deg,#c94674,#8044a2) !important;} div[data-testid="stButton"] button, div[data-testid="stButton"] button * {color:#fff !important; font-weight:900 !important; text-shadow:0 1px 2px #58204f !important;}
.right-card {background:linear-gradient(145deg,#fffef1,#fff5fa); border:2px solid #f5d7e8; border-radius:24px; padding:1.2rem; min-height:170px; box-shadow:0 9px 24px #9d5f7a18; text-align:center;}
.right-card .emoji {font-size:2rem;}
.right-card h3 {font-size:1.08rem; color:#5a3c78; margin:.45rem 0;}
.right-card p {font-size:.94rem; color:#735f75; margin:0;}
.message-wall {display:flex; flex-direction:column; align-items:stretch; gap:.9rem; width:100%; max-width:900px; margin:1rem auto; padding:1rem; box-sizing:border-box; border:3px dashed #e9a7c7; border-radius:28px; background:rgba(255,255,255,.9); box-shadow:0 10px 24px #8b4d7418;}
.message-card {display:block !important; flex:0 0 auto !important; width:100% !important; max-width:100% !important; box-sizing:border-box; padding:1.15rem 1.25rem; border-radius:20px; margin:0; box-shadow:0 8px 22px #4e2c550d; animation:rise .55s ease both;}
.message-card p {font-size:1.05rem; margin:.3rem 0 0; line-height:1.9;}
.message-card small {opacity:.76; font-weight:700;}
@media (max-width:700px) {.message-wall {padding:.65rem; border-width:2px;} .message-card {padding:1rem;}}
@keyframes rise {from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.footer {text-align:center;color:#80677b;background:#fff;border-radius:18px;padding:1.2rem;margin-top:2rem;border:1px solid #f6dce3;}
hr {border-color:#c9e7fa;}
/* اجعل صورة يوم الطفل هي خلفية الصفحة ونسّق الواجهة كلوحة احتفالية */
.stApp {background: url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-background.jpeg") center top / cover fixed no-repeat #80cff8 !important; color:#342747;}
.block-container {background:rgba(255,255,255,.34) !important; border:3px solid rgba(255,255,255,.78) !important; border-radius:38px !important; box-shadow:0 12px 34px #2678a533 !important; backdrop-filter:none !important;}
.hero {background:linear-gradient(115deg,#38bdf8,#8b83f6 52%,#ff79a8) !important; border:4px solid #fff !important; border-radius:36px !important; box-shadow:0 10px 0 #55a8dc55,0 16px 30px #3479a844 !important;}
.section-title {display:inline-block; padding:.28rem 1rem; background:rgba(255,255,255,.93); border:2px solid #f5c6dc; border-radius:999px; box-shadow:0 5px 14px #597da022; text-shadow:0 1px #fff;}
.section-hint {display:table; padding:.25rem .85rem; border-radius:14px; background:rgba(255,255,255,.84); color:#46324f !important;}
[data-testid="stForm"] {background:rgba(255,255,255,.93); border:3px solid #fff; border-radius:28px; padding:1rem 1.1rem; box-shadow:0 10px 24px #4a82a522;}
[data-testid="stTextArea"] textarea {background:#fff !important; color:#342747 !important; border:2px solid #f1b9d4 !important; border-radius:18px !important;}
[data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button {background:linear-gradient(105deg,#ff668f,#ffad4d 55%,#42b9e9) !important; border:2px solid #fff !important; box-shadow:0 5px 0 #ca7caa55 !important;}
.right-card {background:linear-gradient(145deg,rgba(255,255,255,.97),rgba(255,246,252,.96)) !important; border:3px solid #fff !important; outline:2px solid #f3bfd8; box-shadow:0 8px 0 #f1cee0,0 12px 22px #5382a322 !important;}
.school, .footer {box-shadow:0 7px 0 #efc9df55,0 10px 24px #5180a322 !important;}
@media (max-width:700px) {.stApp {background-attachment:scroll !important; background-size:100% auto !important;} .block-container {background:rgba(255,255,255,.42) !important; padding:1rem .9rem 2rem !important; border-radius:26px !important;} [data-testid="stForm"] {padding:.8rem !important;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero" dir="rtl">
  <h1>🌍 اليوم العالمي للطفل 🧸</h1>
  <p>نفرح، نحلم، ونكتب رسائل من القلب 💛</p>
</div>
<div class="school" dir="rtl"><b>بكل الحب، مدرسة الزويراء الأولى الابتدائية</b><br><span class="teacher-credit">إعداد: أ. منال الحربي و أ. ساميه ناصر 🌷</span><br>معًا نحتفي بحقوق كل طفل ونستمع لصوته الجميل</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title" dir="rtl">حقوقي الجميلة</div><div class="section-hint" dir="rtl">لكل طفل حقوق جميلة تساعده أن يكبر سعيدًا وآمنًا.</div>', unsafe_allow_html=True)
cols = st.columns(3)
for i, (emoji, title, description) in enumerate(RIGHTS):
    with cols[i % 3]:
        if st.button(f"{emoji}  {title}", key=f"right_{i}", use_container_width=True):
            st.session_state["selected_right"] = i
        if st.session_state.get("selected_right") == i:
            card_text = description
        else:
            card_text = "اضغطي البطاقة لتتعرفي على حقك الجميل 🌷"
        st.markdown(f'<div class="right-card" dir="rtl"><p>{html.escape(card_text)}</p></div>', unsafe_allow_html=True)
    if i % 3 == 2 and i != len(RIGHTS) - 1:
        cols = st.columns(3)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title" dir="rtl">✍️ هنا تتحدث الطفولة</div><div class="section-hint" dir="rtl">مساحة صغيرة لصوتك الجميل، اكتبي ما يجول في خاطرك.</div>', unsafe_allow_html=True)
with st.form("message_form", clear_on_submit=True):
    kind = st.radio("اختاري نوع المشاركة", POST_TYPES, horizontal=True)
    message = st.text_area("اكتبي رسالتك هنا", max_chars=400, height=130, placeholder="اكتبي كلماتك الجميلة… من دون اسم أو أي معلومة شخصية.")
    st.caption("لخصوصيتك: لا تكتبي اسمك أو رقمك أو أي معلومة تكشف هويتك. ستظهر رسالتك للجميع فور إرسالها، فاكتبي كلمات لطيفة وآمنة.")
    submitted = st.form_submit_button("💌 إرسال رسالتي", use_container_width=True)
    if submitted:
        if len(message.strip()) < 3:
            st.warning("اكتبي رسالتك أولًا، ولو بكلمات قليلة 🌷")
        else:
            save_message(kind, message)
            st.success("ظهرت رسالتك للجميع في لوحة رسائل من القلب. شكرًا لصوتك الجميل! 💖")

st.markdown('<div class="section-title" dir="rtl">💌 رسائل من القلب</div><div class="section-hint" dir="rtl">رسائل الطالبات تظهر هنا مباشرة بعد إرسالها.</div>', unsafe_allow_html=True)
public_messages = get_messages()
colors = [("#fff0f5", "#f6cfdf"), ("#f5efff", "#dfd0f5"), ("#ffffff", "#eee4ec")]
wall_cards = []
for i, row in enumerate(public_messages):
    bg, border = colors[i % len(colors)]
    wall_cards.append(f'<div class="message-card" dir="rtl" style="background:{bg};border:2px solid {border}"><small>{html.escape(row["kind"])} 💗</small><p>{html.escape(row["body"])}</p></div>')
if not wall_cards:
    wall_cards.append('<div class="message-card" dir="rtl" style="background:#fff0f5;border:2px solid #f6cfdf"><p>كوني أول من يرسل كلمة جميلة هنا 🌸</p></div>')
st.markdown(f'<div class="message-wall" dir="rtl">{"".join(wall_cards)}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="footer" dir="rtl">بكل الحب، <b>مدرسة الزويراء الأولى الابتدائية</b><br><span class="teacher-credit">إعداد: أ. منال الحربي و أ. ساميه ناصر 🌷</span></div>', unsafe_allow_html=True)
