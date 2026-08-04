import asyncio
import random
import sys
import traceback
import re
from datetime import datetime
from gc import get_objects
from time import time
from uuid import uuid4
from pyrogram.enums import ParseMode
import requests
from pyrogram.helpers import ikb
from pyrogram.raw.functions import Ping
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultAnimation,
    InlineQueryResultArticle,
    InlineQueryResultCachedAnimation,
    InlineQueryResultCachedAudio,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedSticker,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedVoice,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    InputTextMessageContent,
)

from config import API_MAELYN, BOT_ID, BOT_NAME, HELPABLE, SUDO_OWNERS
from kelra import bot, kelra
from kelra.database import dB, state
from kelra.helpers import (
    CMD,
    ButtonUtils,
    Message,
    Tools,
    get_time,
    paginate_modules,
    query_fonts,
    start_time,
)
from kelra.logger import logger
from plugins.pmpermit import DEFAULT_TEXT, LIMIT


# ==========================================
# LOGIC KATEGORI PREMIUM UNTUK INLINE HELP
# ==========================================
def clean_category_name(raw_name):
    # Membersihkan tag <emoji> HANYA untuk di dalam tombol
    return re.sub(r'<emoji id=\d+>(.*?)</emoji>', r'\1', raw_name).strip()

def get_categories():
    categories = {}
    for mod in sorted(HELPABLE):
        raw_cat = getattr(HELPABLE[mod], "__CATEGORY__", None)
        if not raw_cat:
            continue
            
        clean_cat = clean_category_name(raw_cat)
        if clean_cat not in categories:
            categories[clean_cat] = []
        categories[clean_cat].append(mod)
    return categories

def get_category_menu(page=0):
    categories = get_categories()
    cat_list = list(categories.keys())
    buttons = []
    
    per_page = 6
    total_pages = (len(cat_list) + per_page - 1) // per_page if len(cat_list) > 0 else 1
    start = page * per_page
    end = start + per_page
    current_cats = cat_list[start:end]
    
    for i in range(0, len(current_cats), 2):
        clean_cat1 = current_cats[i]
        row = [InlineKeyboardButton(text=clean_cat1, callback_data=f"cat_{clean_cat1[:30]}", style="primary")]
        
        if i + 1 < len(current_cats):
            clean_cat2 = current_cats[i+1]
            row.append(InlineKeyboardButton(text=clean_cat2, callback_data=f"cat_{clean_cat2[:30]}", style="primary"))
        buttons.append(row)
        
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"cat_page_{page-1}", style="primary"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"cat_page_{page+1}", style="primary"))
        
    if nav_row:
        buttons.append(nav_row)
        
    return InlineKeyboardMarkup(buttons)


