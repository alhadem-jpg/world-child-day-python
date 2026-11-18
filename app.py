import hmac
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


def configured_teacher_password():
    password = os.environ.get("TEACHER_PASSWORD", "")
    if password:
        return password
    try:
        return st.secrets.get("TEACHER_PASSWORD", "")
    except Exception:
        return ""


def save_message(kind: str, body: str):
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO messages(kind, body, approved, created_at) VALUES (?, ?, 0, ?)",
            (kind, body.strip(), datetime.utcnow().isoformat(timespec="seconds")),
        )


def get_messages(approved_only=True):
    with connect_db() as conn:
        if approved_only:
            return conn.execute(
                "SELECT id, kind, body FROM messages WHERE approved=1 ORDER BY id DESC"
            ).fetchall()
        return conn.execute(
            "SELECT id, kind, body FROM messages ORDER BY id DESC"
        ).fetchall()


connect_db().close()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"], button, input, textarea {font-family:'Cairo', sans-serif !important;}
.stApp {background:linear-gradient(145deg,#fff9f3 0%,#fff0f5 48%,#f5f0ff 100%); color:#342747;}
.block-container {max-width:1100px; padding-top:1.5rem; padding-bottom:3rem;}
.hero {background:linear-gradient(115deg,#ff7999,#ff9e78 55%,#ffc66f); border-radius:30px; padding:2.1rem 2rem; text-align:center; color:white; box-shadow:0 14px 35px #de6d6c33; margin-bottom:1.2rem;}
.hero h1 {font-size:clamp(2rem,5vw,3.35rem); margin:0; font-weight:900;}
.hero p {font-size:1.1rem; margin:.55rem 0 0;}
.school {background:#fff; border:1px solid #f6dce3; color:#80677b; border-radius:18px; padding:.85rem 1rem; text-align:center; margin-bottom:1.5rem; box-shadow:0 5px 18px #543c4d0a;}
.section-title {font-size:1.8rem; font-weight:900; color:#673f8e; margin:.5rem 0 .2rem;}
.section-hint {color:#816d82; margin-bottom:1rem;}
div[data-testid="stButton"] button {border:0; border-radius:16px; font-weight:800; min-height:3rem;}
.right-card {background:#fff; border:1px solid #f5e2e8; border-radius:21px; padding:1.2rem; min-height:170px; box-shadow:0 8px 22px #5a31570c; text-align:center;}
.right-card .emoji {font-size:2rem;}
.right-card h3 {font-size:1.08rem; color:#5a3c78; margin:.45rem 0;}
.right-card p {font-size:.94rem; color:#735f75; margin:0;}
.message-card {padding:1.15rem 1.25rem; border-radius:20px; margin:.65rem 0; box-shadow:0 8px 22px #4e2c550d; animation:rise .55s ease both;}
.message-card p {font-size:1.05rem; margin:.3rem 0 0; line-height:1.9;}
.message-card small {opacity:.76; font-weight:700;}
@keyframes rise {from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.footer {text-align:center;color:#80677b;background:#fff;border-radius:18px;padding:1.2rem;margin-top:2rem;border:1px solid #f6dce3;}
hr {border-color:#f0dfe8;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero" dir="rtl">
  <h1>🌍 اليوم العالمي للطفل 🧸</h1>
  <p>نفرح، نحلم، ونكتب رسائل من القلب 💛</p>
</div>
<div class="school" dir="rtl"><b>مدرسة الزويراء الأولى الابتدائية</b><br>معًا نحتفي بحقوق كل طفل ونستمع لصوته الجميل</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title" dir="rtl">🌈 حقوقي الجميلة</div><div class="section-hint" dir="rtl">لكل طفل حقوق جميلة تساعده أن يكبر سعيدًا وآمنًا.</div>', unsafe_allow_html=True)
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
    st.caption("لخصوصيتك: لا تكتبي اسمك أو رقمك أو أي معلومة تكشف هويتك. ستراجع المعلمة الرسالة قبل نشرها.")
    submitted = st.form_submit_button("💌 إرسال رسالتي", use_container_width=True)
    if submitted:
        if len(message.strip()) < 3:
            st.warning("اكتبي رسالتك أولًا، ولو بكلمات قليلة 🌷")
        else:
            save_message(kind, message)
            st.success("وصلت رسالتك إلى المعلمة للمراجعة. شكرًا لصوتك الجميل! 💖")

st.markdown('<div class="section-title" dir="rtl">💌 رسائل من القلب</div><div class="section-hint" dir="rtl">رسائل وافقت المعلمة على مشاركتها تظهر هنا.</div>', unsafe_allow_html=True)
public_messages = get_messages()
if not public_messages:
    st.info("ستظهر هنا الرسائل الجميلة بعد مراجعتها والموافقة عليها 🌸")
else:
    colors = [("#fff0f5", "#f6cfdf"), ("#f5efff", "#dfd0f5"), ("#ffffff", "#eee4ec")]
    for i, row in enumerate(public_messages):
        bg, border = colors[i % len(colors)]
        st.markdown(f'<div class="message-card" dir="rtl" style="background:{bg};border:1px solid {border}"><small>{html.escape(row["kind"])} 💗</small><p>{html.escape(row["body"])}</p></div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("🔐 لوحة المعلمة — مراجعة المشاركات"):
    password = st.text_input("كلمة مرور المعلمة", type="password", key="teacher_password")
    configured_password = configured_teacher_password()
    if not configured_password:
        st.warning("لوحة المراجعة مقفلة حتى تضبط المعلمة كلمة المرور في إعدادات الاستضافة باسم TEACHER_PASSWORD.")
    elif password and hmac.compare_digest(password, configured_password):
        st.success("تم الدخول إلى لوحة المراجعة.")
        pending = get_messages(approved_only=False)
        pending = [r for r in pending if not r["approved"]]
        if not pending:
            st.info("لا توجد رسائل بانتظار المراجعة.")
        for row in pending:
            st.markdown(f'**{html.escape(row["kind"])}**  \n{html.escape(row["body"])}')
            approve_col, delete_col = st.columns(2)
            with approve_col:
                if st.button("✅ موافقة ونشر", key=f"approve_{row['id']}", use_container_width=True):
                    with connect_db() as conn:
                        conn.execute("UPDATE messages SET approved=1 WHERE id=?", (row["id"],))
                    st.rerun()
            with delete_col:
                if st.button("🗑️ رفض وحذف", key=f"delete_{row['id']}", use_container_width=True):
                    with connect_db() as conn:
                        conn.execute("DELETE FROM messages WHERE id=?", (row["id"],))
                    st.rerun()
    elif password:
        st.error("كلمة المرور غير صحيحة.")

st.markdown('<div class="footer" dir="rtl">بكل الحب، <b>مدرسة الزويراء الأولى الابتدائية</b><br>إعداد: <b>أ. منال الحربي</b> 🌷</div>', unsafe_allow_html=True)
