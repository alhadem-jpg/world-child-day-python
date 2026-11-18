import html
import hmac
import os
import random
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

MOTIVATION_LINES = [
    "أنتِ قادرة على تحقيق أحلامك خطوةً خطوة",
    "ذكاؤك واجتهادك يفتحان لك أبوابًا جميلة",
    "محاولتك اليوم بداية نجاح رائع",
    "أفكارك الجميلة تستحق أن يسمعها الجميع",
    "ابتسامتك تجعل يوم من حولك أجمل",
    "قلبك اللطيف هدية جميلة لمن حولك",
    "لكِ موهبة خاصة تزداد جمالًا كلما شاركتِها",
    "لا يوجد حلم كبير على عزيمتك",
    "كل يوم تتعلمين فيه شيئًا جديدًا هو يوم مميز",
    "أنتِ شجاعة حين تحاولين من جديد",
    "صوتك مهم ورأيك يستحق الاحترام",
    "خطواتك الصغيرة تصنع إنجازات كبيرة",
    "اجتهادك اليوم سيبهرك غدًا",
    "أنتِ مصدر فرح وفخر لمن يحبك",
    "خيالك الواسع يجعل العالم أجمل",
    "لا تستسلمي، فكل محاولة تقرّبك من هدفك",
    "لديكِ قدرة جميلة على نشر اللطف",
    "أنتِ تستحقين الفرح والنجاح والأمان",
    "كل فكرة جميلة تبدأ بطفلة تؤمن بنفسها",
    "تعلمك المستمر هو سر تميزك",
    "أنتِ أقوى مما تظنين وأقدر مما تتخيلين",
    "طيبتك تجعل العالم مكانًا أحنّ",
    "لكل يوم فرصة جديدة لتبدعي وتتألقي",
    "أنتِ قادرة على صنع فرق جميل",
    "أحلامك تستحق أن تحافظي عليها وتسعي إليها",
    "فضولك الجميل يقودك إلى اكتشافات رائعة",
    "لديكِ قلب شجاع وعقل مبدع",
    "كل إنجاز عظيم يبدأ بخطوة صغيرة",
    "أنتِ جميلة بأفكارك وأخلاقك وأحلامك",
    "ثقي بنفسك، فأنتِ تتقدمين كل يوم",
    "وجودك يضيف لونًا جميلًا إلى العالم",
    "من حقك أن تحلمي وأن تعبّري عن رأيك",
    "أنتِ تتعلمين وتنموين وتصبحين أفضل كل يوم",
    "قدرتك على المحاولة سر قوتك",
    "العالم يحتاج إلى أفكارك المميزة",
    "أنتِ تستحقين أن يفخر بك قلبك",
    "الأيام الجميلة تبدأ بإيمانك بنفسك",
    "كلما تعلمتِ أكثر أزهرت أحلامك",
    "أنتِ بطلة قصتك الجميلة",
    "لطفك الصغير يصنع سعادة كبيرة",
    "أنتِ قادرة على تجاوز الصعوبات بهدوء",
    "لا بأس أن تخطئي، فالتعلم يبدأ بالمحاولة",
    "لديكِ طاقة جميلة تستطيعين بها إنجاز الكثير",
    "أنتِ مبدعة بطريقتك الخاصة",
    "أحلامك تكبر مع كل خطوة شجاعة",
    "أنتِ تستحقين أن يسمع العالم صوتك",
    "كل ما تتقنينه اليوم كان يومًا ما محاولة",
    "في داخلك نور يضيء طريقك",
    "أنتِ صديقة رائعة لنفسك حين تشجعينها",
    "مستقبلك مليء بفرص جميلة تنتظرك"
]
MOTIVATION_FRAMES = [
    "يا {name}، {line}",
    "{name} الغالية، تذكّري: {line}",
    "إلى {name} الجميلة: {line}",
]
MOTIVATION_COUNT = len(MOTIVATION_LINES) * len(MOTIVATION_FRAMES)


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
    conn.execute("""CREATE TABLE IF NOT EXISTS motivation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrase_id INTEGER NOT NULL UNIQUE,
        used_at TEXT NOT NULL
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


def get_admin_messages():
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, kind, body, approved FROM messages ORDER BY id DESC"
        ).fetchall()


def set_message_visibility(message_id: int, visible: bool):
    with connect_db() as conn:
        conn.execute(
            "UPDATE messages SET approved=? WHERE id=?",
            (1 if visible else 0, message_id),
        )


def teacher_password_configured():
    try:
        return str(st.secrets.get("TEACHER_PASSWORD", ""))
    except Exception:
        return os.environ.get("TEACHER_PASSWORD", "")




def next_motivation(name: str):
    with connect_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        used = {row[0] for row in conn.execute("SELECT phrase_id FROM motivation_history")}
        last_row = conn.execute("SELECT phrase_id FROM motivation_history ORDER BY id DESC LIMIT 1").fetchone()
        last_phrase = last_row[0] if last_row else None
        if len(used) >= MOTIVATION_COUNT:
            conn.execute("DELETE FROM motivation_history")
            used = set()
            if last_phrase is not None and MOTIVATION_COUNT > 1:
                conn.execute(
                    "INSERT INTO motivation_history(phrase_id, used_at) VALUES (?, ?)",
                    (last_phrase, datetime.utcnow().isoformat(timespec="seconds")),
                )
                used.add(last_phrase)
        available = [phrase_id for phrase_id in range(MOTIVATION_COUNT) if phrase_id not in used]
        phrase_id = random.choice(available)
        conn.execute(
            "INSERT INTO motivation_history(phrase_id, used_at) VALUES (?, ?)",
            (phrase_id, datetime.utcnow().isoformat(timespec="seconds")),
        )
    frame_index, line_index = divmod(phrase_id, len(MOTIVATION_LINES))
    safe_name = html.escape(name.strip())
    return MOTIVATION_FRAMES[frame_index].format(name=safe_name, line=MOTIVATION_LINES[line_index])

connect_db().close()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"], button, input, textarea {font-family:'Cairo', sans-serif !important;}
.stApp {background:linear-gradient(150deg,rgba(255,222,238,.22),rgba(208,238,255,.16)), url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-pastel-background.jpeg") center top / cover fixed no-repeat; color:#342747;}
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
.stApp {background: url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-pastel-background.jpeg") center top / cover fixed no-repeat #80cff8 !important; color:#342747;}
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

/* خلفية الطفل الجديدة مع واجهة أمامية واضحة */
.stApp {background:url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-pastel-background.jpeg") center top / cover fixed no-repeat #fff0eb !important; color:#49384a !important;}
.block-container {background:rgba(255,250,247,.86) !important; border:3px solid rgba(255,255,255,.96) !important; border-radius:32px !important; box-shadow:0 12px 34px rgba(125,82,88,.18) !important; backdrop-filter:blur(2px) !important;}
.hero {background:linear-gradient(115deg,#f28f9b,#f5b184 55%,#f6d28d) !important; border:4px solid #fff !important; border-radius:32px !important; color:#fff !important; text-shadow:0 2px 5px rgba(104,55,67,.3) !important; box-shadow:0 9px 0 rgba(226,153,141,.28),0 14px 28px rgba(154,103,101,.2) !important;}
.school,.footer {background:rgba(255,255,255,.96) !important; border:2px solid #f2d2cc !important; color:#5a4655 !important;}
.section-title {background:rgba(255,255,255,.97) !important; color:#9a5574 !important; border:2px solid #edc2cf !important; box-shadow:0 5px 14px rgba(131,80,97,.12) !important;}
.section-hint {background:rgba(255,255,255,.92) !important; color:#584553 !important; border:1px solid #f0ddd5 !important;}
[data-testid="stForm"] {background:rgba(255,255,255,.96) !important; border:2px solid #f2d2cc !important; box-shadow:0 8px 22px rgba(131,80,97,.12) !important;}
.right-card {background:rgba(255,255,255,.96) !important; border:2px solid #f1d5cf !important; outline:1px solid #edc2cf !important; box-shadow:0 7px 0 rgba(238,211,204,.6),0 12px 22px rgba(100,76,84,.1) !important;}
.message-wall {background:rgba(255,255,255,.94) !important; border-color:#eabaca !important;}
[data-testid="stTextArea"] textarea {background:#fff !important; color:#49384a !important; border-color:#e9bdc8 !important;}
[data-testid="stFormSubmitButton"] button,div[data-testid="stButton"] button {background:linear-gradient(105deg,#d8798c,#b97b9d 60%,#dda66d) !important; border:2px solid #fff !important; color:#fff !important; box-shadow:0 4px 0 rgba(171,107,124,.3) !important;}
[data-testid="stFormSubmitButton"] button *,div[data-testid="stButton"] button * {color:#fff !important;}
@media (max-width:700px) {.stApp {background-attachment:scroll !important; background-size:100% auto !important;} .block-container {background:rgba(255,250,247,.9) !important; padding:1rem .9rem 2rem !important; border-radius:26px !important;} [data-testid="stForm"] {padding:.8rem !important;}}


/* واجهة مستوحاة من تصميم هنا تتحدث الطفولة */
.stApp {background:linear-gradient(rgba(255,247,251,.56),rgba(255,247,251,.72)),url("https://raw.githubusercontent.com/alhadem-jpg/world-child-day-python/main/childrens-day-pastel-background.jpeg") center top / cover fixed no-repeat !important;color:#49324f !important;}
.block-container {max-width:1180px !important;padding:1rem 1.25rem 3rem !important;margin:0 auto !important;background:transparent !important;border:0 !important;border-radius:0 !important;box-shadow:none !important;backdrop-filter:none !important;}
.top-nav {position:sticky;top:.5rem;z-index:1000;display:flex;align-items:center;justify-content:space-between;gap:1rem;width:min(100%,1020px);margin:.3rem auto 3.2rem;padding:.8rem 1.5rem;border:1px solid rgba(255,255,255,.95);border-radius:999px;background:rgba(255,250,255,.88);box-shadow:0 8px 28px rgba(112,69,110,.12);backdrop-filter:blur(16px);}
.top-nav a {text-decoration:none !important;color:#58405f !important;font-weight:800;}
.nav-brand {color:#d65c98 !important;font-size:1.12rem;white-space:nowrap;}
.nav-links {display:flex;gap:clamp(.8rem,3vw,2.3rem);align-items:center;}
.nav-links a:hover {color:#d65c98 !important;}
.hero {background:transparent !important;border:0 !important;border-radius:0 !important;box-shadow:none !important;padding:4.4rem 1rem 7rem !important;margin:0 auto 2rem !important;color:#5b4262 !important;text-align:center;}
.hero-tag {display:inline-flex;align-items:center;padding:.55rem 1.2rem;border-radius:999px;background:rgba(255,255,255,.88);color:#9671b9;font-weight:800;box-shadow:0 5px 18px rgba(110,70,116,.1);}
.hero h1 {margin:1.4rem 0 .6rem !important;font-size:clamp(3rem,8vw,5.6rem) !important;font-weight:900 !important;line-height:1.2;background:linear-gradient(100deg,#e45d9c,#a16bd3);-webkit-background-clip:text;background-clip:text;color:transparent !important;text-shadow:none !important;}
.school-name {font-weight:900;font-size:clamp(1.8rem,4.2vw,3rem);background:linear-gradient(100deg,#e88c57,#39a98d,#9062cc,#e15d96);-webkit-background-clip:text;background-clip:text;color:transparent;margin:.7rem 0;}
.hero p {max-width:650px;margin:.7rem auto 1.8rem !important;font-size:1.15rem;color:#66556c;line-height:1.9;}
.hero-actions {display:flex;justify-content:center;flex-wrap:wrap;gap:.8rem;}
.hero-actions a {display:inline-flex;align-items:center;justify-content:center;padding:.85rem 1.5rem;border-radius:999px;text-decoration:none !important;font-weight:900;box-shadow:0 8px 20px rgba(116,71,124,.12);}
.hero-primary {background:linear-gradient(100deg,#df609b,#9867cd);color:white !important;}
.hero-secondary {background:rgba(255,255,255,.88);color:#9671b9 !important;}
.section-head {text-align:center;margin:1.6rem auto 2.2rem;scroll-margin-top:110px;}
.section-kicker {display:inline-block;padding:.4rem 1rem;border-radius:999px;background:#f2e5ff;color:#9670b7;font-size:.9rem;font-weight:800;}
.section-head h2 {margin:.8rem 0 .25rem !important;font-size:clamp(2.1rem,5vw,3rem) !important;font-weight:900 !important;background:linear-gradient(100deg,#df609b,#9867cd);-webkit-background-clip:text;background-clip:text;color:transparent !important;}
.section-head p {color:#716275;font-size:1.05rem;margin:.3rem 0 !important;}
.section-stars {display:block;color:#df609b;font-size:1rem;margin-top:.7rem;}
.stHorizontalBlock:has(.right-card) [data-testid="column"] {background:linear-gradient(145deg,rgba(255,239,250,.96),rgba(248,238,255,.96));border:2px solid rgba(255,255,255,.95);border-radius:28px;padding:.9rem .8rem .5rem;box-shadow:0 12px 24px rgba(103,70,111,.12);transition:transform .2s,box-shadow .2s;}
.stHorizontalBlock:has(.right-card) [data-testid="column"]:hover {transform:translateY(-4px);box-shadow:0 16px 28px rgba(103,70,111,.17);}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button {min-height:7.5rem !important;border-radius:22px !important;background:transparent !important;border:0 !important;box-shadow:none !important;color:#4e3858 !important;font-size:1.28rem !important;white-space:normal;}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button * {color:#4e3858 !important;text-shadow:none !important;}
.right-card {min-height:4rem !important;background:transparent !important;border:0 !important;outline:0 !important;border-radius:0 !important;padding:.2rem .3rem .7rem !important;box-shadow:none !important;text-align:center;}
.right-card p {color:#806c84 !important;font-size:.92rem !important;line-height:1.7 !important;}
[data-testid="stForm"] {max-width:760px;margin:0 auto 3rem !important;padding:1.5rem 2rem !important;border:2px solid rgba(255,255,255,.98) !important;border-radius:32px !important;background:linear-gradient(145deg,rgba(255,238,250,.95),rgba(247,237,255,.96)) !important;box-shadow:0 14px 30px rgba(103,70,111,.13) !important;}
[data-testid="stRadio"] [role="radiogroup"] {gap:.65rem !important;}
[data-testid="stRadio"] label {background:rgba(255,255,255,.82);border:1px solid #f2d6eb;border-radius:18px;padding:.55rem .75rem !important;color:#563f60 !important;font-weight:800 !important;}
[data-testid="stTextArea"] textarea {min-height:230px !important;background:rgba(255,255,255,.94) !important;border:2px solid #ecd2e7 !important;border-radius:24px !important;color:#49324f !important;font-size:1.03rem !important;}
[data-testid="stCaptionContainer"] p {color:#847189 !important;}
[data-testid="stFormSubmitButton"] button,div[data-testid="stButton"] button {background:linear-gradient(100deg,#df609b,#9867cd) !important;border:0 !important;border-radius:999px !important;box-shadow:0 8px 20px rgba(130,72,138,.18) !important;}
.message-wall {max-width:820px !important;border:0 !important;border-radius:30px !important;background:transparent !important;box-shadow:none !important;padding:.5rem !important;}
.message-card {border:2px solid rgba(255,255,255,.96) !important;border-radius:26px !important;padding:1.35rem 1.5rem !important;box-shadow:0 10px 24px rgba(108,72,112,.12) !important;}
.message-card p {color:#4f3c57 !important;}
.footer {max-width:900px;margin:4rem auto 1rem !important;padding:2rem !important;background:linear-gradient(145deg,rgba(255,239,250,.96),rgba(246,236,255,.96)) !important;border:2px solid white !important;border-radius:32px !important;box-shadow:0 12px 28px rgba(103,70,111,.12) !important;color:#5c4764 !important;font-size:1.15rem;font-weight:800;}
.teacher-credit {background:white !important;border-color:#f3d9e7 !important;box-shadow:0 4px 12px rgba(124,74,132,.1) !important;}
hr {border-color:rgba(190,151,190,.3) !important;}
@media(max-width:700px){.block-container{padding:.5rem .8rem 2rem !important}.top-nav{position:relative;top:auto;flex-direction:column;padding:.7rem;border-radius:24px;margin-bottom:1rem}.nav-links{gap:.8rem;flex-wrap:wrap;justify-content:center;font-size:.84rem}.hero{padding:2.5rem .4rem 4rem !important}.hero h1{font-size:3rem !important}.hero p{font-size:1rem}.stHorizontalBlock:has(.right-card){gap:.7rem}.stHorizontalBlock:has(.right-card) [data-testid="column"]{padding:.65rem .4rem .35rem;border-radius:21px}.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button{min-height:6.5rem !important;font-size:.96rem !important;padding:.5rem !important}.right-card{padding:.1rem .1rem .45rem !important}.right-card p{font-size:.8rem !important}[data-testid="stForm"]{padding:1rem !important;border-radius:25px !important}[data-testid="stTextArea"] textarea{min-height:180px !important}}


/* فراشات رقيقة ترفرف وتتحرك بهدوء */
.butterfly-layer{position:fixed;inset:0;z-index:2;pointer-events:none;overflow:hidden;}
.child-butterfly{position:absolute;width:42px;height:40px;opacity:.78;animation:butterfly-float 8s ease-in-out infinite;transform-origin:center;filter:drop-shadow(0 3px 5px rgba(133,88,155,.16));}
.child-butterfly .wing{position:absolute;width:16px;height:19px;border-radius:85% 16% 78% 20%;background:var(--wing,#b27bd1);transform-origin:100% 90%;}
.child-butterfly .upper.left{left:4px;top:1px;transform:rotate(-28deg);animation:wing-left 1.15s ease-in-out infinite;}
.child-butterfly .upper.right{right:4px;top:1px;transform:scaleX(-1) rotate(-28deg);animation:wing-right 1.15s ease-in-out infinite;}
.child-butterfly .lower.left{left:5px;top:18px;width:13px;height:15px;transform:rotate(28deg);animation:wing-left 1.15s ease-in-out infinite reverse;}
.child-butterfly .lower.right{right:5px;top:18px;width:13px;height:15px;transform:scaleX(-1) rotate(28deg);animation:wing-right 1.15s ease-in-out infinite reverse;}
.child-butterfly .body{position:absolute;left:20px;top:8px;width:3px;height:25px;border-radius:99px;background:#75518d;z-index:2;}
.child-butterfly .body:before,.child-butterfly .body:after{content:"";position:absolute;top:-4px;width:8px;height:8px;border-top:1.5px solid #75518d;border-radius:50%;}
.child-butterfly .body:before{right:1px;transform:rotate(-25deg)}.child-butterfly .body:after{left:1px;transform:rotate(25deg)}
.butterfly-one{--wing:#b58ad8;left:9%;top:27%;animation-duration:8.6s;}
.butterfly-two{--wing:#e98ab7;right:8%;top:51%;animation-duration:9.4s;animation-delay:-2s;transform:scale(.82);}
.butterfly-three{--wing:#ce9adf;left:15%;top:78%;animation-duration:10s;animation-delay:-4s;transform:scale(.72);}
@keyframes butterfly-float{0%,100%{translate:0 0;rotate:-5deg}50%{translate:12px -15px;rotate:6deg}}
@keyframes wing-left{0%,100%{scale:1 1}50%{scale:.62 1}}
@keyframes wing-right{0%,100%{scale:1 1}50%{scale:.62 1}}
@media(max-width:700px){.butterfly-one{left:7%;top:25%}.butterfly-two{right:6%;top:54%}.butterfly-three{left:10%;top:79%}}


/* بطاقات الحقوق: إطار مستقل بعرض كامل مثل المثال */
.stHorizontalBlock:has(.right-card){display:flex !important;flex-direction:column !important;align-items:stretch !important;gap:1.15rem !important;width:min(100%,760px) !important;margin:0 auto 1rem !important;}
.stHorizontalBlock:has(.right-card) [data-testid="column"]{box-sizing:border-box !important;width:100% !important;max-width:100% !important;flex:0 0 auto !important;margin:0 !important;padding:1.1rem 1rem .75rem !important;min-height:12.5rem !important;border:2px solid rgba(255,255,255,.98) !important;border-radius:32px !important;background:linear-gradient(145deg,rgba(255,239,250,.97),rgba(248,238,255,.97)) !important;box-shadow:0 12px 26px rgba(103,70,111,.14) !important;transition:transform .25s ease,box-shadow .25s ease !important;}
.stHorizontalBlock:has(.right-card) [data-testid="column"]:hover{transform:translateY(-3px) !important;box-shadow:0 16px 30px rgba(103,70,111,.18) !important;}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"]{width:100% !important;}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button{width:100% !important;min-height:8.3rem !important;padding:1rem !important;border:0 !important;border-radius:24px !important;background:transparent !important;box-shadow:none !important;color:#49324f !important;font-size:1.45rem !important;font-weight:900 !important;white-space:normal !important;}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button p{color:#49324f !important;font-size:1.4rem !important;font-weight:900 !important;line-height:1.5 !important;text-align:center !important;text-shadow:none !important;}
.stHorizontalBlock:has(.right-card) .right-card{min-height:2rem !important;margin:0 !important;padding:.15rem .3rem .35rem !important;background:transparent !important;border:0 !important;outline:0 !important;box-shadow:none !important;}
.stHorizontalBlock:has(.right-card) .right-card p{margin:0 !important;color:#806c84 !important;font-size:1.05rem !important;line-height:1.6 !important;}
@media(max-width:700px){.stHorizontalBlock:has(.right-card){width:100% !important;gap:1rem !important;margin-bottom:.8rem !important;}.stHorizontalBlock:has(.right-card) [data-testid="column"]{min-height:12rem !important;padding:.9rem .8rem .65rem !important;border-radius:30px !important;}.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button{min-height:7.6rem !important;font-size:1.25rem !important;}.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button p{font-size:1.25rem !important;}.stHorizontalBlock:has(.right-card) .right-card p{font-size:.98rem !important;}}


/* الإطار الفعلي لبطاقة الحق داخل عمود Streamlit */
.stHorizontalBlock:has(.right-card) > div[data-testid="stColumn"]{box-sizing:border-box !important;display:flex !important;flex:0 0 100% !important;width:100% !important;max-width:100% !important;min-width:100% !important;align-items:stretch !important;padding:1.1rem 1rem .75rem !important;min-height:12.5rem !important;border:2px solid rgba(255,255,255,.98) !important;border-radius:32px !important;background:linear-gradient(145deg,rgba(255,239,250,.97),rgba(248,238,255,.97)) !important;box-shadow:0 12px 26px rgba(103,70,111,.14) !important;}
.stHorizontalBlock:has(.right-card) > div[data-testid="stColumn"] > div{width:100% !important;}
@media(max-width:700px){.stHorizontalBlock:has(.right-card) > div[data-testid="stColumn"]{min-height:12rem !important;padding:.9rem .8rem .65rem !important;border-radius:30px !important;}}


/* أيقونة دائرية لكل حق داخل بطاقته */
.right-icon{width:92px;height:92px;margin:.1rem auto .25rem;display:flex;align-items:center;justify-content:center;border:9px solid #fff;border-radius:50%;background:var(--right-icon,#59acd2);box-shadow:0 5px 14px rgba(77,66,92,.12);font-size:2.8rem;line-height:1;}
.icon-0{--right-icon:#52a8d1}.icon-1{--right-icon:#e8b83d}.icon-2{--right-icon:#42b89a}.icon-3{--right-icon:#ee9565}.icon-4{--right-icon:#e36aa7}.icon-5{--right-icon:#9871d1}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button{min-height:3.6rem !important;padding:.15rem .5rem !important;font-size:1.4rem !important;}
.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button p{font-size:1.4rem !important;line-height:1.45 !important;}
@media(max-width:700px){.right-icon{width:82px;height:82px;font-size:2.4rem;border-width:8px}.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button{min-height:3.4rem !important;font-size:1.2rem !important}.stHorizontalBlock:has(.right-card) div[data-testid="stButton"] button p{font-size:1.2rem !important}}

.motivation-form {max-width:760px;margin:0 auto 1rem !important;padding:1.2rem 1.4rem;border:2px solid rgba(255,255,255,.96);border-radius:28px;background:linear-gradient(145deg,rgba(255,239,250,.96),rgba(247,237,255,.97));box-shadow:0 12px 26px rgba(103,70,111,.12);}
.motivation-result {max-width:760px;margin:1rem auto 2rem;padding:1.3rem 1.5rem;border:2px solid #fff;border-radius:26px;background:linear-gradient(110deg,#fff1f6,#f3e9ff);color:#5b3f68;text-align:center;font-size:1.2rem;font-weight:900;line-height:1.9;box-shadow:0 10px 24px rgba(103,70,111,.13);animation:rise .55s ease both;}
[data-testid="stTextInput"] input {background:#fff !important;color:#49324f !important;border:2px solid #ecd2e7 !important;border-radius:16px !important;}
@media(max-width:700px){.motivation-form{padding:.9rem !important}.motivation-result{font-size:1.05rem;padding:1rem;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="butterfly-layer" aria-hidden="true"><span class="child-butterfly butterfly-one"><i class="wing upper left"></i><i class="wing upper right"></i><i class="wing lower left"></i><i class="wing lower right"></i><i class="body"></i></span><span class="child-butterfly butterfly-two"><i class="wing upper left"></i><i class="wing upper right"></i><i class="wing lower left"></i><i class="wing lower right"></i><i class="body"></i></span><span class="child-butterfly butterfly-three"><i class="wing upper left"></i><i class="wing upper right"></i><i class="wing lower left"></i><i class="wing lower right"></i><i class="body"></i></span></div>
<nav class="top-nav" dir="rtl"><a class="nav-brand" href="#top">♥ هنا تتحدث الطفولة</a><div class="nav-links"><a href="#rights">حقوقي الجميلة</a><a href="#motivation">كلمتي لك</a><a href="#voice">هنا تتحدث الطفولة</a><a href="#wall">رسائل من القلب</a></div></nav>
<div class="hero" id="top" dir="rtl"><div class="hero-tag">⭐ بمناسبة اليوم العالمي للطفل ⭐</div><h1>هنا تتحدث الطفولة</h1><div class="school-name">مدرسة الزويراء الأولى الابتدائية</div><p>لكل طفلة صوت، ولكل صوت حكاية… تعرّفي على حقوقك واكتبي رسالتك للعالم</p><div class="hero-actions"><a class="hero-primary" href="#voice">اكتبي رسالتك　❀</a><a class="hero-secondary" href="#rights">تعرّفي على حقوقك　♡</a></div></div>
""", unsafe_allow_html=True)

