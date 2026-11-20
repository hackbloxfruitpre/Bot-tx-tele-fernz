import logging
import asyncio
import httpx
import json
import string
import os
import random
import pytz
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)


TOKEN = "9013814469:AAFejc8zagffNtXldhGQuhnFrBgbJgtDVQ4"
ADMIN_ID = 7504960222
DATAKEY_FILE = "datakey.json"
HANOI_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
QR_URL = "https://i.postimg.cc/v8kGHhMv/6334773150821849158.jpg"

CHANNEL_THONG_BAO = "https://t.me/kenhthongbaofzteam"
CHANNEL_CHAT = "https://t.me/kenhchatfzteam"
CHANNEL_BILL = "https://t.me/fzteambill"
ADMIN_HANDLE = "@tungocbo"
FREE_KEY_BOT = "@fztooltxfree_bot"


REQUIRED_BOXES = [
    {"name": "Kênh Thông Báo FZ Team", "url": CHANNEL_THONG_BAO, "chat_id": None},
    {"name": "Nhóm Chat FZ Team", "url": CHANNEL_CHAT, "chat_id": None},
    {"name": "Kênh Check Bill FZ Team", "url": CHANNEL_BILL, "chat_id": None},
]


API_URLS = {
    "sun_tx":     "http://180.93.114.115:3000/sunwin/taixiu",
    "sun_sb":     "http://163.61.182.4:7777/sun/sicbo",
    "hit_tx":     "http://180.93.114.115:3000/hitclub/taixiu",
    "hit_md5":    "http://180.93.114.115:3000/hitclub/taixiumd5",
    "hit_sb":     "http://163.61.182.4:7777/hit/sicbo",
    "b52_tx":     "http://180.93.114.115:3000/b52/taixiu",
    "b52_md5":    "http://180.93.114.115:3000/b52/taixiumd5",
    "b52_sb":     "http://180.93.114.115:3000/b52/sicbo",
    "betvip_tx":  "http://180.93.114.115:3000/betvip/taixiu",
    "betvip_md5": "http://180.93.114.115:3000/betvip/taixiumd5",
    "xd88_tx":    "http://180.93.114.115:3000/xocdia88/taixiu",
    "xd88_md5":   "http://180.93.114.115:3000/xocdia88/taixiumd5",
    "lc79_tx":    "http://180.93.114.115:3000/lc79/taixiu",
    "lc79_md5":   "http://180.93.114.115:3000/lc79/taixiumd5",
}


EMOJI_MAP = {
    "bell":        "6327857028949616018",
    "alert":       "6187956445036682670",
    "gift":        "6327659078201910163",
    "party":       "6186045798770286978",
    "bag":         "5229064374403998351",
    "percent":     "5386367538735104399",
    "spinner":     "5406745015365943482",
    "down":        "6282981642977944453",
    "net":         "6283020430827594914",
    "pin":         "6282807323140301774",
    "crown":       "6282574544502793568",
    "calendar":    "6282563411947561888",
    "game":        "6285240855905182667",
    "gear":        "6282526771581558537",
    "clip":        "6282961933373024331",
    "check":       "6282757029073265526",
    "cross":       "6187956445036682670",
    "game68":      "6283069706987381126",
    "club789":     "6282745939467708386",
    "go88":        "6282946544505202249",
    "sumclub":     "6282887140812532517",
    "tx_md5":      "6282907829669994559",
    "dice":        "6283010225985300164",
    "luck8":       "6282582722120524545",
    "rikvip":      "6282554036033956435",
    "iwin":        "6282752862954989731",
    "son789":      "6285090510575013655",
    "mega":        "6282542147564480286",
    "money":       "6282688322481431358",
    "dice_3d":     "6282625534354531452",
    "monitor":     "6283064591681333288",
    "cash":        "6282581652673667827",
    "fire":        "6282779899774117162",
    "sunwin":      "6282567672555120082",
    "hitclub":     "6283010225985300164",
    "b52_logo":    "6282887140812532517",
    "betvip_logo": "6282946544505202249",
    "lc79_logo":   "6282554036033956435",
    "xd88_logo":   "6284957224854889656",
    "table_tx":    "6131914320189071678",
    "table_md5":   "6129639044084147418",
    "table_sicbo": "5357334165404537258",
}

def ce(key, fallback):
    return f'<tg-emoji emoji-id="{EMOJI_MAP[key]}">{fallback}</tg-emoji>'

def btn_icon(key):
    return {"icon_custom_emoji_id": EMOJI_MAP[key]}

E_BELL       = ce("bell", "🔔")
E_ALERT      = ce("alert", "🚨")
E_GIFT       = ce("gift", "🎁")
E_PARTY      = ce("party", "🎉")
E_BAG        = ce("bag", "🛍")
E_PCT        = ce("percent", "%")
E_SPIN       = ce("spinner", "⌛")
E_DOWN       = ce("down", "⬇️")
E_NET        = ce("net", "🌐")
E_PIN        = ce("pin", "📌")
E_CROWN      = ce("crown", "👑")
E_CAL        = ce("calendar", "🗓")
E_GAME       = ce("game", "🎮")
E_GEAR       = ce("gear", "⚙️")
E_CLIP       = ce("clip", "📎")
E_OK         = ce("check", "✔️")
E_NO         = ce("cross", "❌")
E_DICE       = ce("dice", "🎲")
E_DICE3D     = ce("dice_3d", "🎲")
E_MD5        = ce("tx_md5", "🔐")
E_MEGA       = ce("mega", "📣")
E_MONEY      = ce("money", "💸")
E_MON        = ce("monitor", "🖥")
E_CASH       = ce("cash", "💵")
E_FIRE       = ce("fire", "🔥")

E_SUNWIN     = ce("sunwin", "☀️")
E_HITCLUB    = ce("hitclub", "🎰")
E_B52        = ce("b52_logo", "🃏")
E_BETVIP     = ce("betvip_logo", "🏆")
E_LC79       = ce("lc79_logo", "💎")
E_XD88       = ce("xd88_logo", "🍀")

E_TABLE_TX   = ce("table_tx", "🎮")
E_TABLE_MD5  = ce("table_md5", "🎮")
E_TABLE_SB   = ce("table_sicbo", "👽")


MEDIA_GROUP_BUFFERS = {}
MEDIA_GROUP_CAPTIONS = {}
MEDIA_GROUP_TIMERS = {}
MEDIA_GROUP_ACTIVE_MODE = {}


def init_datakey_file():
    if not os.path.exists(DATAKEY_FILE):
        save_datakey({
            "users": {}, "keys": {}, "history": [], "deposits": {},
            "giftcodes": {}, "game_history": {}, "deposit_requests": {},
            "free_key_requests": {},
            "sub_admins": [],
            "free_key_claims": {},
            "settings": {"last_user_id": 0, "last_key_id": 0,
                         "last_deposit_id": 0, "last_giftcode_id": 0,
                         "last_freekey_id": 0}
        })

def load_datakey():
    try:
        with open(DATAKEY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("sub_admins", [])
            data.setdefault("free_key_claims", {})
            data.setdefault("free_key_requests", {})
            return data
    except Exception:
        return {
            "users": {}, "keys": {}, "history": [], "deposits": {},
            "giftcodes": {}, "game_history": {}, "deposit_requests": {},
            "free_key_requests": {}, "sub_admins": [], "free_key_claims": {},
            "settings": {"last_user_id": 0, "last_key_id": 0,
                         "last_deposit_id": 0, "last_giftcode_id": 0,
                         "last_freekey_id": 0}
        }

def save_datakey(data):
    with open(DATAKEY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_hanoi_time():
    return datetime.now(HANOI_TZ)

def parse_hanoi_time(t):
    return datetime.fromisoformat(t).astimezone(HANOI_TZ) if t else None

def is_admin(user_id, data=None):
    if not user_id:
        return False
    uid_int = int(user_id)
    if uid_int == ADMIN_ID:
        return True
    if data is None:
        data = load_datakey()
    return uid_int in [int(x) for x in data.get("sub_admins", [])]

def ensure_user(data, user):
    uid = str(user.id)
    if uid not in data.setdefault("users", {}):
        data["users"][uid] = {
            "username": user.username or "No Username",
            "first_name": user.first_name or "Vô Danh",
            "join_date": get_hanoi_time().isoformat(),
            "key_expires": None,
            "balance": 0,
            "analysis_count": 0,
            "verified_3box": False,
        }
        save_datakey(data)
    else:
        data["users"][uid].setdefault("verified_3box", False)
    return uid

def next_request_id(data):
    s = data.setdefault("settings", {})
    s["last_deposit_id"] = s.get("last_deposit_id", 0) + 1
    return s["last_deposit_id"]

def next_freekey_id(data):
    s = data.setdefault("settings", {})
    s["last_freekey_id"] = s.get("last_freekey_id", 0) + 1
    return s["last_freekey_id"]

def is_key_active(user_record, user_id=None, data=None):
    if is_admin(user_id, data):
        return True
    exp = parse_hanoi_time(user_record.get("key_expires")) if user_record else None
    return exp is not None and get_hanoi_time() < exp

def _normalize_kq(v):
    if not v:
        return None
    s = str(v).upper()
    if "TAI" in s or "TÀI" in s:
        return "Tài"
    if "XIU" in s or "XỈU" in s:
        return "Xỉu"
    return None

def record_result(game_key, phien, ket_qua, pred=None):
    if not phien:
        return
    data = load_datakey()
    hist = data.setdefault("game_history", {}).setdefault(game_key, [])
    kq_norm = _normalize_kq(ket_qua)
    for entry in hist:
        if entry["phien"] == phien:
            if kq_norm and not entry.get("ket_qua"):
                entry["ket_qua"] = kq_norm
                if entry.get("pred"):
                    entry["status"] = "ĐÚNG" if entry["pred"].upper() == kq_norm.upper() else "SAI"
                save_datakey(data)
            return
    rec = {
        "phien": phien, "ket_qua": kq_norm, "pred": pred,
        "status": None, "time": get_hanoi_time().isoformat()
    }
    if pred and kq_norm:
        rec["status"] = "ĐÚNG" if pred.upper() == kq_norm.upper() else "SAI"
    hist.append(rec)
    if len(hist) > 200:
        hist.pop(0)
    save_datakey(data)

def _extract_chat_target(box):
    cid = box.get("chat_id")
    if cid not in (None, "", 0):
        return cid
    url = (box.get("url") or "").strip()
    if url.startswith("https://t.me/") and "/+" not in url and "/c/" not in url:
        handle = url.split("https://t.me/", 1)[1].strip("/").split("/")[0]
        if handle and not handle.startswith("joinchat"):
            return f"@{handle}"
    return None

async def check_3box_membership(bot, user_id):
    checked_count = 0
    for idx, box in enumerate(REQUIRED_BOXES, 1):
        target = _extract_chat_target(box)
        if not target:
            return False, box["name"], f"Box #{idx} ({box['name']}) chưa điền chat_id trong REQUIRED_BOXES.", checked_count
        try:
            member = await bot.get_chat_member(chat_id=target, user_id=int(user_id))
            if member.status in ("left", "kicked"):
                return False, box["name"], None, checked_count
            checked_count += 1
        except Exception as e:
            logging.warning("get_chat_member failed for %s (%s): %s", box["name"], target, e)
            return False, box["name"], f"Không kiểm tra được {box['name']} ({target}). Hãy kiểm tra bot đã vào box đó chưa.", checked_count
    return True, None, None, checked_count

def get_gate_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1. Kênh Thông Báo FZ Team", url=CHANNEL_THONG_BAO, api_kwargs=btn_icon("bell"))],
        [InlineKeyboardButton("2. Nhóm Chat FZ Team", url=CHANNEL_CHAT, api_kwargs=btn_icon("mega"))],
        [InlineKeyboardButton("3. Kênh Check Bill FZ Team", url=CHANNEL_BILL, api_kwargs=btn_icon("cash"))],
        [InlineKeyboardButton("Check OK — Xác Nhận Đã Vào 3 Box", callback_data="check_3box_ok", api_kwargs=btn_icon("check"))],
    ])