# ==========================================
# HANDLER UTAMA INLINE QUERY
# ==========================================
@CMD.INLINE()
async def _(client, inline_query):
    try:
        text = inline_query.query.strip().lower()
        logger.info(f"INLINE QUERY = {text}")
        if not text:
            return
        answers = []
        if text.split()[0] == "help":
            answerss = await get_inline_help(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "alive":
            answerss = await alive_inline(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.startswith("jaseb_menu_"):
            answerss = await jaseb_inline_menu(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_send":
            tuju = text.split()[1]
            answerss = await send_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_copy":
            tuju = text.split()[1]
            answerss = await copy_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "make_button":
            tuju = text.split()[1]
            answerss = await button_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "pmpermit_inline":
            answerss = await pmpermit_inline(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "copy_inline":
            answerss = await copy_inline_msg(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "user_info":
            answerss = await user_inline(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "gc_info":
            answerss = await gc_inline(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "get_note":
            answerss = await get_inline_note(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_eval":
            answerss = await inline_eval(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_font":
            answerss = await inline_font(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_cat":
            answerss = await inline_cat(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_bola":
            answerss = await inline_bola(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "get_users":
            answerss = await get_kelra_user(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_textpro":
            answerss = await inline_textpro(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_ttsearch":
            answerss = await inline_ttsearch(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_ttdownload":
            answerss = await inline_ttdownload(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_spotify":
            answerss = await inline_spotify(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_pinsearch":
            answerss = await inline_pinsearch(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_news":
            answerss = await inline_news(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_music":
            answerss = await inline_music_cb(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_playsearch":
            answerss = await inline_playsearch_cb(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)
        elif text.split()[0] == "inline_cancel":
            answerss = await cancel_gcast_inline(answers, inline_query)
            return await client.answer_inline_query(inline_query.id, results=answerss, cache_time=0)

    except Exception:
        logger.error(f"{traceback.format_exc()}")


# ==========================================
# FUNGSI BANTUAN INLINE
# ==========================================
async def jaseb_inline_menu(result, inline_query):
    user_id = int(inline_query.query.split("_")[2])
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ 5 Mnt", callback_data=f"jsb_start_{user_id}_300", style="primary"),
            InlineKeyboardButton("⏱ 10 Mnt", callback_data=f"jsb_start_{user_id}_600", style="primary"),
            InlineKeyboardButton("⏱ 15 Mnt", callback_data=f"jsb_start_{user_id}_900", style="primary")
        ],
        [
            InlineKeyboardButton("⏱ 30 Mnt", callback_data=f"jsb_start_{user_id}_1800", style="primary"),
            InlineKeyboardButton("⏱ 45 Mnt", callback_data=f"jsb_start_{user_id}_2700", style="primary"),
            InlineKeyboardButton("⏳ 1 Jam", callback_data=f"jsb_start_{user_id}_3600", style="primary")
        ],
        [
            InlineKeyboardButton("⏳ 2 Jam", callback_data=f"jsb_start_{user_id}_7200", style="primary"),
            InlineKeyboardButton("⏳ 3 Jam", callback_data=f"jsb_start_{user_id}_10800", style="primary"),
            InlineKeyboardButton("⏳ 6 Jam", callback_data=f"jsb_start_{user_id}_21600", style="primary")
        ],
        [
            InlineKeyboardButton("🛑 Matikan Jaseb", callback_data=f"jsb_cancel_{user_id}", style="danger")
        ]
    ])
    
    result.append(
        InlineQueryResultArticle(
            title="Menu Jaseb",
            input_message_content=InputTextMessageContent(
                "<blockquote><b>⚙️ JASEB AUTO-BROADCAST</b>\n\n"
                "Silakan pilih durasi interval pengiriman ke semua grup:</blockquote>",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=buttons
        )
    )
    return result


async def cancel_gcast_inline(result, inline_query):
    query = inline_query.query.split()
    if len(query) < 3:
        return result
    
    task_id = query[1]
    msg_id = query[2]
    
    msg = f"<i>Task running #<code>{task_id}</code>. Click button for cancel task!</i>"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Cancel Task", callback_data=f"cancel_task {task_id}", style="danger")],
        [InlineKeyboardButton("Close", callback_data="close_gcast", style="danger")]
    ])
    
    result.append(
        InlineQueryResultArticle(
            title="Cancel Task",
            input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True),
            reply_markup=buttons
        )
    )
    return result


async def inline_music_cb(result, inline_query):
    user_id = inline_query.from_user.id
    data = state.get(user_id, "NOW_PLAYING")
    if not data:
        return result
    
    chat_id = data["chat_id"]
    owner_id = data["user_id"]
    caption = data["caption"]
    photo_url = data["photo_url"]
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"mpause|{chat_id}|{owner_id}", style="danger"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"mresume|{chat_id}|{owner_id}", style="success")
        ],
        [
            InlineKeyboardButton("⏭ Skip", callback_data=f"mskip|{chat_id}|{owner_id}", style="primary"),
            InlineKeyboardButton("⏹ Stop", callback_data=f"mstop|{chat_id}|{owner_id}", style="danger")
        ],
        [
            InlineKeyboardButton("📜 Playlist", callback_data=f"mplaylist|{chat_id}|{owner_id}", style="primary")
        ]
    ])
    
    result.append(
        InlineQueryResultPhoto(
            photo_url=photo_url,
            title="Now Playing",
            caption=caption, parse_mode=ParseMode.HTML,
            reply_markup=buttons
        )
    )
    return result


async def inline_playsearch_cb(result, inline_query):
    query_split = inline_query.query.split()
    if len(query_split) < 3: return result
    client_id = int(query_split[1])
    uniq = query_split[2]
    
    search_results = state.get(client_id, f"SEARCH_{uniq}")
    if not search_results: return result
    
    buttons = []
    for i, res in enumerate(search_results):
        title = res.get("title", "Unknown")[:30]
        duration = res.get("duration", "-")
        channel = res.get("channel", "Unknown")[:15]
        button_text = f"{i+1}. {title} | {duration} | {channel}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"pselect|{client_id}|{uniq}|{i}", style="primary")])
    buttons.append([InlineKeyboardButton("❌ Batal", callback_data=f"close_playsearch|{client_id}", style="danger")])
    
    result.append(
        InlineQueryResultArticle(
            title="Play Search",
            input_message_content=InputTextMessageContent("🔍 **Silakan pilih lagu yang ingin diputar:**"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    )
    return result


async def inline_news(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    try:
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next", callback_data=f"news_1_{uniq}", style="primary")]])
        date = data[0].get("berita_diupload", "-")
        foto = data[0]["berita_thumb"]
        judul = f"**Title:** {data[0]['berita']}\n**Link:** {data[0]['berita_url']}\n**Uploaded:** {date}"
        results.append(
            InlineQueryResultPhoto(
                photo_url=foto,
                caption=judul,
                title="Inline News",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline news: {traceback.format_exc()}")


async def inline_pinsearch(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    try:
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next", callback_data=f"nxpinsearch_1_{uniq}", style="primary")]])
        results.append(
            InlineQueryResultPhoto(
                photo_url=data[0],
                title="Inline Pinterest",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline result pindl: {traceback.format_exc()}")


async def inline_ttdownload(results, inline):
    userid = inline.from_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Download Video", callback_data=f"cqtiktok_videodl_{userid}", style="primary"),
            InlineKeyboardButton("Download Audio", callback_data=f"cqtiktok_audiodl_{userid}", style="success"),
        ]
    ])
    results.append(
        InlineQueryResultArticle(
            title="Tiktok Inline Download!",
            reply_markup=keyboard,
            input_message_content=InputTextMessageContent("<blockquote><b>Please select the button below you want to download!</b></blockquote>", parse_mode=ParseMode.HTML),
        )
    )
    return results


async def inline_spotify(results, inline):
    userid = inline.from_user.id
    uniq = str(inline.query.split()[1])
    data = state.get(userid, uniq)
    state.set(userid, "fordlspotify", data[0]["url"])
    try:
        for audio in data:
            caption = f"""
<blockquote expandable>🎶 **Title:** {audio['title']}
👥 **Popularity:** {audio['popularity']}
⏳ **Duration:** {audio['duration']}
🖇️ **Spotify URL:** <a href='{audio['url']}'>here</a></blockquote>"""
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("Download audio", callback_data=f"dlspot_{userid}_{uniq}", style="success")],
                [InlineKeyboardButton("Next audio", callback_data=f"nxtspotify_1_{userid}_{uniq}", style="primary")],
            ])
            results.append(
                InlineQueryResultArticle(
                    title="Tiktok Inline Download!",
                    reply_markup=buttons,
                    input_message_content=InputTextMessageContent(caption, disable_web_page_preview=True),
                )
            )
        return results
    except Exception:
        logger.error(f"Inline result spotify: {traceback.format_exc()}")


async def inline_ttsearch(results, inline):
    userid = inline.from_user.id
    uniq = str(inline.query.split()[1])
    data = state.get(userid, uniq)
    try:
        for video in data:
            title = video["title"] or "-"
            video_link = video["play"]
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Next video", callback_data=f"nxttsearch_1_{userid}_{uniq}", style="primary")]])
            caption = f"<blockquote>{title}</blockquote>"
            results.append(
                InlineQueryResultVideo(
                    video_url=video_link,
                    title=title,
                    caption=caption, parse_mode=ParseMode.HTML,
                    reply_markup=buttons,
                )
            )
        return results
    except Exception:
        logger.error(f"Inline result ttdl: {traceback.format_exc()}")


async def inline_bola(resultss, inline_query):
    url = f"https://api.maelyn.tech/api/jadwalbola?apikey={API_MAELYN}"
    result = await Tools.fetch.get(url)
    uniq = f"{str(uuid4())}"
    if result.status_code == 200:
        data = result.json()
        if data["status"] == "Success":
            buttons = []
            temp_row = []
            state.set(uniq.split("-")[0], uniq.split("-")[0], data["result"])
            for liga_date in data["result"]:
                button = InlineKeyboardButton(
                    text=liga_date["LigaDate"],
                    callback_data=f"bola_matches {uniq.split('-')[0]} {liga_date['LigaDate']}",
                    style="primary"
                )
                temp_row.append(button)

                if len(temp_row) == 3:
                    buttons.append(temp_row)
                    temp_row = []

            if temp_row:
                buttons.append(temp_row)
            last_row = [
                InlineKeyboardButton(text="« Back", callback_data=f"bola_date {uniq.split('-')[0]}", style="primary"),
                InlineKeyboardButton(text="Close", callback_data="close inline_bola", style="danger"),
            ]
            buttons.append(last_row)
            keyboard = InlineKeyboardMarkup(buttons)

            resultss.append(
                InlineQueryResultArticle(
                    title="Football Schedule",
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent("<b>Select a date to view football matches:</b>", parse_mode=ParseMode.HTML),
                )
            )
    return resultss


async def get_kelra_user(result, inline_query):
    try:
        msg = await Message.userbot(0)
        buttons = ButtonUtils.userbot(kelra._ubot[0].me.id, 0)
        result.append(
            InlineQueryResultArticle(
                title="get user Inline!",
                reply_markup=buttons,
                input_message_content=InputTextMessageContent(msg),
            )
        )

        return result
    except Exception:
        logger.error(f"Line 209:\n {traceback.format_exc()}")


async def inline_textpro(result, inline):
    try:
        userid = inline.from_user.id
        text = state.get(userid, "TEXT_PRO")
        image_data = await Tools.gen_text_pro(text, "water-color")
        keyboard = ButtonUtils.create_buttons_textpro(Tools.query_textpro[0], userid, current_batch=0)
        state.set(userid, "page_textpro", 0)
        buttons = InlineKeyboardMarkup(keyboard)
        result.append(
            InlineQueryResultPhoto(
                photo_url=image_data,
                title="Text Pro Inline!",
                reply_markup=buttons,
                caption=f"<blockquote>**Costum text:**\n\n{text}</blockquote>",
            )
        )

        return result
    except Exception:
        logger.error(f"Line 180:\n {traceback.format_exc()}")


async def inline_cat(result, inline_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh cat", callback_data="refresh_cat", style="primary")], 
        [InlineKeyboardButton("Close", callback_data="close inline_cat", style="danger")]
    ])
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    if r.status_code == 200:
        data = r.json()
        cat_url = data[0]["url"]
        if cat_url.endswith(".gif"):
            result.append(
                InlineQueryResultAnimation(
                    animation_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<b>Meow 😽</b>",
                )
            )
        else:
            result.append(
                InlineQueryResultPhoto(
                    photo_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<b>Meow 😽</b>",
                )
            )

    return result


async def inline_font(result, inline_query):
    get_id = inline_query.from_user.id

    keyboard = ButtonUtils.create_font_keyboard(query_fonts[0], get_id, current_batch=0)

    buttons = InlineKeyboardMarkup(keyboard)
    result.append(
        InlineQueryResultArticle(
            title="Font Inline!",
            reply_markup=buttons,
            input_message_content=InputTextMessageContent("<b>Please choice fonts:</b>", parse_mode=ParseMode.HTML),
        )
    )
    return result


async def inline_eval(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    data = state.get(BOT_ID, uniq)
    if len(data) == 1:
        msg = data["time"]
        button = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data=f"close inline_eval {uniq}", style="danger")]])
    else:
        msg = data["time"]
        button = InlineKeyboardMarkup([[InlineKeyboardButton("Output", url=f"{data['url']}", style="primary")]])
    result.append(
        InlineQueryResultArticle(
            title="Inline Eval",
            input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True),
            reply_markup=button,
        )
    )
    return result


async def gc_inline(result, inline_query):
    ids = inline_query.from_user.id
    data = state.get(ids, "gc_info")
    state.set(BOT_ID, "gc_info", data)
    usr = data["username"]
    if usr is None:
        keyb = InlineKeyboardMarkup([[InlineKeyboardButton("Desc", callback_data=f"cb_desc {data['id']}", style="primary")]])
    else:
        keyb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Chat", url=f"https://t.me/{usr}", style="primary"),
                InlineKeyboardButton("Desc", callback_data=f"cb_desc {data['id']}", style="primary"),
            ]
        ])
    msg = f"""
<blockquote expandable><b>ChatInfo:</b>
   <b>name:</b> <b>{data['name']}</b>
      <b>id:</b> <code>{data['id']}</code>
      <b>type:</b> <b>{data['type']}</b>
      <b>dc_id:</b> <b>{data['dc_id']}</b>
      <b>username:</b> <b>@{data['username']}</b>
      <b>member:</b> <b>{data['member']}</b>
      <b>protect:</b> <b>{data['protect']}</b>
      <b>is_creator:</b> <b>{data['is_creator']}</b>
      <b>is_admin:</b> <b>{data['is_admin']}</b>
      <b>is_restricted:</b> <b>{data['is_restricted']}</b></blockquote>
"""
    result.append(
        InlineQueryResultArticle(
            title="gc info!",
            input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True, parse_mode=ParseMode.HTML),
            reply_markup=keyb,
        )
    )
    return result


async def user_inline(result, inline_query):
    ids = inline_query.from_user.id
    data = state.get(ids, "user_info")
    try:
        org = await bot.get_users(int(data["id"]))
        keyb = InlineKeyboardMarkup([[InlineKeyboardButton("User", user_id=int(org.id), style="primary")]])
    except Exception:
        org = f"tg://openmessage?user_id={int(data['id'])}"
        keyb = InlineKeyboardMarkup([[InlineKeyboardButton("User", url=f"{org}", style="primary")]])
    msg = f"""
<blockquote expandable><b>UserInfo:</b>
   <b>name:</b> <b>{data['name']}</b>
      <b>id:</b> <code>{data['id']}</code>
      <b>created:</b> <code>{data['create']}</code>
      <b>is_contact:</b> <b>{data['contact']}</b>
      <b>is_premium:</b> <b>{data['premium']}</b>
      <b>is_deleted:</b> <b>{data['deleted']}</b>
      <b>is_bot:</b> <b>{data['isbot']}</b>
      <b>is_gbanned:</b> <b>{data['gbanned']}</b>
      <b>dc_id:</b> <b>{data['dc_id']}</b></blockquote>
"""
    result.append(
        InlineQueryResultArticle(
            title="user info!",
            input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True, parse_mode=ParseMode.HTML),
            reply_markup=keyb,
        )
    )
    return result


async def pmpermit_inline(result, inline_query):
    him = int(inline_query.query.split()[1])
    mee = inline_query.from_user.id
    gtext = await dB.get_var(mee, "PMTEXT")
    pm_text = gtext if gtext else DEFAULT_TEXT
    pm_warns = await dB.get_var(mee, "PMLIMIT") or LIMIT
    Flood = state.get(mee, him)
    teks, button = ButtonUtils.parse_msg_buttons(pm_text)
    button = ButtonUtils.create_inline_keyboard(button, mee)
    def_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"cb_pm ok {mee} {him}", style="success"),
            InlineKeyboardButton("Disapprove", callback_data=f"cb_pm no {mee} {him}", style="danger"),
        ],
        [
            InlineKeyboardButton(f"You have a warning {Flood} of {pm_warns} !!", callback_data=f"cb_pm warn {mee} {him}", style="primary")
        ],
    ])
    if button:
        for row in def_button.inline_keyboard:
            button.inline_keyboard.append(row)
    else:
        button = def_button
    tekss = await Tools.escape_tag(bot, him, teks, Tools.parse_words)
    media = await dB.get_var(mee, "PMMEDIA")
    if media:
        filem = InlineQueryResultCachedVideo if media["type"] == "video" else InlineQueryResultCachedPhoto
        url_ling = {"video_file_id": media["file_id"]} if media["type"] == "video" else {"photo_file_id": media["file_id"]}
        result.append(
            filem(
                **url_ling,
                title="PMPermit Media1",
                caption=tekss,
                reply_markup=button,
            )
        )
    else:
        result.append(
            InlineQueryResultArticle(
                title="PMPermit NOn-Media",
                input_message_content=InputTextMessageContent(
                    tekss,
                    disable_web_page_preview=True,
                ),
                reply_markup=button,
            )
        )
    return result