st.markdown('<div id="rights" class="section-head" dir="rtl"><span class="section-kicker">القسم الأول　❀</span><h2>حقوقي الجميلة</h2><p>اضغطي على كل بطاقة لتكتشفي حقًّا من حقوقك</p><span class="section-stars">♥　★　♥</span></div>', unsafe_allow_html=True)
cols = st.columns(3)
for i, (emoji, title, description) in enumerate(RIGHTS):
    with cols[i % 3]:
        st.markdown(f'<div class="right-icon icon-{i}" aria-hidden="true">{emoji}</div>', unsafe_allow_html=True)
        if st.button(title, key=f"right_{i}", use_container_width=True):
            st.session_state["selected_right"] = i
        if st.session_state.get("selected_right") == i:
            card_text = description
        else:
            card_text = "اضغطي البطاقة لتتعرفي على حقك الجميل 🌷"
        st.markdown(f'<div class="right-card" dir="rtl"><p>{html.escape(card_text)}</p></div>', unsafe_allow_html=True)
    if i % 3 == 2 and i != len(RIGHTS) - 1:
        cols = st.columns(3)

st.markdown('<div id="motivation" class="section-head" dir="rtl"><span class="section-kicker">هدية صغيرة　❀</span><h2>كلمة تحفيزية باسمك</h2><p>اكتبي اسمك الأول، وخذي رسالة جميلة خاصة بك</p><span class="section-stars">♥　★　♥</span></div>', unsafe_allow_html=True)
with st.form("motivation_form", clear_on_submit=True):
    student_name = st.text_input("اسمك الأول", max_chars=20, placeholder="مثال: نورة")
    st.caption("اكتبي الاسم الأول فقط؛ لا نحفظ اسمك في قاعدة بيانات الرسائل.")
    get_motivation = st.form_submit_button("🌷 أرسلوا لي كلمة تحفيزية", use_container_width=True)
    if get_motivation:
        if not student_name.strip():
            st.warning("اكتبي اسمك الأول لتحصلي على رسالتك الجميلة 🌸")
        else:
            st.session_state["motivation_result"] = next_motivation(student_name.strip())