async def send_3box_gate(update_or_query, edit=False, reason=None):
    extra = f"\n{E_ALERT} <b>Chi tiết:</b> <i>{reason}</i>" if reason else ""
    text = (
        f"{E_ALERT} <b>BẮT BUỘC THAM GIA ĐỦ 3 BOX MỚI DÙNG BOT</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Bạn phải vào đủ <b>3 box</b> dưới đây trước khi sử dụng bot:\n"
        f"1. {E_BELL} Kênh Thông Báo: {CHANNEL_THONG_BAO}\n"
        f"2. {E_MEGA} Nhóm Chat: {CHANNEL_CHAT}\n"
        f"3. {E_CASH} Kênh Check Bill: {CHANNEL_BILL}\n\n"
        f"{E_OK} Sau khi vào đủ cả 3 box, bấm <b>Check OK</b>.{extra}"
    )
    kb = get_gate_keyboard()
    if edit and hasattr(update_or_query, "edit_message_text"):
        try:
            return await update_or_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            return await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    return await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def enforce_3box_or_block(update, context, user, data, is_callback=False):
    uid = str(user.id)
    u = data["users"][uid]
    ok, missing_box, reason, _ = await check_3box_membership(context.bot, user.id)
    if not ok:
        u["verified_3box"] = False
        save_datakey(data)
        alert_msg = reason or f"Bạn chưa vào đủ 3 box (thiếu: {missing_box})!"
        if is_callback:
            q = update.callback_query
            await q.answer(alert_msg[:200], show_alert=True)
            return True, await send_3box_gate(q, edit=True, reason=reason)
        return True, await send_3box_gate(update, edit=False, reason=reason)
    u["verified_3box"] = True
    save_datakey(data)
    return False, None

def build_main_header(user, u, data=None):
    uid = str(user.id)
    name = user.first_name or "Vô Danh"
    username = f"@{user.username}" if user.username else "Không có"
    if is_key_active(u, user.id, data):
        if is_admin(user.id, data) and not u.get("key_expires"):
            role_label = "ADMIN CHÍNH" if int(user.id) == ADMIN_ID else "ADMIN PHỤ"
            key_status = f"{E_CROWN} <b>{role_label} VIP VĨNH VIỄN</b>"
        else:
            exp = parse_hanoi_time(u["key_expires"])
            key_status = f"{E_CROWN} <b>VIP tới {exp.strftime('%d/%m/%Y %H:%M')}</b>"
    elif u.get("key_expires"):
        key_status = f"{E_NO} <b>Đã hết hạn</b>"
    else:
        key_status = f"{E_SPIN} <b>Chưa kích hoạt</b>"

    return (
        f"{E_CROWN} <b>BOT DOP SACH TIEN CUA NHA CAI</b> {E_CROWN}\n"
        f"{E_FIRE} <b>REAL-TIME NHANH GON - CHUAN XAC</b> {E_FIRE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} <b>Xin chào,</b> <b>{name}</b>! {E_FIRE}\n"
        f"{E_PIN} <b>ID:</b> <code>{uid}</code>\n"
        f"{E_CLIP} <b>Nick:</b> {username}\n"
        f"{E_MONEY} <b>Số dư:</b> <code>{u.get('balance', 0):,}đ</code> {E_CASH}\n"
        f"{E_CROWN} <b>KEY VIP:</b> {key_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_BELL} <b>KÊNH THÔNG BÁO:</b> {CHANNEL_THONG_BAO}\n"
        f"{E_MEGA} <b>NHÓM CHAT:</b> {CHANNEL_CHAT}\n"
        f"{E_CASH} <b>KÊNH CHECK BILL:</b> {CHANNEL_BILL}\n"
        f"{E_CROWN} <b>ADMIN HỖ TRỢ:</b> {ADMIN_HANDLE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_OK} <b>CHỌN CHỨC NĂNG BÊN DƯỚI</b> {E_FIRE}"
    )

def build_info_block(user, user_record, game_name=None, data=None):
    uid = str(user.id)
    name = user.first_name or "Vô Danh"
    username = f"@{user.username}" if user.username else "Không có"
    balance = user_record.get("balance", 0) if user_record else 0
    join_date = "—"
    if user_record and user_record.get("join_date"):
        jd = parse_hanoi_time(user_record["join_date"])
        if jd:
            join_date = jd.strftime('%d/%m/%Y')
    if user_record and is_key_active(user_record, user.id, data):
        if is_admin(user.id, data) and not user_record.get("key_expires"):
            key_status = f"{E_CROWN} <b>ADMIN VIP VĨNH VIỄN</b>"
        else:
            exp = parse_hanoi_time(user_record["key_expires"])
            key_status = f"{E_CROWN} <b>VIP tới {exp.strftime('%d/%m/%Y %H:%M')}</b>"
    elif user_record and user_record.get("key_expires"):
        key_status = f"{E_NO} <b>Đã hết hạn</b>"
    else:
        key_status = f"{E_SPIN} <b>Chưa kích hoạt</b>"
    today = get_hanoi_time()
    lines = [
        f"{E_CROWN} <b>THÔNG TIN TÀI KHOẢN</b> {E_FIRE}",
        f"{E_PARTY} <b>User:</b> <b>{name}</b>",
        f"{E_PIN} <b>ID:</b> <code>{uid}</code>",
        f"{E_NET} <b>Nick:</b> {username}",
        f"{E_CAL} <b>Tham gia:</b> <code>{join_date}</code>",
        f"{E_MONEY} <b>Số dư:</b> <code>{balance:,}đ</code> {E_CASH}",
        f"{E_BAG} <b>KEY VIP:</b> {key_status}",
        f"{E_BELL} <b>Thời gian:</b> <code>{today.strftime('%d/%m/%Y %H:%M:%S')}</code>",
    ]
    if game_name:
        lines.append(f"{E_GAME} <b>Phiên xem:</b> <b>{game_name}</b> {E_FIRE}")
    return "\n".join(lines)

def _clean_session_code(val):
    if val is None:
        return None
    s = str(val).strip().lstrip("#")
    return s if s else None

def _next_session_code(prev_val):
    s = _clean_session_code(prev_val)
    if not s:
        return None
    if s.isdigit():
        return str(int(s) + 1)
    return s

async def fetch_api_data(api_url, tool_type):
    if not api_url:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(api_url)
            if r.status_code != 200:
                return None
            d = r.json()
            is_sicbo = tool_type.endswith("_sb")
            if is_sicbo:
                prev_s = _clean_session_code(
                    d.get("phien_hien_tai") or d.get("phien_truoc") or d.get("Phien_hien_tai")
                )
                pred_s = _clean_session_code(
                    d.get("Phien_du_doan") or d.get("phien_du_doan") or d.get("phien_ke_tiep")
                )
                if not pred_s or (prev_s and pred_s == prev_s):
                    pred_s = _next_session_code(prev_s)
                return {
                    "game": tool_type.split("_")[0].upper(),
                    "session": pred_s,
                    "pred": d.get("du_doan") or d.get("Du_doan"),
                    "rate": d.get("ty_le_thang", "88.5%"),
                    "live_phien": prev_s,
                    "live_kq": _normalize_kq(d.get("ket_qua") or d.get("ket_qua_phien")),
                }

            prev_s = _clean_session_code(
                d.get("phien_hien_tai") or d.get("Phien_Hien_tai") or d.get("phien_truoc")
            )
            pred_s = _clean_session_code(
                d.get("Phien_du_doan") or d.get("phien_du_doan") or d.get("phien_ke_tiep")
            )
            if not pred_s or (prev_s and pred_s == prev_s):
                pred_s = _next_session_code(prev_s)

            return {
                "game": tool_type.split("_")[0].upper(),
                "session": pred_s,
                "pred": d.get("Du_doan") or d.get("du_doan"),
                "dice": (f"{d.get('Xuc_xac1')}-{d.get('Xuc_xac2')}-{d.get('Xuc_xac3')}"
                         if d.get("Xuc_xac1") else None),
                "total": d.get("Tong") or d.get("tong_diem"),
                "rate": d.get("ty_le_thang", "89.2%"),
                "live_phien": prev_s,
                "live_kq": _normalize_kq(
                    d.get("ket_qua") or d.get("Ket_qua")
                    or d.get("ket_qua_phien") or d.get("Du_doan_hien_tai")),
            }
    except Exception:
        return None

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    data = load_datakey()
    uid = ensure_user(data, user)
    u = data["users"][uid]
    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return
    await update.message.reply_text(
        build_main_header(user, u, data),
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard(user.id, data)
    )

# --- ADMIN COMMANDS ---
async def handle_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if len(args) < 1:
        return await update.message.reply_text(f"{E_ALERT} Dùng: <code>/key &lt;số_ngày&gt;</code>", parse_mode="HTML")
    try:
        days = int(args[0])
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        data.setdefault("keys", {})[key] = {
            "days": days, "used": False,
            "created_at": get_hanoi_time().isoformat(), "used_by": None
        }
        save_datakey(data)
        await update.message.reply_text(
            f"{E_PARTY} <b>Tạo Key {days} ngày thành công:</b> {E_CROWN}\n<code>{key}</code>",
            parse_mode="HTML"
        )
    except ValueError:
        await update.message.reply_text(f"{E_NO} Số ngày không hợp lệ!", parse_mode="HTML")