async def copy_inline(result, inline_query, user_id):
    try:
        _id = state.get(user_id, "inline_copy")
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            button = message.reply_to_message.reply_markup
            caption = message.reply_to_message.text or message.reply_to_message.caption or ""
            entities = message.reply_to_message.entities or message.reply_to_message.caption_entities or ""
            if message.reply_to_message.media:
                client = message._client
                reply = message.reply_to_message
                copy = await reply.copy(bot.me.username)
                sent = await client.send_message(bot.me.username, "/id copy_media", reply_to_message_id=copy.id)
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                data = state.get(user_id, "copy_media")
                file_id = str(data["file_id"])
                type = str(data["type"])
                type_mapping = {
                    "photo": InlineQueryResultCachedPhoto,
                    "video": InlineQueryResultCachedVideo,
                    "animation": InlineQueryResultCachedAnimation,
                    "audio": InlineQueryResultCachedAudio,
                    "document": InlineQueryResultCachedDocument,
                    "sticker": InlineQueryResultCachedSticker,
                    "voice": InlineQueryResultCachedVoice,
                }
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": caption,
                    "caption_entities": entities,
                    "reply_markup": button,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update({"document_file_id": file_id, "title": "Document with Button"})
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

                result.append(result_class(**kwargs))
            else:
                result.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Send Inline!",
                        reply_markup=button,
                        input_message_content=InputTextMessageContent(
                            caption,
                            entities=entities,
                        ),
                    )
                )
        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


