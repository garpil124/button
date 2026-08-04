import asyncio
import random
from pyrogram import filters
from config import OWNER_ID, SUDO_OWNERS, SUPPORT
from kelra.database import state, dB
from kelra.helpers import CMD, FILTERS, Basic_Effect, ButtonUtils, Message, Tools
from kelra.logger import logger

@CMD.BOT("setimg", filters.user(SUDO_OWNERS))
async def set_start_img(client, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply("❌ Balas ke Foto, Video, atau GIF untuk menjadikannya Media Start & Help!")
    media = Tools.get_file_id(message.reply_to_message)
    await dB.set_var(client.me.id, "START_MEDIA", {"type": media["message_type"], "file_id": media["file_id"]})
    await message.reply("✅ Media Start & Help berhasil diatur!")

@CMD.BOT("delimg", filters.user(SUDO_OWNERS))
async def del_start_img(client, message):
    await dB.remove_var(client.me.id, "START_MEDIA")
    await message.reply("✅ Media Start & Help berhasil dihapus! Sekarang hanya menggunakan Teks.")

@CMD.BOT("start", FILTERS.PRIVATE)
@CMD.DB_BROADCAST
async def start_home(client, message):
    is_cb = hasattr(message, "data")
    user = message.from_user
    chat_id = message.message.chat.id if is_cb else message.chat.id
    msg_obj = message.message if is_cb else message

    buttons = ButtonUtils.start_menu(is_admin=(user.id in SUDO_OWNERS))
    text = Message.welcome_message(client, message)
    media_data = await dB.get_var(client.me.id, "START_MEDIA")

    if is_cb:
        if media_data:
            m_type = media_data["type"]
            f_id = media_data["file_id"]
            if msg_obj.media:
                from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAnimation
                if m_type == "photo": media = InputMediaPhoto(f_id, caption=text)
                elif m_type == "video": media = InputMediaVideo(f_id, caption=text)
                else: media = InputMediaAnimation(f_id, caption=text)
                try:
                    await msg_obj.edit_media(media, reply_markup=buttons)
                except Exception:
                    await msg_obj.edit_caption(text, reply_markup=buttons)
            else:
                await msg_obj.delete()
                if m_type == "photo": await client.send_photo(chat_id, f_id, caption=text, reply_markup=buttons)
                elif m_type == "video": await client.send_video(chat_id, f_id, caption=text, reply_markup=buttons)
                else: await client.send_animation(chat_id, f_id, caption=text, reply_markup=buttons)
        else:
            if msg_obj.media:
                await msg_obj.delete()
                await client.send_message(chat_id, text, reply_markup=buttons, disable_web_page_preview=True)
            else:
                await msg_obj.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)
    else:
        if user.id not in SUDO_OWNERS:
            await client.send_message(SUPPORT, f"<b>User: {user.mention}\nID: `{user.id}`\nName: {user.first_name}\nHas started your bot.</b>")
        
        # --- KODE MUNCULIN, TUNGGU, & HAPUS (VERSI STIKER TRANSPARAN) ---
        try:
            gift_terpilih = Message.get_random_gift()
            
            # Pake reply_sticker biar stikernya gerak dan background-nya transparan
            sent_gift = await message.reply_sticker(gift_terpilih)
            
            # Jeda 4 detik biar user liat stikernya gerak
            await asyncio.sleep(4) 
            
            # Hapus stiker tersebut setelah 4 detik!
            await sent_gift.delete()
            
        except Exception as e:
            await message.reply_text(f"⚠️ Gagal kirim gift. Error:\n`{e}`")
        # -------------------------------------------

        # Parameter message_effect_id diaktifkan kembali
        effect_id = random.choice(Basic_Effect)
        if media_data:
            m_type = media_data["type"]
            f_id = media_data["file_id"]
            if m_type == "photo": await message.reply_photo(f_id, caption=text, reply_markup=buttons)
            elif m_type == "video": await message.reply_video(f_id, caption=text, reply_markup=buttons)
            else: await message.reply_animation(f_id, caption=text, reply_markup=buttons)
        else:
            await message.reply_text(text, reply_markup=buttons, disable_web_page_preview=True, message_effect_id=effect_id)

@CMD.BOT("button")
async def _(client, message):
    link = message.text.split(None, 1)[1]
    tujuan, _id = Tools.extract_ids_from_link(link)
    txt = state.get(message.from_user.id, "edit_reply_markup")
    teks, button = ButtonUtils.parse_msg_buttons(txt)
    if button:
        button = ButtonUtils.create_inline_keyboard(button)
    return await client.edit_message_reply_markup(chat_id=tujuan, message_id=_id, reply_markup=button)

@CMD.BOT("id")
async def _(client, message):
    if len(message.command) < 2: return
    query = message.text.split()[1]
    try:
        reply = message.reply_to_message
        media = Tools.get_file_id(reply)
        data = {"file_id": media["file_id"], "type": media["message_type"]}
        state.set(message.from_user.id, query, data)
    except Exception as er:
        logger.error(f"{str(er)}")

@CMD.BOT("cekid", filters.user(SUDO_OWNERS))
async def cek_id_media(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Balas (reply) pesannya ke video/animasi/sticker!")
    
    media = message.reply_to_message
    if media.sticker:
        f_id = media.sticker.file_id
    elif media.animation:
        f_id = media.animation.file_id
    elif media.video:
        f_id = media.video.file_id
    elif media.document:
        f_id = media.document.file_id
    else:
        return await message.reply("❌ Ini bukan file yang didukung!")
        
    await message.reply(f"✅ **Ini File ID yang benar untuk bot ini:**\n\n`{f_id}`")