async def handle_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text(f"{E_ALERT} Dùng: <code>/approve &lt;request_id&gt; &lt;số_tiền&gt;</code>", parse_mode="HTML")
    try:
        req_id = args[0]
        amount = int(args[1])
    except ValueError:
        return await update.message.reply_text(f"{E_NO} Tham số không hợp lệ!", parse_mode="HTML")
    req = data.get("deposit_requests", {}).get(req_id)
    if not req:
        return await update.message.reply_text(f"{E_NO} Không tìm thấy yêu cầu nạp!", parse_mode="HTML")
    if req.get("status") not in ("pending", "awaiting_admin"):
        return await update.message.reply_text(f"{E_NO} Yêu cầu đã {req.get('status')}!", parse_mode="HTML")
    uid_str = req["user_id"]
    data["users"].setdefault(uid_str, {"balance": 0, "first_name": "N/A"})
    data["users"][uid_str]["balance"] = data["users"][uid_str].get("balance", 0) + amount
    req["status"] = "approved"
    req["approved_at"] = get_hanoi_time().isoformat()
    req["approved_amount"] = amount
    save_datakey(data)
    await update.message.reply_text(
        f"{E_OK} <b>Đã duyệt đơn #{req_id}</b> {E_PARTY}\n"
        f"{E_PIN} User: <code>{uid_str}</code>\n"
        f"{E_MONEY} Cộng: <code>{amount:,}đ</code>\n"
        f"{E_CASH} Số dư mới: <code>{data['users'][uid_str]['balance']:,}đ</code>",
        parse_mode="HTML"
    )
    try:
        await context.bot.send_message(
            int(uid_str),
            f"{E_PARTY} <b>NẠP TIỀN THÀNH CÔNG!</b> {E_MONEY}\n"
            f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
            f"{E_CASH} Cộng: <code>+{amount:,}đ</code>\n"
            f"{E_CROWN} Số dư hiện tại: <code>{data['users'][uid_str]['balance']:,}đ</code>",
            parse_mode="HTML"
        )
    except Exception:
        pass

async def handle_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    args = context.args
    if not args:
        return await update.message.reply_text(f"{E_ALERT} Dùng: <code>/broadcast &lt;tin_nhắn&gt;</code>", parse_mode="HTML")
    message = " ".join(args)
    users = data.get("users", {})
    sent_count = 0
    for user_id in users.keys():
        try:
            await context.bot.send_message(
                int(user_id), f"{E_MEGA} <b>THÔNG BÁO TỪ ADMIN:</b> {E_FIRE}\n\n{message}", parse_mode="HTML"
            )
            sent_count += 1
        except Exception:
            continue
    await update.message.reply_text(
        f"{E_OK} <b>Đã gửi broadcast tới {sent_count}/{len(users)} người dùng.</b> {E_PARTY}",
        parse_mode="HTML"
    )

async def handle_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_datakey()
    if not is_admin(update.effective_user.id, data):
        return
    await update.message.reply_text(build_stats_text(data), parse_mode="HTML")

def build_stats_text(data=None):
    if data is None:
        data = load_datakey()
    total_users = len(data.get("users", {}))
    active_users = sum(1 for u in data.get("users", {}).values() if is_key_active(u, None, data))
    active_keys = sum(1 for k in data.get("keys", {}).values() if not k.get("used", False))
    used_keys = sum(1 for k in data.get("keys", {}).values() if k.get("used", False))
    pending_dep = sum(1 for r in data.get("deposit_requests", {}).values()
                      if r.get("status") in ("pending", "awaiting_admin"))
    pending_fk = sum(1 for r in data.get("free_key_requests", {}).values()
                     if r.get("status") == "awaiting_admin")
    sub_count = len(data.get("sub_admins", []))
    revenue = 0
    for k in data.get("keys", {}).values():
        if k.get("used", False):
            d = k.get("days", 0)
            if d == 1:
                revenue += 40000
            elif d == 3:
                revenue += 60000
            elif d >= 9999:
                revenue += 120000
    return (
        f"{E_MON} <b>THỐNG KÊ HỆ THỐNG</b> {E_FIRE}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} Tổng Users: <code>{total_users}</code>\n"
        f"{E_CROWN} Đang có VIP: <code>{active_users}</code>\n"
        f"{E_GEAR} Admin phụ: <code>{sub_count}</code>\n"
        f"{E_OK} Key đã dùng: <code>{used_keys}</code>\n"
        f"{E_GIFT} Key còn trống: <code>{active_keys}</code>\n"
        f"{E_SPIN} Đơn nạp chờ duyệt: <code>{pending_dep}</code>\n"
        f"{E_BELL} Đơn Free Key 3h chờ duyệt: <code>{pending_fk}</code>\n"
        f"{E_CASH} Tổng doanh thu Key: <code>{revenue:,}đ</code> {E_MONEY}"
    )

# --- KEYBOARDS (GIỮ NGUYÊN MENU GAME 100%) ---
def get_main_inline_keyboard(user_id, data=None):
    kb = [
        [InlineKeyboardButton("Danh Sách Game VIP", callback_data="menu_games", api_kwargs=btn_icon("game"))],
        [
            InlineKeyboardButton("Hồ Sơ Cá Nhân", callback_data="menu_profile", api_kwargs=btn_icon("clip")),
            InlineKeyboardButton("Mua Gói Key VIP", callback_data="menu_buykey", api_kwargs=btn_icon("bag"))
        ],
        [
            InlineKeyboardButton("Get Key Free 3h", callback_data="menu_freekey", api_kwargs=btn_icon("gift")),
            InlineKeyboardButton("Kích Hoạt Key", callback_data="menu_activate", api_kwargs=btn_icon("crown"))
        ],
        [
            InlineKeyboardButton("Nạp Tiền Ví", callback_data="menu_deposit", api_kwargs=btn_icon("money")),
            InlineKeyboardButton("Nhập Giftcode", callback_data="menu_giftcode", api_kwargs=btn_icon("party"))
        ],
        [
            InlineKeyboardButton("Lịch Sử Mua KEY", callback_data="menu_history", api_kwargs=btn_icon("calendar")),
            InlineKeyboardButton("Hỗ Trợ Khác", callback_data="menu_support", api_kwargs=btn_icon("net"))
        ],
        [
            InlineKeyboardButton("Feedback Tool", callback_data="menu_feedback", api_kwargs=btn_icon("bell")),
        ],
    ]
    if is_admin(user_id, data):
        kb.append([InlineKeyboardButton("ADMIN TOOLS QUẢN TRỊ", callback_data="admin_tools", api_kwargs=btn_icon("gear"))])
    return InlineKeyboardMarkup(kb)

def get_game_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("SUNWIN", callback_data="game_SUNWIN", api_kwargs=btn_icon("sunwin")),
            InlineKeyboardButton("HITCLUB", callback_data="game_HITCLUB", api_kwargs=btn_icon("hitclub"))
        ],
        [
            InlineKeyboardButton("B52 CLUB", callback_data="game_B52", api_kwargs=btn_icon("b52_logo")),
            InlineKeyboardButton("BETVIP", callback_data="game_BETVIP", api_kwargs=btn_icon("betvip_logo"))
        ],
        [
            InlineKeyboardButton("LC79", callback_data="game_LC79", api_kwargs=btn_icon("lc79_logo")),
            InlineKeyboardButton("XOCDIA88", callback_data="game_XD88", api_kwargs=btn_icon("xd88_logo"))
        ],
        [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ])

def get_sub_inline_keyboard(game):
    menus = {
        "SUNWIN": [
            [
                InlineKeyboardButton("SUNWIN TÀI XỈU", callback_data="run_sun_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("SUNWIN SICBO", callback_data="run_sun_sb", api_kwargs=btn_icon("table_sicbo"))
            ]
        ],
        "HITCLUB": [
            [
                InlineKeyboardButton("HIT TÀI XỈU", callback_data="run_hit_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("HIT MD5", callback_data="run_hit_md5", api_kwargs=btn_icon("table_md5"))
            ],
            [InlineKeyboardButton("HIT SICBO", callback_data="run_hit_sb", api_kwargs=btn_icon("table_sicbo"))]
        ],
        "B52": [
            [
                InlineKeyboardButton("B52 TÀI XỈU", callback_data="run_b52_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("B52 MD5", callback_data="run_b52_md5", api_kwargs=btn_icon("table_md5"))
            ],
            [InlineKeyboardButton("B52 SICBO", callback_data="run_b52_sb", api_kwargs=btn_icon("table_sicbo"))]
        ],
        "BETVIP": [
            [
                InlineKeyboardButton("BETVIP TÀI XỈU", callback_data="run_betvip_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("BETVIP MD5", callback_data="run_betvip_md5", api_kwargs=btn_icon("table_md5"))
            ]
        ],
        "LC79": [
            [
                InlineKeyboardButton("LC79 TÀI XỈU", callback_data="run_lc79_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("LC79 MD5", callback_data="run_lc79_md5", api_kwargs=btn_icon("table_md5"))
            ]
        ],
        "XD88": [
            [
                InlineKeyboardButton("XD88 TÀI XỈU", callback_data="run_xd88_tx", api_kwargs=btn_icon("table_tx")),
                InlineKeyboardButton("XD88 MD5", callback_data="run_xd88_md5", api_kwargs=btn_icon("table_md5"))
            ]
        ],
    }
    kb = [row[:] for row in menus.get(game, [])]
    kb.append([InlineKeyboardButton("Quay Lại", callback_data="menu_games", api_kwargs=btn_icon("down"))])
    return InlineKeyboardMarkup(kb)

def get_admin_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Tạo Giftcode", callback_data="admin_giftcode", api_kwargs=btn_icon("gift")),
            InlineKeyboardButton("Tạo Key VIP", callback_data="admin_createkey", api_kwargs=btn_icon("crown"))
        ],
        [
            InlineKeyboardButton("Thống Kê", callback_data="admin_stats", api_kwargs=btn_icon("monitor")),
            InlineKeyboardButton("Broadcast", callback_data="admin_broadcast", api_kwargs=btn_icon("mega"))
        ],
        [
            InlineKeyboardButton("Đơn Nạp Chờ", callback_data="admin_deposits", api_kwargs=btn_icon("money")),
            InlineKeyboardButton("Danh Sách User", callback_data="admin_users", api_kwargs=btn_icon("clip"))
        ],
        [
            InlineKeyboardButton("Add / Xóa Admin Phụ", callback_data="admin_manage_sub", api_kwargs=btn_icon("gear")),
        ],
        [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ])

def get_back_keyboard(target="menu_back", label="Quay Lại"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=target, api_kwargs=btn_icon("down"))]])