async def send_inline(result, inline_query, user_id):
    try:
        _id = state.get(user_id, "inline_send")
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            button = message.reply_to_message.reply_markup
            caption = message.reply_to_message.text or message.reply_to_message.caption or ""
            entities = message.reply_to_message.entities or message.reply_to_message.caption_entities or ""
            if message.reply_to_message.media:
                client = message._client
                reply = message.reply_to_message
                copy = await reply.copy(bot.me.username)
                sent = await client.send_message(bot.me.username, "/id send_media", reply_to_message_id=copy.id)
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                data = state.get(user_id, "send_media")
                file_id = str(data["file_id"])
                type = str(data["type"])
                type_mapping = {
                    "photo": InlineQueryResultCachedPhoto,
                    "video": InlineQueryResultCachedVideo,
                    "animation": InlineQueryResultCachedAnimation,
                    "audio": InlineQueryResultCachedAudio,
                    "document": InlineQueryResultCachedDocument,
                    "sticker": InlineQueryResultCachedSticker,
                    "voice": InlineQueryResultCachedVoice,
                }
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": caption,
                    "reply_markup": button,
                    "caption_entities": entities,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update({"document_file_id": file_id, "title": "Document with Button"})
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

                result.append(result_class(**kwargs))
            else:
                result.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Send Inline!",
                        reply_markup=button,
                        input_message_content=InputTextMessageContent(caption, entities=entities),
                    )
                )
        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