if st.session_state.get("motivation_result"):
    st.markdown(f'<div class="motivation-result" dir="rtl">💖 {st.session_state["motivation_result"]} 🌷</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div id="voice" class="section-head" dir="rtl"><span class="section-kicker">القسم الثاني　❀</span><h2>هنا تتحدث الطفولة</h2><p>مساحة صغيرة لصوتك الجميل، اكتبي ما يجول في خاطرك</p><span class="section-stars">♥　★　♥</span></div>', unsafe_allow_html=True)
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

st.markdown('<div id="wall" class="section-head" dir="rtl"><span class="section-kicker">القسم الثالث　❀</span><h2>رسائل من القلب</h2><p>كلمات جميلة كتبتها طالباتنا الغاليات</p><span class="section-stars">♥　★　♥</span></div>', unsafe_allow_html=True)
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

st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("🔐 لوحة المعلمة — إدارة رسائل الحائط"):
    teacher_password = teacher_password_configured()
    if not teacher_password:
        st.info("لوحة المعلمة مقفلة حتى تضبطي رمزًا خاصًا في Streamlit: App settings → Secrets، ثم أضيفي TEACHER_PASSWORD = \"رمزك السري\" وأعيدي تشغيل التطبيق.")
    elif not st.session_state.get("teacher_authenticated", False):
        with st.form("teacher_login_form"):
            entered_password = st.text_input("رمز المعلمة", type="password")
            login = st.form_submit_button("دخول لوحة المعلمة", use_container_width=True)
        if login:
            if hmac.compare_digest(entered_password.encode("utf-8"), teacher_password.encode("utf-8")):
                st.session_state["teacher_authenticated"] = True
                st.rerun()
            else:
                st.error("الرمز غير صحيح.")
    else:
        if st.button("تسجيل الخروج من لوحة المعلمة", key="teacher_logout"):
            st.session_state["teacher_authenticated"] = False
            st.rerun()
        teacher_messages = get_admin_messages()
        if not teacher_messages:
            st.info("لا توجد رسائل في الحائط حتى الآن.")
        for row in teacher_messages:
            with st.container():
                status = "منشورة" if row["approved"] else "مخفاة عن الزائرات"
                st.markdown(f"**{html.escape(row['kind'])} — {status}**")
                st.write(row["body"])
                if row["approved"]:
                    if st.button("إخفاء الرسالة من الحائط", key=f"hide_message_{row['id']}"):
                        set_message_visibility(row["id"], False)
                        st.rerun()
                else:
                    if st.button("إظهار الرسالة مجددًا", key=f"show_message_{row['id']}"):
                        set_message_visibility(row["id"], True)
                        st.rerun()