def get_deposit_keyboard(req_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tôi Đã Chuyển Khoản", callback_data=f"dep_sent:{req_id}", api_kwargs=btn_icon("check"))],
        [InlineKeyboardButton("Hủy Yêu Cầu Nạp", callback_data=f"dep_cancel:{req_id}", api_kwargs=btn_icon("cross"))],
    ])

def get_admin_deposit_keyboard(req_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Duyệt Đơn", callback_data=f"dep_ok:{req_id}", api_kwargs=btn_icon("check")),
            InlineKeyboardButton("Từ Chối", callback_data=f"dep_no:{req_id}", api_kwargs=btn_icon("cross"))
        ],
    ])

def get_admin_freekey_keyboard(req_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Duyệt Key 3h", callback_data=f"fk_ok:{req_id}", api_kwargs=btn_icon("check")),
            InlineKeyboardButton("Từ Chối", callback_data=f"fk_no:{req_id}", api_kwargs=btn_icon("cross"))
        ],
    ])

async def send_photos_to_admins(bot, data, photo_file_ids, caption, reply_markup=None):
    """Gửi đầy đủ 1 hoặc nhiều ảnh tới Admin chính & Admin phụ."""
    if not photo_file_ids:
        return
    recipients = {int(ADMIN_ID)} | {int(x) for x in data.get("sub_admins", [])}
    chunks = [photo_file_ids[i:i + 10] for i in range(0, len(photo_file_ids), 10)]
    for aid in recipients:
        try:
            if len(photo_file_ids) == 1:
                await bot.send_photo(
                    chat_id=aid,
                    photo=photo_file_ids[0],
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            else:
                for c_idx, chunk in enumerate(chunks):
                    media = []
                    for idx, fid in enumerate(chunk):
                        if c_idx == 0 and idx == 0:
                            media.append(InputMediaPhoto(media=fid, caption=caption, parse_mode="HTML"))
                        else:
                            media.append(InputMediaPhoto(media=fid))
                    await bot.send_media_group(chat_id=aid, media=media)
                if reply_markup:
                    await bot.send_message(
                        chat_id=aid,
                        text=f"{E_CROWN} <b>Thao tác xử lý ({len(photo_file_ids)} ảnh ở trên):</b> {E_FIRE}",
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
        except Exception as e:
            logging.warning("Send photos to admin %s failed: %s", aid, e)
            continue

def can_claim_free_key(uid_str, data):
    last_claim = data.get("free_key_claims", {}).get(uid_str)
    if not last_claim:
        return True, None
    t = parse_hanoi_time(last_claim)
    if not t:
        return True, None
    next_available = t + timedelta(hours=24)
    now = get_hanoi_time()
    if now < next_available:
        return False, next_available
    return True, None

def issue_free_3h_key(uid_str, data):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    now = get_hanoi_time()
    data.setdefault("keys", {})[key] = {
        "days": 0,
        "hours": 3,
        "used": False,
        "created_at": now.isoformat(),
        "used_by": None,
        "free_key": True,
        "claimed_by": uid_str,
    }
    data.setdefault("free_key_claims", {})[uid_str] = now.isoformat()
    save_datakey(data)
    return key

async def submit_freekey_photos_for_review(bot, chat_id, user, uid_str, photo_file_ids, note=""):
    data = load_datakey()
    allowed, next_dt = can_claim_free_key(uid_str, data)
    if not allowed:
        return await bot.send_message(
            chat_id=chat_id,
            text=f"{E_NO} Bạn đã nhận Key Free 3h rồi. Lượt tiếp theo lúc: <code>{next_dt.strftime('%d/%m/%Y %H:%M')}</code> {E_BELL}",
            parse_mode="HTML",
            reply_markup=get_main_inline_keyboard(user.id, data)
        )

    req_id = next_freekey_id(data)
    now_iso = get_hanoi_time().isoformat()
    data.setdefault("free_key_requests", {})[str(req_id)] = {
        "user_id": uid_str,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "photo_file_ids": photo_file_ids,
        "photo_file_id": photo_file_ids[0],
        "note": note,
        "status": "awaiting_admin",
        "created_at": now_iso,
    }
    save_datakey(data)

    note_line = f"\n{E_CLIP} Ghi chú: <i>{note}</i>" if note else ""
    admin_caption = (
        f"{E_GIFT} <b>YÊU CẦU DUYỆT KEY FREE 3H #{req_id}</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} User: <code>{uid_str}</code> (@{user.username or 'no_username'})\n"
        f"{E_CLIP} Tên: <b>{user.first_name or 'Vô Danh'}</b>\n"
        f"{E_PIN} Số ảnh gửi: <b>{len(photo_file_ids)} ảnh</b> — Rải <code>{FREE_KEY_BOT}</code> vào tối thiểu 3 box {E_FIRE}{note_line}"
    )
    await send_photos_to_admins(
        bot,
        data,
        photo_file_ids,
        admin_caption,
        reply_markup=get_admin_freekey_keyboard(req_id)
    )

    return await bot.send_message(
        chat_id=chat_id,
        text=f"{E_OK} <b>ĐÃ GỬI {len(photo_file_ids)} HÌNH ẢNH CHỜ ADMIN DUYỆT TAY!</b> {E_PARTY}\n"
             f"━━━━━━━━━━━━━━━━━━━━\n"
             f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
             f"{E_GIFT} Toàn bộ <b>{len(photo_file_ids)} ảnh</b> chứng minh rải <code>{FREE_KEY_BOT}</code> đã được chuyển tới Admin.\n"
             f"{E_CROWN} Sau khi Admin duyệt, bot sẽ tự động gửi <b>Key Free 3h</b> cho bạn.",
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard(user.id, data)
    )

async def handle_admin_freekey_callback(update, context, action, req_id):
    q = update.callback_query
    data = load_datakey()
    if not is_admin(q.from_user.id, data):
        return await q.answer("Chỉ Admin mới có quyền duyệt!", show_alert=True)

    req = data.get("free_key_requests", {}).get(str(req_id))
    if not req:
        return await q.answer("Yêu cầu không tồn tại.", show_alert=True)
    if req.get("status") != "awaiting_admin":
        return await q.answer(f"Yêu cầu đã xử lý ({req.get('status')}).", show_alert=True)

    uid_str = req["user_id"]
    if action == "no":
        req["status"] = "rejected"
        req["reviewed_at"] = get_hanoi_time().isoformat()
        req["reviewed_by"] = q.from_user.id
        save_datakey(data)
        msg_done = f"{E_NO} <b>Đã từ chối yêu cầu Key Free 3h #{req_id}</b> (User: <code>{uid_str}</code>)."
        try:
            await q.edit_message_caption(caption=msg_done, parse_mode="HTML")
        except Exception:
            await q.edit_message_text(text=msg_done, parse_mode="HTML")
        try:
            await context.bot.send_message(
                int(uid_str),
                f"{E_NO} <b>YÊU CẦU KEY FREE 3H #{req_id} BỊ TỪ CHỐI</b> {E_ALERT}\n"
                f"Vui lòng kiểm tra lại ảnh chứng minh rải <code>{FREE_KEY_BOT}</code> vào tối thiểu 3 box hoặc liên hệ {ADMIN_HANDLE}.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    if action == "ok":
        allowed, next_dt = can_claim_free_key(uid_str, data)
        if not allowed:
            req["status"] = "rejected"
            save_datakey(data)
            return await q.answer("User này đã nhận Key Free 3h trong 24h qua!", show_alert=True)

        key = issue_free_3h_key(uid_str, data)
        req["status"] = "approved"
        req["issued_key"] = key
        req["reviewed_at"] = get_hanoi_time().isoformat()
        req["reviewed_by"] = q.from_user.id
        save_datakey(data)

        msg_done = (
            f"{E_OK} <b>Đã duyệt & gửi Key Free 3h #{req_id}</b> {E_PARTY}\n"
            f"{E_PIN} User: <code>{uid_str}</code>\n"
            f"{E_GIFT} Key 3h: <code>{key}</code>"
        )
        try:
            await q.edit_message_caption(caption=msg_done, parse_mode="HTML")
        except Exception:
            await q.edit_message_text(text=msg_done, parse_mode="HTML")
        try:
            await context.bot.send_message(
                int(uid_str),
                f"{E_PARTY} <b>ADMIN ĐÃ DUYỆT KEY FREE 3H!</b> {E_GIFT}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
                f"{E_CROWN} Mã KEY 3h: <code>{key}</code>\n"
                f"{E_BELL} Thời hạn: <b>3 giờ</b> {E_FIRE}\n\n"
                f"{E_OK} Vào <b>Kích Hoạt Key</b> và dán mã trên để sử dụng ngay!",
                parse_mode="HTML"
            )
        except Exception:
            pass

# --- DEPOSIT FLOW ---
async def open_deposit(chat_id, user, context):
    data = load_datakey()
    uid = ensure_user(data, user)
    req_id = next_request_id(data)
    data.setdefault("deposit_requests", {})[str(req_id)] = {
        "user_id": uid,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "status": "pending",
        "created_at": get_hanoi_time().isoformat(),
        "approved_at": None,
        "approved_amount": None,
    }
    save_datakey(data)

    caption = (
        f"{E_MONEY} <b>CỔNG NẠP TIỀN TỰ ĐỘNG</b> {E_CASH}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n\n"
        f"{E_CROWN} 1. Quét mã QR bên trên và chuyển khoản.\n"
        f"{E_CASH} 2. Nội dung CK bắt buộc: <code>NAP{req_id}</code>\n"
        f"{E_OK} 3. Bấm nút <b>Tôi Đã Chuyển Khoản</b> bên dưới để Admin cộng tiền.\n\n"
        f"{E_FIRE} <i>Hệ thống xử lý siêu tốc trong 1-3 phút!</i>"
    )
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=QR_URL,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_deposit_keyboard(req_id)
    )

async def handle_deposit_callback(update, context, action, req_id):
    q = update.callback_query
    uid = str(q.from_user.id)
    data = load_datakey()
    req = data.get("deposit_requests", {}).get(req_id)
    if not req:
        return await q.edit_message_caption(
            caption=f"{E_NO} Yêu cầu nạp không tồn tại.", parse_mode="HTML"
        )
    if req["user_id"] != uid:
        return await q.answer("Yêu cầu không thuộc tài khoản này!", show_alert=True)

    if action == "cancel":
        if req["status"] == "pending":
            req["status"] = "cancelled"
            save_datakey(data)
        return await q.edit_message_caption(
            caption=f"{E_NO} <b>Đã hủy yêu cầu nạp #{req_id}.</b>\nGõ /start để quay lại menu chính.",
            parse_mode="HTML"
        )

    if action == "sent":
        if req["status"] != "pending":
            return await q.answer("Yêu cầu này đã được gửi hoặc xử lý rồi!", show_alert=True)
        req["status"] = "awaiting_admin"
        req["user_confirmed_at"] = get_hanoi_time().isoformat()
        save_datakey(data)
        await q.edit_message_caption(
            caption=f"{E_OK} <b>ĐÃ GHI NHẬN THANH TOÁN!</b> {E_PARTY}\n"
                    f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
                    f"{E_CROWN} Admin sẽ kiểm tra và cộng tiền ngay cho bạn!",
            parse_mode="HTML"
        )
        recipients = {int(ADMIN_ID)} | {int(x) for x in data.get("sub_admins", [])}
        dep_text = (
            f"{E_MONEY} <b>YÊU CẦU NẠP TIỀN MỚI #{req_id}</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PARTY} User: <code>{uid}</code> (@{req['username'] or 'no_username'})\n"
            f"{E_CLIP} Tên: <b>{req['first_name']}</b>\n"
            f"{E_BELL} Thời gian: <code>{req['user_confirmed_at']}</code>\n"
            f"{E_CASH} Nội dung CK: <code>NAP{req_id}</code> {E_FIRE}"
        )
        for aid in recipients:
            try:
                await context.bot.send_message(
                    chat_id=aid,
                    text=dep_text,
                    parse_mode="HTML",
                    reply_markup=get_admin_deposit_keyboard(req_id)
                )
            except Exception:
                continue
        return

async def handle_admin_deposit_callback(update, context, action, req_id):
    q = update.callback_query
    data = load_datakey()
    if not is_admin(q.from_user.id, data):
        return await q.answer("Chỉ Admin mới có quyền này!", show_alert=True)
    req = data.get("deposit_requests", {}).get(req_id)
    if not req:
        return await q.answer("Yêu cầu không tồn tại.", show_alert=True)
    if req["status"] not in ("awaiting_admin", "pending"):
        return await q.answer(f"Đơn này đã ở trạng thái: {req['status']}", show_alert=True)

    if action == "no":
        req["status"] = "rejected"
        req["approved_at"] = get_hanoi_time().isoformat()
        save_datakey(data)
        await q.edit_message_text(
            text=f"{E_NO} <b>Đã từ chối đơn nạp #{req_id}</b>", parse_mode="HTML"
        )
        try:
            await context.bot.send_message(
                int(req["user_id"]),
                f"{E_NO} <b>YÊU CẦU NẠP TIỀN BỊ TỪ CHỐI</b> {E_ALERT}\n"
                f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
                f"{E_BELL} Vui lòng liên hệ {ADMIN_HANDLE} để được hỗ trợ.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    if action == "ok":
        await q.edit_message_text(
            text=f"{E_OK} <b>Đang duyệt đơn #{req_id}</b> {E_CROWN}\n"
                 f"{E_MONEY} Vui lòng nhập số tiền cần cộng cho User <code>{req['user_id']}</code> (VD: 50000):",
            parse_mode="HTML"
        )
        context.user_data["admin_approve_req"] = req_id
        context.user_data["waiting_approve_amount"] = True
        return

async def handle_approve_amount(update, context):
    msg = update.message.text.strip()
    try:
        amount = int(msg.replace(",", "").replace(".", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await update.message.reply_text(f"{E_NO} Số tiền không hợp lệ! Nhập lại số nguyên dương:", parse_mode="HTML")
    req_id = context.user_data.get("admin_approve_req")
    context.user_data.pop("waiting_approve_amount", None)
    context.user_data.pop("admin_approve_req", None)
    if not req_id:
        return await update.message.reply_text(f"{E_NO} Không có yêu cầu chờ duyệt!", parse_mode="HTML")
    data = load_datakey()
    req = data.get("deposit_requests", {}).get(str(req_id))
    if not req or req["status"] not in ("awaiting_admin", "pending"):
        return await update.message.reply_text(f"{E_NO} Yêu cầu không hợp lệ hoặc đã xử lý!", parse_mode="HTML")
    uid_str = req["user_id"]
    data["users"].setdefault(uid_str, {"balance": 0, "first_name": "N/A"})
    data["users"][uid_str]["balance"] = data["users"][uid_str].get("balance", 0) + amount
    req["status"] = "approved"
    req["approved_at"] = get_hanoi_time().isoformat()
    req["approved_amount"] = amount
    save_datakey(data)
    await update.message.reply_text(
        f"{E_PARTY} <b>Đã duyệt đơn #{req_id}</b> {E_OK}\n"
        f"{E_PIN} User: <code>{uid_str}</code>\n"
        f"{E_MONEY} Cộng: <code>+{amount:,}đ</code>\n"
        f"{E_CASH} Số dư mới: <code>{data['users'][uid_str]['balance']:,}đ</code>",
        parse_mode="HTML",
        reply_markup=get_admin_inline_keyboard()
    )
    try:
        await context.bot.send_message(
            int(uid_str),
            f"{E_PARTY} <b>NẠP TIỀN THÀNH CÔNG!</b> {E_MONEY}\n"
            f"{E_PIN} Mã yêu cầu: <code>#{req_id}</code>\n"
            f"{E_CASH} Cộng: <code>+{amount:,}đ</code>\n"
            f"{E_CROWN} Số dư hiện tại: <code>{data['users'][uid_str]['balance']:,}đ</code>",
            parse_mode="HTML"
        )
    except Exception:
        pass

async def forward_feedback_to_admin(bot, chat_id, user, photo_file_ids=None, content_text=""):
    photo_list = photo_file_ids or []
    uid = user.id
    data = load_datakey()
    safe_content = content_text.strip() if content_text else "(Không có nội dung chữ)"
    count_info = f"<b>{len(photo_list)} ảnh</b>" if photo_list else "<b>không có ảnh</b>"
    admin_caption = (
        f"{E_BELL} <b>FEEDBACK MỚI TỪ USER</b> {E_CROWN}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PARTY} Tên: <b>{user.first_name}</b> (@{user.username or 'no_username'})\n"
        f"{E_PIN} ID: <code>{uid}</code>\n"
        f"{E_CLIP} Đính kèm: {count_info} {E_FIRE}\n"
        f"{E_MEGA} Nội dung:\n<i>{safe_content}</i>"
    )
    if photo_list:
        await send_photos_to_admins(bot, data, photo_list, admin_caption)
    else:
        recipients = {int(ADMIN_ID)} | {int(x) for x in data.get("sub_admins", [])}
        for aid in recipients:
            try:
                await bot.send_message(chat_id=aid, text=admin_caption, parse_mode="HTML")
            except Exception:
                continue

    summary_part = f"<b>{len(photo_list)} ảnh + nội dung</b>" if photo_list else "<b>nội dung</b>"
    await bot.send_message(
        chat_id=chat_id,
        text=f"{E_PARTY} <b>GỬI FEEDBACK THÀNH CÔNG!</b> {E_OK}\n"
             f"━━━━━━━━━━━━━━━━━━━━\n"
             f"{E_CROWN} Đã chuyển y hệt {summary_part} tới Admin.\n"
             f"{E_FIRE} Cảm ơn bạn đã đóng góp cho hệ thống!",
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard(uid, data)
    )

def _schedule_album_debounce(context, chat_id, user, uid_str, group_key, mode):
    old_task = MEDIA_GROUP_TIMERS.get(group_key)
    if old_task and not old_task.done():
        old_task.cancel()

    async def _worker():
        try:
            await asyncio.sleep(1.2)
        except asyncio.CancelledError:
            return
        MEDIA_GROUP_TIMERS.pop(group_key, None)
        MEDIA_GROUP_ACTIVE_MODE.pop(group_key, None)
        photo_ids = MEDIA_GROUP_BUFFERS.pop(group_key, [])
        cap_final = MEDIA_GROUP_CAPTIONS.pop(group_key, "")
        if not photo_ids:
            return

        if mode == "freekey":
            context.user_data.pop("waiting_freekey_photo", None)
            await submit_freekey_photos_for_review(
                context.bot, chat_id, user, uid_str, photo_ids, note=cap_final
            )
        elif mode == "feedback":
            if cap_final:
                context.user_data.pop("waiting_feedback", None)
                context.user_data.pop("feedback_photo_ids", None)
                await forward_feedback_to_admin(
                    context.bot, chat_id, user, photo_file_ids=photo_ids, content_text=cap_final
                )
            else:
                existing = context.user_data.get("feedback_photo_ids", [])
                existing.extend(photo_ids)
                context.user_data["feedback_photo_ids"] = existing
                context.user_data["waiting_feedback"] = True
                kb = [
                    [InlineKeyboardButton(f"Gửi {len(existing)} Ảnh Ngay", callback_data="fb_send_photo_only", api_kwargs=btn_icon("check"))],
                    [InlineKeyboardButton("Hủy Feedback", callback_data="menu_back", api_kwargs=btn_icon("down"))],
                ]
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{E_OK} <b>Đã nhận {len(existing)} ảnh feedback!</b> {E_PARTY}\n"
                         f"Hãy nhập <b>nội dung mô tả</b> vào khung chat, hoặc bấm nút gửi ảnh ngay bên dưới:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(kb)
                )

    MEDIA_GROUP_TIMERS[group_key] = asyncio.create_task(_worker())

# --- HANDLE PHOTO MESSAGE ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_datakey()
    uid = ensure_user(data, user)

    photo = update.message.photo[-1]
    caption = (update.message.caption or "").strip()
    media_group_id = update.message.media_group_id

    if media_group_id:
        for prefix, m_name in (("fk", "freekey"), ("fb", "feedback")):
            g_key = f"{prefix}:{uid}:{media_group_id}"
            if MEDIA_GROUP_ACTIVE_MODE.get(g_key) == m_name:
                MEDIA_GROUP_BUFFERS.setdefault(g_key, []).append(photo.file_id)
                if caption:
                    MEDIA_GROUP_CAPTIONS[g_key] = caption
                _schedule_album_debounce(
                    context, update.effective_chat.id, user, uid, g_key, m_name
                )
                return

    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return

    if context.user_data.get("waiting_freekey_photo"):
        if media_group_id:
            group_key = f"fk:{uid}:{media_group_id}"
            MEDIA_GROUP_ACTIVE_MODE[group_key] = "freekey"
            MEDIA_GROUP_BUFFERS[group_key] = [photo.file_id]
            if caption:
                MEDIA_GROUP_CAPTIONS[group_key] = caption
            _schedule_album_debounce(
                context, update.effective_chat.id, user, uid, group_key, "freekey"
            )
            return

        context.user_data.pop("waiting_freekey_photo", None)
        return await submit_freekey_photos_for_review(
            context.bot, update.effective_chat.id, user, uid, [photo.file_id], note=caption
        )

    if not context.user_data.get("waiting_feedback"):
        return

    if media_group_id:
        group_key = f"fb:{uid}:{media_group_id}"
        MEDIA_GROUP_ACTIVE_MODE[group_key] = "feedback"
        MEDIA_GROUP_BUFFERS[group_key] = [photo.file_id]
        if caption:
            MEDIA_GROUP_CAPTIONS[group_key] = caption
        _schedule_album_debounce(
            context, update.effective_chat.id, user, uid, group_key, "feedback"
        )
        return

    if caption:
        context.user_data.pop("waiting_feedback", None)
        context.user_data.pop("feedback_photo_ids", None)
        return await forward_feedback_to_admin(
            context.bot, update.effective_chat.id, user, photo_file_ids=[photo.file_id], content_text=caption
        )

    existing_ids = context.user_data.get("feedback_photo_ids", [])
    existing_ids.append(photo.file_id)
    context.user_data["feedback_photo_ids"] = existing_ids
    kb = [
        [InlineKeyboardButton(f"Gửi {len(existing_ids)} Ảnh Ngay", callback_data="fb_send_photo_only", api_kwargs=btn_icon("check"))],
        [InlineKeyboardButton("Hủy Feedback", callback_data="menu_back", api_kwargs=btn_icon("down"))],
    ]
    await update.message.reply_text(
        f"{E_OK} <b>Đã nhận {len(existing_ids)} ảnh feedback!</b> {E_PARTY}\n"
        f"Bây giờ hãy nhập <b>nội dung mô tả</b> vào khung chat, hoặc bấm nút gửi ảnh ngay bên dưới:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# --- HANDLE TEXT INPUT ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    user = update.effective_user
    uid = user.id
    data = load_datakey()
    uid_str = ensure_user(data, user)

    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=False)
    if blocked:
        return

    if context.user_data.get("waiting_approve_amount"):
        return await handle_approve_amount(update, context)

    if context.user_data.get("waiting_freekey_photo"):
        return await update.message.reply_text(
            f"{E_ALERT} Vui lòng <b>gửi hình ảnh</b> chứng minh đã rải <code>{FREE_KEY_BOT}</code> vào tối thiểu 3 box để Admin duyệt tay.",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

    
    if context.user_data.get("waiting_sub_admin"):
        context.user_data.pop("waiting_sub_admin", None)
        if not is_admin(uid, data):
            return
        try:
            target_id = int(msg)
            if target_id == ADMIN_ID:
                return await update.message.reply_text(
                    f"{E_ALERT} ID này là Admin chính.",
                    parse_mode="HTML",
                    reply_markup=get_admin_inline_keyboard()
                )
            sub_list = [int(x) for x in data.get("sub_admins", [])]
            if target_id in sub_list:
                sub_list.remove(target_id)
                data["sub_admins"] = sub_list
                save_datakey(data)
                status_text = f"{E_NO} Đã gỡ quyền Admin phụ cho ID <code>{target_id}</code>."
            else:
                sub_list.append(target_id)
                data["sub_admins"] = sub_list
                save_datakey(data)
                status_text = f"{E_OK} Đã thêm Admin phụ ID <code>{target_id}</code> (full quyền quản trị như Admin chính)."
            return await update.message.reply_text(
                status_text,
                parse_mode="HTML",
                reply_markup=get_admin_inline_keyboard()
            )
        except ValueError:
            return await update.message.reply_text(
                f"{E_NO} ID không hợp lệ! Vui lòng nhập số ID Telegram.",
                parse_mode="HTML",
                reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
            )

    
    if context.user_data.get("waiting_for_giftcode"):
        try:
            amount = int(msg.replace(",", "").replace(".", ""))
            if amount <= 0:
                await update.message.reply_text(f"{E_NO} Số tiền phải lớn hơn 0!", parse_mode="HTML")
                return
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            data.setdefault("giftcodes", {})[code] = {
                "amount": amount, "created_at": get_hanoi_time().isoformat(),
                "created_by": uid, "used_by": None, "used_at": None, "is_used": False,
            }
            save_datakey(data)
            context.user_data["waiting_for_giftcode"] = False
            await update.message.reply_text(
                f"{E_GIFT} <b>ĐÃ TẠO GIFTCODE THÀNH CÔNG!</b> {E_PARTY}\n\n"
                f"{E_MONEY} Giá trị: <code>{amount:,}đ</code>\n"
                f"{E_PIN} Mã code: <code>{code}</code>",
                parse_mode="HTML", reply_markup=get_admin_inline_keyboard()
            )
        except ValueError:
            await update.message.reply_text(f"{E_NO} Vui lòng nhập số tiền hợp lệ!", parse_mode="HTML")
        return

    if context.user_data.get("awaiting_key"):
        key = msg.upper()
        if key in data.get("keys", {}) and not data["keys"][key].get("used"):
            kinfo = data["keys"][key]
            now = get_hanoi_time()
            cur_exp = parse_hanoi_time(data["users"][uid_str].get("key_expires"))
            base_time = cur_exp if (cur_exp and cur_exp > now) else now
            if kinfo.get("hours"):
                exp = base_time + timedelta(hours=int(kinfo["hours"]))
                duration_label = f"{int(kinfo['hours'])} giờ"
            else:
                days = kinfo["days"]
                exp = base_time + timedelta(days=days)
                duration_label = f"{days} ngày"

            data["users"][uid_str]["key_expires"] = exp.isoformat()
            data["keys"][key].update({
                "used": True, "used_by": uid_str, "used_at": now.isoformat()
            })
            save_datakey(data)
            context.user_data["awaiting_key"] = False
            await update.message.reply_text(
                f"{E_PARTY} <b>KÍCH HOẠT KEY THÀNH CÔNG!</b> {E_CROWN}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_PIN} Key: <code>{key}</code>\n"
                f"{E_CAL} Thời hạn: <code>{duration_label}</code>\n"
                f"{E_BELL} Hết hạn lúc: <code>{exp.strftime('%d/%m/%Y %H:%M')}</code> {E_FIRE}",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data)
            )
        else:
            context.user_data["awaiting_key"] = False
            await update.message.reply_text(
                f"{E_NO} <b>Key không tồn tại hoặc đã được sử dụng!</b>",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data)
            )
        return

    # User nhập Giftcode
    if context.user_data.get("waiting_giftcode_input"):
        gc = msg.upper()
        if gc in data.get("giftcodes", {}):
            info = data["giftcodes"][gc]
            if info.get("is_used", False):
                context.user_data["waiting_giftcode_input"] = False
                await update.message.reply_text(
                    f"{E_NO} <b>Giftcode này đã có người sử dụng!</b>",
                    parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data)
                )
            else:
                amount = info["amount"]
                data["users"][uid_str]["balance"] = data["users"][uid_str].get("balance", 0) + amount
                info.update({
                    "is_used": True, "used_by": uid_str, "used_at": get_hanoi_time().isoformat()
                })
                save_datakey(data)
                context.user_data["waiting_giftcode_input"] = False
                await update.message.reply_text(
                    f"{E_PARTY} <b>NHẬP GIFTCODE THÀNH CÔNG!</b> {E_GIFT}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{E_MONEY} Cộng ví: <code>+{amount:,}đ</code>\n"
                    f"{E_CASH} Số dư hiện tại: <code>{data['users'][uid_str]['balance']:,}đ</code> {E_CROWN}",
                    parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data)
                )
        else:
            context.user_data["waiting_giftcode_input"] = False
            await update.message.reply_text(
                f"{E_NO} <b>Mã Giftcode không hợp lệ!</b>",
                parse_mode="HTML", reply_markup=get_main_inline_keyboard(uid, data)
            )
        return

    # User gửi Feedback
    if context.user_data.get("waiting_feedback"):
        photo_ids = context.user_data.pop("feedback_photo_ids", [])
        context.user_data["waiting_feedback"] = False
        return await forward_feedback_to_admin(
            context.bot, update.effective_chat.id, user, photo_file_ids=photo_ids, content_text=msg
        )

    # Admin tạo Key
    if context.user_data.get("waiting_create_key"):
        try:
            days = int(msg)
            if days <= 0:
                await update.message.reply_text(f"{E_NO} Số ngày phải lớn hơn 0!", parse_mode="HTML")
                return
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
            data.setdefault("keys", {})[key] = {
                "days": days, "used": False,
                "created_at": get_hanoi_time().isoformat(), "used_by": None
            }
            save_datakey(data)
            context.user_data["waiting_create_key"] = False
            await update.message.reply_text(
                f"{E_PARTY} <b>ĐÃ TẠO KEY THÀNH CÔNG!</b> {E_CROWN}\n\n"
                f"{E_PIN} Key: <code>{key}</code>\n"
                f"{E_CAL} Số ngày: <code>{days} ngày</code>",
                parse_mode="HTML", reply_markup=get_admin_inline_keyboard()
            )
        except ValueError:
            await update.message.reply_text(f"{E_NO} Vui lòng nhập số ngày hợp lệ!", parse_mode="HTML")
        return

    # Admin Broadcast
    if context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        users = data.get("users", {})
        sent_count, failed = 0, 0
        status = await update.message.reply_text(f"{E_SPIN} Đang gửi broadcast...", parse_mode="HTML")
        for target in users.keys():
            try:
                await context.bot.send_message(
                    int(target),
                    f"{E_MEGA} <b>THÔNG BÁO TỪ ADMIN:</b> {E_FIRE}\n\n{msg}",
                    parse_mode="HTML"
                )
                sent_count += 1
                if sent_count % 10 == 0:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=status.message_id,
                        text=f"{E_SPIN} Đang gửi... ({sent_count}/{len(users)})",
                        parse_mode="HTML"
                    )
                await asyncio.sleep(0.08)
            except Exception:
                failed += 1
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, message_id=status.message_id,
            text=f"{E_PARTY} <b>Broadcast hoàn tất!</b> {E_OK}\n"
                 f"{E_OK} Thành công: <code>{sent_count}</code>\n"
                 f"{E_NO} Thất bại: <code>{failed}</code>",
            parse_mode="HTML",
            reply_markup=get_admin_inline_keyboard()
        )
        return