async def button_inline(result, inline_query, user_id):
    try:
        data = state.get(user_id, "button")
        text, button = ButtonUtils.parse_msg_buttons(data)
        if button:
            button = ButtonUtils.create_inline_keyboard(button, user_id)

        data2 = state.get(user_id, "button_media")
        if not data2:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Text Button!",
                    input_message_content=InputTextMessageContent(text, disable_web_page_preview=True),
                    reply_markup=button,
                )
            )
        else:
            file_id = str(data2["file_id"])
            type = str(data2["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedAudio,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }

            if type in type_mapping:
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": text,
                    "reply_markup": button,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update({"document_file_id": file_id, "title": "Document with Button"})
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

                result.append(result_class(**kwargs))

        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


async def copy_inline_msg(result, inline_query):
    result.append(
        InlineQueryResultArticle(
            title="Copy Inline!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔐 Unlock Message 🔐", callback_data=f"copymsg_{int(inline_query.query.split()[1])}", style="success")]
            ]),
            input_message_content=InputTextMessageContent("<b>🔒 This is private content</b>", parse_mode=ParseMode.HTML),
        )
    )
    return result


# ==========================================
# MENU INLINE HELP DENGAN FORMAT PREMIUM
# ==========================================
async def get_inline_help(result, inline_query):
    user_id = inline_query.from_user.id
    prefix = kelra.get_prefix(user_id)
    full = f"<a href=tg://user?id={inline_query.from_user.id}>{inline_query.from_user.first_name} {inline_query.from_user.last_name or ''}</a>"
    
    text_help = f"<blockquote><b><emoji id=6088918540755148137>🤖</emoji> {BOT_NAME}</b></blockquote>"

    msg = f"""
<blockquote><b>
 <emoji id=5436262556064817413>📚</emoji> Inline Help Menu
 <emoji id=6088918540755148137>🤖</emoji> Prefixes: <code>{' '.join(prefix)}</code>
 <emoji id=5215186239853964761>🧩</emoji> Plugins: <code>{len(HELPABLE)}</code>
 <emoji id=5253539825360843975>👤</emoji> {full} </b></blockquote>
{text_help}
<blockquote><b>🔍 Pilih kategori dibawah untuk melihat fitur:</b></blockquote>"""

    result.append(
        InlineQueryResultArticle(
            title="Help Menu Premium!",
            description="Command Help Premium",
            reply_markup=get_category_menu(page=0),
            input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True, parse_mode=ParseMode.HTML),
        )
    )
    return result


