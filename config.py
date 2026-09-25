# -*- coding: utf-8 -*-
"""
تنظیمات مرکزی ربات.
هر عددی که ممکنه بخوای عوض کنی (قیمت‌ها، آیدی ادمین، کانال‌ها) همینجاست.

نکته: BOT_TOKEN, BOT_USERNAME, ADMIN_IDS از "Variables" ریلوی خونده می‌شن
تا لازم نباشه هر بار کد رو ویرایش/پوش کنی. بقیه مقادیر (قیمت‌ها و ...)
همینجا مستقیم قابل تغییرن.
"""

import os

# ---------- توکن و یوزرنیم ربات ----------
# اگه بخوای بعداً از تب Variables ریلوی عوضش کنی، همونجا اولویت داره؛
# وگرنه همین مقدار پیش‌فرض که خودت دادی استفاده می‌شه.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8838508333:AAEohddtihuZlUsBkRDS39l2LwTkk-2G0GE")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "GredDroBot")  # بدون @

# ---------- ادمین‌ها ----------
# مقدار متغیر ADMIN_IDS رو با کاما جدا کن، مثلاً: 111111111,222222222
_admin_ids_raw = os.environ.get("ADMIN_IDS", "6189261314")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()]

# ---------- کانال ثبت درخواست‌های برداشت ----------
# ربات باید ادمین این کانال باشه تا بتونه توش پیام بفرسته.
WITHDRAW_CHANNEL = os.environ.get("WITHDRAW_CHANNEL", "@varizitm")

# ---------- تنظیمات مالی ----------
# نمایش با $ هست ولی خودِ واریز واقعی با BNB (شبکه BEP20) انجام می‌شه.
CURRENCY_SYMBOL = "$"
STARTING_BALANCE = 3.0     # موجودی اولیه‌ی هر کاربر جدید
MIN_WITHDRAW = 75.0        # حداقل مبلغ قابل برداشت
REFERRAL_REWARD = 8.0      # پاداش هر زیرمجموعه
WITHDRAW_MILESTONE_REFERRALS = 9  # از این تعداد زیرمجموعه به بالا، موقع زدن «برداشت» استیکر جشن نشون داده می‌شه


def fmt_amount(amount) -> str:
    """فرمت یکدست نمایش مبلغ، مثلاً $5.0"""
    return f"{CURRENCY_SYMBOL}{amount}"


# ---------- دیتابیس ----------
DB_PATH = "bot.db"

# ---------- استیکرها ----------
STICKER_SET = "Crocosaurus"