# --- CALLBACK ROUTER ---
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data_tag = q.data
    user = q.from_user
    uid = str(user.id)
    data = load_datakey()
    ensure_user(data, user)
    u = data["users"][uid]

    if data_tag == "check_3box_ok":
        ok, missing_box, reason, checked_count = await check_3box_membership(context.bot, user.id)
        if not ok:
            detail = reason or f"Chưa vào box: {missing_box}"
            await q.answer(detail[:200], show_alert=True)
            return await send_3box_gate(q, edit=True, reason=reason)
        u["verified_3box"] = True
        save_datakey(data)
        await q.answer(f"Xác nhận thành công ({checked_count}/3 box)!", show_alert=False)
        return await q.edit_message_text(
            build_main_header(user, u, data),
            parse_mode="HTML",
            reply_markup=get_main_inline_keyboard(user.id, data)
        )

    await q.answer()
    blocked, _ = await enforce_3box_or_block(update, context, user, data, is_callback=True)
    if blocked:
        return

    if data_tag.startswith("fk_"):
        parts = data_tag.split(":")
        if len(parts) == 2:
            action, req_id = parts
            if action == "fk_ok":
                return await handle_admin_freekey_callback(update, context, "ok", req_id)
            if action == "fk_no":
                return await handle_admin_freekey_callback(update, context, "no", req_id)
        return

    if data_tag == "fb_send_photo_only":
        photo_ids = context.user_data.pop("feedback_photo_ids", [])
        context.user_data.pop("waiting_feedback", None)
        if not photo_ids:
            return await q.edit_message_text(
                f"{E_NO} Không tìm thấy ảnh feedback!",
                parse_mode="HTML",
                reply_markup=get_main_inline_keyboard(user.id, data)
            )
        admin_caption = (
            f"{E_BELL} <b>FEEDBACK {len(photo_ids)} ẢNH MỚI TỪ USER</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PARTY} Tên: <b>{user.first_name}</b> (@{user.username or 'no_username'})\n"
            f"{E_PIN} ID: <code>{uid}</code>\n"
            f"{E_CLIP} Nội dung: <i>(Chỉ gửi {len(photo_ids)} ảnh)</i> {E_FIRE}"
        )
        await send_photos_to_admins(context.bot, data, photo_ids, admin_caption)
        return await q.edit_message_text(
            f"{E_PARTY} <b>Đã gửi y hệt {len(photo_ids)} ảnh feedback tới Admin thành công!</b> {E_OK}",
            parse_mode="HTML",
            reply_markup=get_main_inline_keyboard(user.id, data)
        )

    for state_key in [
        "waiting_for_giftcode", "awaiting_key", "waiting_giftcode_input",
        "waiting_create_key", "waiting_broadcast", "waiting_feedback",
        "feedback_photo_ids", "waiting_freekey_photo", "waiting_sub_admin"
    ]:
        context.user_data.pop(state_key, None)

    if data_tag.startswith("dep_"):
        parts = data_tag.split(":")
        if len(parts) != 2:
            return
        action, req_id = parts
        if action == "dep_sent":
            return await handle_deposit_callback(update, context, "sent", req_id)
        if action == "dep_cancel":
            return await handle_deposit_callback(update, context, "cancel", req_id)
        if action == "dep_ok":
            return await handle_admin_deposit_callback(update, context, "ok", req_id)
        if action == "dep_no":
            return await handle_admin_deposit_callback(update, context, "no", req_id)
        return

    if data_tag == "menu_freekey":
        allowed, next_dt = can_claim_free_key(uid, data)
        if not allowed:
            return await q.edit_message_text(
                f"{E_NO} <b>BẠN ĐÃ NHẬN KEY FREE 3H HÔM NAY</b> {E_ALERT}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Vui lòng quay lại sau: <code>{next_dt.strftime('%d/%m/%Y %H:%M')}</code> {E_BELL}",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
        context.user_data["waiting_freekey_photo"] = True
        return await q.edit_message_text(
            f"{E_GIFT} <b>GET KEY FREE 3 GIỜ (ADMIN DUYỆT TAY)</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_FIRE} 1. Rải link/nội dung kèm <code>{FREE_KEY_BOT}</code> vào <b>tối thiểu 3 box</b>.\n"
            f"{E_CLIP} 2. <b>Gửi hình ảnh</b> (1 hoặc nhiều ảnh) chứng minh đã rải vào khung chat ngay bây giờ.\n"
            f"{E_OK} 3. Admin sẽ kiểm tra đủ ảnh và duyệt tay — sau khi duyệt, bot gửi <b>Key 3h</b> cho bạn.\n\n"
            f"<i>Mẫu rải box:</i>\n"
            f"<code>Tool soi cầu real-time miễn phí tại {FREE_KEY_BOT}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

    if data_tag == "menu_back":
        return await q.edit_message_text(
            build_main_header(user, u, data),
            parse_mode="HTML",
            reply_markup=get_main_inline_keyboard(user.id, data)
        )

    if data_tag == "menu_games":
        return await q.edit_message_text(
            f"{E_GAME} <b>CHỌN GAME ĐỂ SOI CẦU:</b> {E_FIRE}\n"
            f"<i>(Danh sách cổng game có API hoạt động Real-Time)</i>",
            parse_mode="HTML",
            reply_markup=get_game_inline_keyboard()
        )

    if data_tag.startswith("game_"):
        game = data_tag.split("_")[1]
        game_icons = {
            "SUNWIN": E_SUNWIN, "HITCLUB": E_HITCLUB, "B52": E_B52,
            "BETVIP": E_BETVIP, "LC79": E_LC79, "XD88": E_XD88
        }
        g_icon = game_icons.get(game, E_GAME)
        return await q.edit_message_text(
            f"{g_icon} <b>CHỌN BÀN CHƠI {game}:</b> {E_TABLE_TX}\n"
            f"<i>{E_TABLE_MD5} Chọn chế độ muốn phân tích cầu bên dưới {E_TABLE_SB}:</i>",
            parse_mode="HTML",
            reply_markup=get_sub_inline_keyboard(game)
        )

    if data_tag == "menu_profile":
        msg = build_info_block(user, u, data=data)
        return await q.edit_message_text(msg, parse_mode="HTML", reply_markup=get_back_keyboard())

    if data_tag == "menu_buykey":
        kb = [
            [InlineKeyboardButton("Gói 1 Ngày — 40,000đ", callback_data="buy_1d", api_kwargs=btn_icon("money"))],
            [InlineKeyboardButton("Gói 3 Ngày — 60,000đ", callback_data="buy_3d", api_kwargs=btn_icon("fire"))],
            [InlineKeyboardButton("Gói Vĩnh Viễn — 120,000đ", callback_data="buy_forever", api_kwargs=btn_icon("crown"))],
            [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
        ]
        return await q.edit_message_text(
            f"{E_BAG} <b>BẢNG GIÁ GÓI KEY VIP</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_MONEY} Số dư ví hiện tại: <code>{u.get('balance', 0):,}đ</code> {E_CASH}\n\n"
            f"{E_TABLE_TX} <b>Gói 1 Ngày:</b> <code>40,000đ</code>\n"
            f"{E_FIRE} <b>Gói 3 Ngày:</b> <code>60,000đ</code>\n"
            f"{E_CROWN} <b>Gói Vĩnh Viễn:</b> <code>120,000đ</code>\n\n"
            f"<i>Bấm chọn gói bên dưới để mua tự động:</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    if data_tag.startswith("buy_"):
        pkgs = {
            "buy_1d": {"days": 1, "price": 40000, "name": "1 Ngày"},
            "buy_3d": {"days": 3, "price": 60000, "name": "3 Ngày"},
            "buy_forever": {"days": 9999, "price": 120000, "name": "Vĩnh Viễn"},
        }
        p = pkgs.get(data_tag)
        if not p:
            return
        balance = u.get("balance", 0)
        if balance < p["price"]:
            return await q.answer(f"Số dư không đủ! Cần {p['price']:,}đ (Hiện có {balance:,}đ)", show_alert=True)
        u["balance"] = balance - p["price"]
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        now = get_hanoi_time()
        data.setdefault("keys", {})[key] = {
            "days": p["days"], "used": False,
            "created_at": now.isoformat(), "used_by": None, "bought_by": uid
        }
        data.setdefault("history", []).append({
            "user_id": uid, "package": p["name"], "price": p["price"],
            "key": key, "time": now.isoformat()
        })
        save_datakey(data)
        kb = [
            [InlineKeyboardButton("Kích Hoạt Key Ngay", callback_data="menu_activate", api_kwargs=btn_icon("crown"))],
            [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
        ]
        return await q.edit_message_text(
            f"{E_PARTY} <b>MUA KEY VIP THÀNH CÔNG!</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_BAG} Gói đã mua: <b>{p['name']}</b>\n"
            f"{E_PIN} Mã KEY: <code>{key}</code>\n"
            f"{E_MONEY} Số dư còn lại: <code>{u['balance']:,}đ</code> {E_CASH}\n\n"
            f"{E_OK} Bấm <b>Kích Hoạt Key Ngay</b> và dán mã key trên để sử dụng!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    if data_tag == "menu_activate":
        context.user_data["awaiting_key"] = True
        return await q.edit_message_text(
            f"{E_CROWN} <b>KÍCH HOẠT KEY VIP</b> {E_FIRE}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_GIFT} Vui lòng nhập hoặc dán <b>MÃ KEY (15 ký tự)</b> của bạn vào khung chat:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

    if data_tag == "menu_deposit":
        try:
            await q.message.delete()
        except Exception:
            pass
        return await open_deposit(q.message.chat_id, user, context)

    if data_tag == "menu_giftcode":
        context.user_data["waiting_giftcode_input"] = True
        return await q.edit_message_text(
            f"{E_GIFT} <b>NHẬP GIFTCODE NHẬN TIỀN</b> {E_PARTY}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_MONEY} Vui lòng nhập <b>MÃ GIFTCODE</b> vào khung chat để cộng tiền vào ví:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

    if data_tag == "menu_history":
        user_hist = [h for h in data.get("history", []) if str(h.get("user_id")) == uid]
        if not user_hist:
            text = (
                f"{E_CAL} <b>LỊCH SỬ MUA KEY</b> {E_CROWN}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_NO} Bạn chưa có giao dịch mua Key nào!"
            )
        else:
            lines = [f"{E_CAL} <b>LỊCH SỬ MUA KEY (10 GẦN NHẤT)</b> {E_CROWN}", "━━━━━━━━━━━━━━━━━━━━"]
            for idx, item in enumerate(reversed(user_hist[-10:]), 1):
                t_obj = parse_hanoi_time(item.get("time"))
                t_str = t_obj.strftime('%d/%m %H:%M') if t_obj else "—"
                lines.append(
                    f"{E_PIN} {idx}. <b>{item['package']}</b> (<code>{item['price']:,}đ</code>) — <code>{t_str}</code>\n"
                    f"   {E_GIFT} Key: <code>{item['key']}</code>"
                )
            text = "\n".join(lines)
        return await q.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())

    if data_tag == "menu_support":
        text = (
            f"{E_NET} <b>TRUNG TÂM HỖ TRỢ KHÁCH HÀNG</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_BELL} <b>Kênh Thông Báo:</b> {CHANNEL_THONG_BAO}\n"
            f"{E_MEGA} <b>Nhóm Chat Giao Lưu:</b> {CHANNEL_CHAT}\n"
            f"{E_CASH} <b>Kênh Check Bill Nạp:</b> {CHANNEL_BILL}\n"
            f"{E_CROWN} <b>Admin Hỗ Trợ Trực Tiếp:</b> {ADMIN_HANDLE} {E_FIRE}\n\n"
            f"{E_OK} <i>Hỗ trợ nạp rút, cấp key & giải đáp thắc mắc 24/7!</i>"
        )
        return await q.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())

    if data_tag == "menu_feedback":
        context.user_data["waiting_feedback"] = True
        return await q.edit_message_text(
            f"{E_BELL} <b>GỬI FEEDBACK / GÓP Ý TOOL</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_CLIP} Bạn có thể gửi:\n"
            f"• <b>1 hoặc nhiều ảnh kèm nội dung</b> (caption)\n"
            f"• Hoặc <b>gửi ảnh trước, nhập nội dung sau</b>\n"
            f"• Hoặc <b>nhập nội dung chữ</b> trực tiếp\n\n"
            f"{E_OK} <i>Khách gửi bao nhiêu ảnh, bot chuyển y hệt bấy nhiêu ảnh tới Admin!</i> {E_FIRE}",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

    # --- ADMIN PANEL ---
    if data_tag == "admin_tools" and is_admin(user.id, data):
        return await q.edit_message_text(
            f"{E_GEAR} <b>BẢNG ĐIỀU KHIỂN ADMIN</b> {E_CROWN}",
            parse_mode="HTML",
            reply_markup=get_admin_inline_keyboard()
        )

    if data_tag == "admin_manage_sub" and is_admin(user.id, data):
        context.user_data["waiting_sub_admin"] = True
        sub_list = data.get("sub_admins", [])
        sub_display = ", ".join(f"<code>{x}</code>" for x in sub_list) if sub_list else "<i>Chưa có</i>"
        return await q.edit_message_text(
            f"{E_GEAR} <b>QUẢN LÝ ADMIN PHỤ</b> {E_CROWN}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Admin chính: <code>{ADMIN_ID}</code>\n"
            f"Danh sách Admin phụ hiện tại: {sub_display}\n\n"
            f"Nhập <b>ID người dùng</b> để thêm mới hoặc gỡ quyền Admin phụ (Admin phụ có đầy đủ chức năng quản trị):",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_giftcode" and is_admin(user.id, data):
        context.user_data["waiting_for_giftcode"] = True
        return await q.edit_message_text(
            f"{E_GIFT} <b>TẠO GIFTCODE MỚI</b> {E_PARTY}\nNhập số tiền cho Giftcode (VD: 50000):",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_createkey" and is_admin(user.id, data):
        context.user_data["waiting_create_key"] = True
        return await q.edit_message_text(
            f"{E_CROWN} <b>TẠO KEY VIP MỚI</b> {E_FIRE}\nNhập số ngày sử dụng (VD: 1, 3, 30, 9999):",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_broadcast" and is_admin(user.id, data):
        context.user_data["waiting_broadcast"] = True
        return await q.edit_message_text(
            f"{E_MEGA} <b>GỬI THÔNG BÁO TOÀN SERVER</b> {E_BELL}\nNhập nội dung muốn gửi tới tất cả User:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_stats" and is_admin(user.id, data):
        return await q.edit_message_text(
            build_stats_text(data),
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_deposits" and is_admin(user.id, data):
        reqs = data.get("deposit_requests", {})
        pending_list = [(k, v) for k, v in reqs.items() if v.get("status") in ("pending", "awaiting_admin")]
        if not pending_list:
            return await q.edit_message_text(
                f"{E_OK} <b>Hiện không có đơn nạp nào đang chờ duyệt!</b> {E_PARTY}",
                parse_mode="HTML",
                reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
            )
        lines = [f"{E_MONEY} <b>DANH SÁCH ĐƠN NẠP CHỜ DUYỆT</b> {E_CASH}", "━━━━━━━━━━━━━━━━━━━━"]
        for rid, rinfo in pending_list[-10:]:
            lines.append(
                f"• Đơn <code>#{rid}</code> | User: <code>{rinfo['user_id']}</code> (@{rinfo.get('username') or 'none'})\n"
                f"  Trạng thái: <b>{rinfo['status']}</b> | Duyệt nhanh: <code>/approve {rid} &lt;tiền&gt;</code>"
            )
        return await q.edit_message_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    if data_tag == "admin_users" and is_admin(user.id, data):
        users_dict = data.get("users", {})
        lines = [f"{E_CLIP} <b>DANH SÁCH USER ({len(users_dict)} NGƯỜI)</b> {E_CROWN}", "━━━━━━━━━━━━━━━━━━━━"]
        for uid_item, uinfo in list(users_dict.items())[-15:]:
            vip_tag = "VIP" if is_key_active(uinfo, int(uid_item), data) else "Thường"
            lines.append(
                f"• <code>{uid_item}</code> | <b>{uinfo.get('first_name', 'N/A')}</b> | "
                f"Ví: <code>{uinfo.get('balance', 0):,}đ</code> | {vip_tag}"
            )
        return await q.edit_message_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=get_back_keyboard("admin_tools", "Quay Lại Admin")
        )

    # --- CHẠY API SOI CẦU ---
    if data_tag.startswith("run_"):
        if not is_key_active(u, user.id, data):
            kb = [
                [InlineKeyboardButton("Get Key Free 3h", callback_data="menu_freekey", api_kwargs=btn_icon("gift"))],
                [InlineKeyboardButton("Mua Gói Key VIP", callback_data="menu_buykey", api_kwargs=btn_icon("bag"))],
                [InlineKeyboardButton("Kích Hoạt Key", callback_data="menu_activate", api_kwargs=btn_icon("crown"))],
                [InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))],
            ]
            return await q.edit_message_text(
                f"{E_ALERT} <b>BẠN CHƯA CÓ KEY VIP HOẶC KEY ĐÃ HẾT HẠN!</b> {E_NO}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Vui lòng nhận Key Free 3h, mua gói Key hoặc nhập mã Key để mở khóa Tool soi cầu.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(kb)
            )

        api_key = data_tag.split("run_")[1]
        table_icon = E_TABLE_SB if api_key.endswith("_sb") else (E_TABLE_MD5 if api_key.endswith("_md5") else E_TABLE_TX)
        table_btn_key = "table_sicbo" if api_key.endswith("_sb") else ("table_md5" if api_key.endswith("_md5") else "table_tx")

        await q.edit_message_text(
            f"{E_SPIN} <b>Đang kết nối máy chủ {api_key.upper()} & phân tích dữ liệu...</b> {table_icon}",
            parse_mode="HTML"
        )
        res = await fetch_api_data(API_URLS.get(api_key), api_key)
        if not res:
            kb = [
                [InlineKeyboardButton("Thử Lại Ngay", callback_data=data_tag, api_kwargs=btn_icon(table_btn_key))],
                [InlineKeyboardButton("Chọn Game Khác", callback_data="menu_games", api_kwargs=btn_icon("game"))],
            ]
            return await q.edit_message_text(
                f"{E_NO} <b>Máy chủ API {api_key.upper()} đang bảo trì hoặc không phản hồi!</b>\n"
                f"<i>Vui lòng thử lại sau vài giây hoặc chọn bàn khác.</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(kb)
            )

        if res.get("live_phien") and res.get("live_kq"):
            record_result(api_key, res["live_phien"], res["live_kq"])
        if res.get("session") and res.get("pred"):
            record_result(api_key, res["session"], None, pred=res["pred"])

        u["analysis_count"] = u.get("analysis_count", 0) + 1
        save_datakey(data)

        game_map_name = {
            "sun_tx": "SUNWIN TÀI XỈU", "sun_sb": "SUNWIN SICBO",
            "hit_tx": "HITCLUB TÀI XỈU", "hit_md5": "HITCLUB MD5", "hit_sb": "HITCLUB SICBO",
            "b52_tx": "B52 TÀI XỈU", "b52_md5": "B52 MD5", "b52_sb": "B52 SICBO",
            "betvip_tx": "BETVIP TÀI XỈU", "betvip_md5": "BETVIP MD5",
            "xd88_tx": "XOCDIA88 TÀI XỈU", "xd88_md5": "XOCDIA88 MD5",
            "lc79_tx": "LC79 TÀI XỈU", "lc79_md5": "LC79 MD5",
        }
        full_game_name = game_map_name.get(api_key, res["game"])
        prev_session = res.get("live_phien") or "-"
        prev_result = res.get("live_kq") or "Đang cập nhật"
        pred_session = res.get("session") or "-"
        pred_choice = str(res.get("pred") or "-").upper()
        win_rate = res.get("rate") or "89.2%"

        lines = [
            f"{table_icon} <b>BÀN CHƠI:</b> <b>{full_game_name}</b> {E_FIRE}",
            f"{E_CAL} <b>PHIÊN TRƯỚC:</b> <code>#{prev_session}</code> <i>({prev_result})</i>",
            f"{E_PIN} <b>PHIÊN DỰ ĐOÁN:</b> <code>#{pred_session}</code> {table_icon}",
        ]
        if res.get("dice"):
            lines.append(f"{E_DICE3D} <b>XÚC XẮC GẦN NHẤT:</b> <code>{res['dice']}</code>")
        if res.get("total"):
            lines.append(f"{E_PCT} <b>TỔNG ĐIỂM:</b> <code>{res['total']}</code>")
        lines.append(f"{E_FIRE} <b>CHỐT CẦU:</b> <code>{pred_choice}</code> {E_CROWN}")
        lines.append(f"{E_CASH} <b>TỈ LỆ THẮNG:</b> <code>{win_rate}</code> {E_PARTY}")

        body = "\n".join(lines)
        info = build_info_block(user, u, game_name=full_game_name, data=data)
        msg = (
            f"{info}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            f"{E_CROWN} <b>━━━ KẾT QUẢ PHÂN TÍCH ━━━</b> {E_CROWN}\n"
            f"{body}"
        )
        kb = [
            [InlineKeyboardButton("Soi Tiếp Phiên Sau", callback_data=data_tag, api_kwargs=btn_icon(table_btn_key))],
            [
                InlineKeyboardButton("Đổi Bàn / Game", callback_data="menu_games", api_kwargs=btn_icon("game")),
                InlineKeyboardButton("Quay Lại", callback_data="menu_back", api_kwargs=btn_icon("down"))
            ],
        ]
        return await q.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

# --- MAIN ---
def main():
    init_datakey_file()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("key", handle_key_command))
    app.add_handler(CommandHandler("approve", handle_approve_command))
    app.add_handler(CommandHandler("broadcast", handle_broadcast_command))
    app.add_handler(CommandHandler("stats", handle_stats_command))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    print("Bot đang khởi động...")
    print(f"Admin ID: {ADMIN_ID}")
    print("Bắt đầu polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()