async def alive_inline(result, inline_query):
    self = inline_query.from_user.id
    pmper = None
    status = None
    start = datetime.now()
    ping = (datetime.now() - start).microseconds / 1000
    upnya = await get_time((time() - start_time))
    me = next((x for x in kelra._ubot), None)
    try:
        peer = kelra._get_my_peer[self]
        users = len(peer["pm"])
        group = len(peer["gc"])
    except Exception:
        users = random.randrange(await me.get_dialogs_count())
        group = random.randrange(await me.get_dialogs_count())
    await me.invoke(Ping(ping_id=0))
    seles = await dB.get_list_from_var(bot.me.id, "SELLER")
    if self in SUDO_OWNERS:
        status = "[Admins]"
    elif self in seles:
        status = "[Seller]"
    else:
        status = "[Costumer]"
    cekpr = await dB.get_var(self, "PMPERMIT")
    if cekpr:
        pmper = "enable"
    else:
        pmper = "disable"
    get_exp = await dB.get_expired_date(self)
    exp = get_exp.strftime("%d-%m-%Y")
    txt = f"""
<blockquote expandable><b>{BOT_NAME}</b>
    <b>status:</b> {status} 
      <b>dc_id:</b> <code>{me.me.dc_id}</code>
      <b>ping_dc:</b> <code>{str(ping).replace('.', ',')} ms</code>
      <b>anti_pm:</b> <code>{pmper}</code>
      <b>peer_users:</b> <code>{users} users</code>
      <b>peer_group:</b> <code>{group} group</code>
      <b>peer_ubot:</b> <code>{len(kelra._ubot)} ubot</code>
      <b>uptime:</b> <code>{upnya}</code>
      <b>expires:</b> <code>{exp}</code></blockquote>
"""
    msge = f"<blockquote expandable>{txt}</blockquote>"
    button = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close alive", style="danger")]])
    cekpic = await dB.get_var(self, "ALIVE_PIC")
    if not cekpic:
        result.append(
            InlineQueryResultArticle(
                title=BOT_NAME,
                description="Get Alive Of Bot.",
                input_message_content=InputTextMessageContent(msge, parse_mode=ParseMode.HTML),
                reply_markup=button,
            )
        )
    else:
        media = InlineQueryResultVideo if cekpic.endswith(".mp4") else InlineQueryResultPhoto
        url_ling = {"video_url": cekpic, "thumb_url": cekpic} if cekpic.endswith(".mp4") else {"photo_url": cekpic}
        result.append(
            media(
                **url_ling,
                title=BOT_NAME,
                description="Get Alive Of Bot.",
                caption=msge,
                reply_markup=button,
            )
        )
    return result


async def get_inline_note(result, inline_query):
    q = inline_query.query.split(None, 1)
    note = q[1]
    logger.info(f"{note}")
    gw = inline_query.from_user.id
    _id = state.get(gw, "in_notes")
    message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
    noteval = await dB.get_var(gw, note, "notes")
    if not noteval:
        return
    btn_close = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data=f"close get_note {note}", style="danger")]])
    state.set("close_notes", "get_note", btn_close)
    try:
        tks = noteval["result"].get("text")
        type = noteval["type"]
        file_id = noteval["file_id"]
        note, button = ButtonUtils.parse_msg_buttons(tks)
        teks = await Tools.escape_filter(message, note, Tools.parse_words)
        button = ButtonUtils.create_inline_keyboard(button, gw)
        for row in btn_close.inline_keyboard:
            button.inline_keyboard.append(row)
        if type != "text":
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedAudio,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": teks,
                "reply_markup": button,
                "parse_mode": ParseMode.HTML,
            }

            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs["audio_file_id"] = file_id
            elif type == "document":
                kwargs.update({"document_file_id": file_id, "title": "Document with Button"})
            elif type == "sticker":
                kwargs["sticker_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Send Inline!",
                    reply_markup=button,
                    input_message_content=InputTextMessageContent(
                        teks,
                        parse_mode=ParseMode.HTML,
                    ),
                )
            )
        return result
    except Exception:
        logger.error(f"Error notes: {traceback.format_exc()}")


# ==========================================
# FUNGSI UNTUK MERESPON KLIK TOMBOL JASEB & CANCEL GCAST
# ==========================================
from pyrogram import filters
from kelra.helpers import task

@bot.on_callback_query(filters.regex(r"^jsb_start_"))
async def on_jaseb_start(client, callback_query):
    # LOCAL IMPORT UNTUK MENCEGAH CIRCULAR IMPORT ERROR!
    from plugins.jaseb import JASEB_RUNNING, JASEB_TASKS, run_jaseb_loop, JASEB_MSG
    
    data = callback_query.data.split("_")
    user_id = int(data[2])
    interval = int(data[3])
    
    # Validasi kepemilikan agar member lain nggak bisa pencet
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ Ini bukan menu Jaseb milikmu!", show_alert=True)

    # Pengecekan JIKA VPS restart (Memori Jaseb hilang)
    if user_id not in JASEB_MSG or not JASEB_MSG.get(user_id):
        return await callback_query.answer("❌ Gagal! Pesan hilang dari memori (bot habis direstart). Silakan reply/ketik ulang .jaseb!", show_alert=True)

    if JASEB_RUNNING.get(user_id, False):
        return await callback_query.answer("⚠️ Jaseb sudah berjalan! Matikan dulu dengan .jaseb off", show_alert=True)

    # WAJIB: Mencari client Ubot milik user untuk menjalankan broadcast-nya
    ubot_client = next((x for x in kelra._ubot if x.me.id == user_id), None)
    if not ubot_client:
        return await callback_query.answer("⚠️ Ubot kamu tidak terdeteksi aktif!", show_alert=True)

    # Menandai Jaseb berjalan
    JASEB_RUNNING[user_id] = True
    
    # Jalankan background loop ke UBOT
    task_loop = asyncio.create_task(run_jaseb_loop(ubot_client, user_id, interval))
    JASEB_TASKS[user_id] = task_loop
    
    menit = interval // 60
    jam = menit // 60
    waktu_str = f"{jam} Jam" if jam > 0 and menit % 60 == 0 else f"{menit} Menit"

    # GANTI KE EMOJI STANDAR (Bot API tidak support tag <emoji>)
    try:
        await callback_query.edit_message_text(
            f"<blockquote>✅ **JASEB BERHASIL DIAKTIFKAN!**\n\n"
            f"⏱ Pesan dikirim setiap **{waktu_str}**.\n"
            f"💬 Cek <code>Saved Messages</code> untuk log auto-broadcast.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Matikan Jaseb", callback_data=f"jsb_cancel_{user_id}", style="danger")]]),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Jika gagal edit pesan (menghindari error nyangkut), batalkan loop
        JASEB_RUNNING[user_id] = False
        task_loop.cancel()
        if user_id in JASEB_TASKS:
            del JASEB_TASKS[user_id]
        logger.error(f"Gagal edit Jaseb menu: {str(e)}")
        await callback_query.answer(f"❌ Gagal memuat UI: {str(e)[:50]}", show_alert=True)

@bot.on_callback_query(filters.regex(r"^jsb_cancel_"))
async def on_jaseb_cancel(client, callback_query):
    from plugins.jaseb import JASEB_RUNNING, JASEB_TASKS
    
    data = callback_query.data.split("_")
    user_id = int(data[2])

    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ Ini bukan menu Jaseb milikmu!", show_alert=True)

    if user_id in JASEB_RUNNING and JASEB_RUNNING[user_id]:
        JASEB_RUNNING[user_id] = False
        
        if user_id in JASEB_TASKS and JASEB_TASKS[user_id]:
            JASEB_TASKS[user_id].cancel()
            del JASEB_TASKS[user_id]

        await callback_query.edit_message_text(
            "<blockquote>🛑 **Jaseb berhasil DIMATIKAN.**</blockquote>",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.answer("⚠️ Jaseb sedang tidak aktif.", show_alert=True)

@bot.on_callback_query(filters.regex(r"^cancel_task"))
async def cancel_task_cb(client, callback_query):
    query = callback_query.data.split()
    task_id = query[1]
    
    if task.is_active(task_id):
        task.end_task(task_id)
        await callback_query.answer(f"Berhasil! Task #{task_id} telah dibatalkan.", show_alert=True)
        await callback_query.edit_message_text(f"❌ <i>Task #{task_id} berhasil dibatalkan oleh user.</i>")
    else:
        await callback_query.answer("Gagal: Task ini sudah selesai atau tidak ditemukan.", show_alert=True)

@bot.on_callback_query(filters.regex(r"^close_gcast"))
async def close_gcast_cb(client, callback_query):
    await callback_query.message.delete()


# ==========================================
# PENANGKAP KLIK (CALLBACK HANDLER) MENU BANTUAN
# ==========================================
@bot.on_callback_query(filters.regex(r"^cat_page_(.*)"))
async def cat_page_cb(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    prefix = kelra.get_prefix(user_id)
    full = f"<a href=tg://user?id={user_id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    text_help = f"<blockquote><b><emoji id=6088918540755148137>🤖</emoji> {BOT_NAME}</b></blockquote>"
    msg = f"""
<blockquote><b>
 <emoji id=5436262556064817413>📚</emoji> Inline Help Menu
 <emoji id=6088918540755148137>🤖</emoji> Prefixes: <code>{' '.join(prefix)}</code>
 <emoji id=5215186239853964761>🧩</emoji> Plugins: <code>{len(HELPABLE)}</code>
 <emoji id=5253539825360843975>👤</emoji> {full} </b></blockquote>
{text_help}
<blockquote><b>🔍 Pilih kategori dibawah untuk melihat fitur:</b></blockquote>"""
    await callback_query.edit_message_text(
        msg, 
        reply_markup=get_category_menu(page), 
        disable_web_page_preview=True, 
        parse_mode=ParseMode.HTML
    )

@bot.on_callback_query(filters.regex(r"^cat_(.*)"))
async def cat_cb(client, callback_query):
    # Hindari tabrakan dengan fungsi halaman (cat_page)
    if callback_query.data.startswith("cat_page"):
        return
        
    clean_cat = callback_query.matches[0].group(1)
    categories = get_categories()
    
    # Cari kategori yang cocok
    matched_cat = None
    for key in categories.keys():
        if key[:30] == clean_cat:
            matched_cat = key
            break
            
    if not matched_cat:
        return await callback_query.answer("Kategori tidak ditemukan!", show_alert=True)
        
    modules = categories[matched_cat]
    buttons = []
    
    # Susun tombol untuk setiap modul di dalam kategori tersebut (2 kolom)
    for i in range(0, len(modules), 2):
        row = [InlineKeyboardButton(text=modules[i], callback_data=f"mod_{modules[i]}", style="primary")]
        if i + 1 < len(modules):
            row.append(InlineKeyboardButton(text=modules[i+1], callback_data=f"mod_{modules[i+1]}", style="primary"))
        buttons.append(row)
        
    # Tombol kembali ke menu kategori utama
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="cat_page_0", style="danger")])
    
    text_help = f"<blockquote><b><emoji id=5436262556064817413>📚</emoji> Kategori: {matched_cat}</b>\n🔍 Pilih modul di bawah ini:</blockquote>"
    await callback_query.edit_message_text(
        text_help, 
        reply_markup=InlineKeyboardMarkup(buttons), 
        disable_web_page_preview=True, 
        parse_mode=ParseMode.HTML
    )

@bot.on_callback_query(filters.regex(r"^mod_(.*)"))
async def mod_cb(client, callback_query):
    mod_name = callback_query.matches[0].group(1)
    if mod_name not in HELPABLE:
        return await callback_query.answer("Modul tidak ditemukan!", show_alert=True)
        
    user_id = callback_query.from_user.id
    pref = kelra.get_prefix(user_id)
    x = next(iter(pref)) if pref else "."
    text_help2 = f"<blockquote>***🤖 {BOT_NAME}***</blockquote>"
    
    # Memanggil teks bantuan dari modul
    help_text = HELPABLE[mod_name].__HELP__.format(x, text_help2)
    
    # Mencari kembali nama kategori agar tombol "Back" bisa berfungsi
    raw_cat = getattr(HELPABLE[mod_name], "__CATEGORY__", "General")
    clean_cat = clean_category_name(raw_cat)
    
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=f"cat_{clean_cat[:30]}", style="danger")]])
    await callback_query.edit_message_text(
        help_text, 
        reply_markup=buttons, 
        disable_web_page_preview=True, 
        parse_mode=ParseMode.HTML
    )

