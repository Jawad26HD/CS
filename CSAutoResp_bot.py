import os
import logging
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن يجب أن يكون من متغيرات البيئة لأسباب أمنية
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8472115288:AAE4_l0rrrhNSeiGgjwZ_BAU6HUu0ConVTE')

# ملف تخزين بيانات المستخدمين
USER_DATA_FILE = "user_data.json"

FAQ = {
    "متى تأسست شركة Clear Smile ؟": "تأسست شركة Clear Smile عام 2016 كأول شركة مختصة بتصنيع الصفائح الشفافة (Aligners) في سوريا والمنطقة، معتمدة على أحدث تقنيات التصميم والطباعة الرقمية.",
    "كيف يعمل التقويم الشفاف Clear Smile ؟": "يعمل من خلال سلسلة صفائح شفافة متسلسلة تُصمم خصيصاً لكل مريض لتحريك الأسنان تدريجياً بخطوات مدروسة حتى الوصول للابتسامة المثالية.",
    "ما هي مراحل المعالجة بالتقويم الشفاف Clear Smile ؟": "1. أخذ الطبعة:\n• إما طبعة رقمية (Intra-Oral Scan)\n• أو طبعة سيليكون مطاط (قاسي و رخو)\n2. إعداد خطة علاج رقمية ثلاثية الأبعاد.\n3. إرسال الخطة للطبيب المعالج عبر الإيميل (تتضمن الحركات المطلوبة والمدة التقديرية).\n4. بعد موافقة الطبيب يتم تصنيع سلسلة الصفائح لكل مرحلة.",
    "ما هو Clear Smile Pro ؟": "Clear Smile Pro هو نظام متطور من Clear Smile يعتمد على صفائح مؤلفة من ثلاث طبقات:\n• مرونة أعلى لزيادة فعالية حركة الأسنان\n• مقاومة أكبر للتصدع والكسر\n• راحة أفضل للمريض\n• أسرع من النظام العادي",
    "ما الفرق بين Clear Smile و Clear Smile Pro ؟": "🔹 Clear Smile العادي\n• نظام: 3 صفائح لكل مرحلة\n• مدة المرحلة: شهر كامل\n• كل صفيحة لها وقت محدد للارتداء (7-14 يوم)\n• الصفائح مؤلفة من طبقة واحدة\n\n🔹 Clear Smile Pro\n• نظام: 2 صفيحة لكل مرحلة\n• مدة المرحلة: 20 يوم فقط (كل صفيحة حوالي 10 أيام)\n• الصفائح مؤلفة من مادة ثلاثية الطبقات (مرونة أعلى – مقاومة للكسر والتصدع – راحة أكبر)\n• أسرع وأكثر فعالية",
    "أين أجد Clear Smile ؟": "يتوفر حصراً عن طريق العيادات والمراكز المعتمدة لدى الشركة، ولا يمكن شراؤه مباشرة من قبل المريض.",
    "من الطبيب الذي يعالج بـ Clear Smile ؟": "العلاج يقدَّم حصراً من خلال أخصائي تقويم معتمد من شركة Clear Smile.",
    "ما مدة وزمن المعالجة بـ Clear Smile ؟": "• حالات بسيطة: 6 – 8 أشهر\n• حالات متوسطة: حتى 12 شهر\n• حالات معقدة: قد تصل إلى 18 – 24 شهر",
    "ما تكلفة المعالجة بـ Clear Smile ؟": "التكلفة النهائية تختلف حسب الحالة وحسب خطة وتقدير الطبيب المعالج.",
    "هل المعالجة مؤلمة ؟": "لا تسبب ألم شديد، فقط إحساس خفيف بالضغط أو الشد عند تبديل الصفيحة، وهو طبيعي ويدل على أن الأسنان تتحرك بشكل صحيح.",
    "ما الحالات التي يعالجها Clear Smile ؟": "✔ العضة المعكوسة\n✔ التراكب والازدحام\n✔ البروز الأمامي\n✔ المسافات والفراغات\n✔ العضة المفتوحة\n✔ أغلب حالات سوء الإطباق\n\nالحالات الأكثر شيوعاً:\n✔ التحضير التقويمي قبل المعالجات التجميلية\n✔ التحضير التقويمي قبل زرع الأسنان\n✔ رصف تقويمي لأسنان محددة\n✔ رصف تقويمي لفك واحد",
}

# تخزين الأسئلة غير المجابة
unanswered_questions = []

# معرف المسؤول (سيتم تعيينه تلقائياً عند استخدام الأمر /setadmin)
ADMIN_ID = None

# تحميل بيانات المستخدمين من الملف
def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"خطأ في تحميل بيانات المستخدمين: {e}")
    return {}

# حفظ بيانات المستخدمين إلى الملف
def save_user_data(user_data):
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطأ في حفظ بيانات المستخدمين: {e}")

# تحديث بيانات المستخدم
def update_user_data(user):
    user_data = load_user_data()
    user_id = str(user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            "first_name": user.first_name,
            "last_name": user.last_name or "",
            "username": user.username or "",
            "language_code": user.language_code or "",
            "is_bot": user.is_bot,
            "interaction_count": 0,
            "last_interaction": None
        }
    else:
        user_data[user_id]["interaction_count"] += 1
    
    # تحديث معلومات المستخدم إذا تغيرت
    user_data[user_id]["first_name"] = user.first_name
    user_data[user_id]["last_name"] = user.last_name or ""
    user_data[user_id]["username"] = user.username or ""
    
    save_user_data(user_data)
    return user_data[user_id]

# إنشاء لوحة المفاتيح مع الأسئلة
def create_faq_keyboard():
    questions = list(FAQ.keys())
    keyboard = [questions[i:i+2] for i in range(0, len(questions), 2)]
    keyboard.append(["إغلاق لوحة المفاتيح"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="اختر سؤالاً من الأسئلة الشائعة")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    keyboard = create_faq_keyboard()
    await update.message.reply_text(
        "مرحبا بك في ClearSmile bot, هذه بعض الاسئلة الشائعة  \n"
        "كيف يمكنني مساعدتك ؟",
        reply_markup=keyboard
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    # التحقق أولاً إذا كان المستخدم مسؤولاً ويحاول الرد على مستخدم آخر
    global ADMIN_ID
    if ADMIN_ID and update.effective_user.id == ADMIN_ID and 'replying_to' in context.user_data:
        await handle_admin_reply(update, context)
        return
        
    question = update.message.text.strip()
    
    if question == "إغلاق لوحة المفاتيح":
        await update.message.reply_text(
            "تم إغلاق لوحة المفاتيح. اكتب /start لإعادة فتحها.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
        
    if question in FAQ:
        await update.message.reply_text(FAQ[question])
    else:
        user = update.message.from_user
        user_info = f"{user.first_name} {user.last_name or ''} (@{user.username or 'لا يوجد'})"
        user_data = {
            "question": question,
            "user_info": user_info,
            "user_id": user.id,
            "message_id": update.message.message_id,
            "chat_id": update.message.chat_id
        }
        unanswered_questions.append(user_data)
        
        # إرسال إشعار للمسؤول
        if ADMIN_ID:
            try:
                keyboard = [
                    [InlineKeyboardButton("الرد على السؤال", callback_data=f"reply_{user.id}")],
                    [InlineKeyboardButton("تجاهل السؤال", callback_data=f"ignore_{user.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                admin_message = (
                    f"❓ سؤال جديد من المستخدم:\n\n"
                    f"👤 المستخدم: {user_info}\n"
                    f"🆔 المعرف: {user.id}\n"
                    f"📝 السؤال: {question}\n\n"
                )
                await context.bot.send_message(
                    chat_id=ADMIN_ID, 
                    text=admin_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"فشل في إرسال الإشعار للمسؤول: {e}")
        
        await update.message.reply_text(
            "تم ارسال سؤالك الى المسؤول, سيتم الاجابة على سؤالك في اقرب وقت ممكن"
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    keyboard = create_faq_keyboard()
    await update.message.reply_text(
        "اختر أحد الأسئلة التالية:",
        reply_markup=keyboard
    )

async def cancel_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    await update.message.reply_text(
        "تم إغلاق لوحة المفاتيح. اكتب /start لإعادة فتحها.",
        reply_markup=ReplyKeyboardRemove()
    )

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    user = update.message.from_user
    user_id = user.id
    await update.message.reply_text(
        f"معرفك هو: {user_id}\n\n"
        f"الاسم: {user.first_name} {user.last_name or ''}\n"
        f"اسم المستخدم: @{user.username or 'لا يوجد'}"
    )

async def set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحديث بيانات المستخدم
    update_user_data(update.message.from_user)
    
    global ADMIN_ID
    user_id = update.message.from_user.id
    ADMIN_ID = user_id
    await update.message.reply_text(
        f"تم تعيينك كمسؤول! معرف المسؤول الآن: {ADMIN_ID}\n\n"
        "يمكنك استخدام الأوامر التالية:\n"
        "/unanswered - رؤية الأسئلة غير المجابة\n"
        "/clear_unanswered - مسح الأسئلة غير المجابة\n"
        "/reply [معرف المستخدم] [الرسالة] - للرد على مستخدم معين\n"
        "/broadcast [الرسالة] - البث الجماعي لجميع المستخدمين\n"
        "/stats - إحصائيات المستخدمين\n"
        "أو استخدام أزرار الرد عند وصول سؤال جديد"
    )

async def get_unanswered_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None:
        await update.message.reply_text("لم يتم تعيين مسؤول بعد. استخدم /setadmin أولاً.")
        return
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("هذا الأمر متاح للمسؤول فقط.")
        return
    
    if not unanswered_questions:
        await update.message.reply_text("لا توجد أسئلة غير مجابة حالياً.")
        return
    
    message = "الأسئلة غير المجابة:\n\n"
    for i, item in enumerate(unanswered_questions, 1):
        message += f"{i}. السؤال: {item['question']}\n   من: {item['user_info']} (ID: {item['user_id']})\n\n"
    
    # إضافة أزرار للرد السريع
    keyboard = []
    for item in unanswered_questions:
        keyboard.append([InlineKeyboardButton(f"الرد على {item['user_info']}", callback_data=f"reply_{item['user_id']}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def clear_unanswered_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None:
        await update.message.reply_text("لم يتم تعيين مسؤول بعد. استخدم /setadmin أولاً.")
        return
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("هذا الأمر متاح للمسؤول فقط.")
        return
    
    global unanswered_questions
    count = len(unanswered_questions)
    unanswered_questions = []
    
    await update.message.reply_text(f"تم مسح {count} سؤال غير مجاب.")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None:
        await update.message.reply_text("لم يتم تعيين مسؤول بعد. استخدم /setadmin أولاً.")
        return
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("هذا الأمر متاح للمسؤول فقط.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("استخدم الأمر بالشكل: /reply [معرف المستخدم] [الرسالة]")
        return
    
    # استخراج معرف المستخدم من الأمر
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("معرف المستخدم غير صحيح.")
        return
    
    # استخراج الرسالة (كل الأجزاء بعد المعرف)
    message = " ".join(context.args[1:])
    
    try:
        # إرسال الرسالة للمستخدم
        await context.bot.send_message(chat_id=user_id, text=f"📨 رد من المسؤول:\n\n{message}")
        await update.message.reply_text(f"✅ تم إرسال الرد إلى المستخدم {user_id}")
        
        # إزالة السؤال من قائمة الأسئلة غير المجابة إن وجد
        global unanswered_questions
        unanswered_questions = [q for q in unanswered_questions if q['user_id'] != user_id]
        
    except Exception as e:
        await update.message.reply_text(f"❌ فشل في إرسال الرسالة: {e}")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = int(data.split('_')[1])
    
    if data.startswith('reply_'):
        # حفظ معرف المستخدم للرد عليه لاحقاً
        context.user_data['replying_to'] = user_id
        await query.edit_message_text(
            f"تم تحديد المستخدم {user_id} للرد. أرسل رسالة الرد الآن:"
        )
    elif data.startswith('ignore_'):
        # تجاهل السؤال
        global unanswered_questions
        unanswered_questions = [q for q in unanswered_questions if q['user_id'] != user_id]
        await query.edit_message_text(f"تم تجاهل سؤال المستخدم {user_id}")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None or update.effective_user.id != ADMIN_ID:
        return
    
    if 'replying_to' in context.user_data:
        user_id = context.user_data['replying_to']
        message = update.message.text
        
        try:
            # إرسال الرسالة للمستخدم
            await context.bot.send_message(chat_id=user_id, text=f"📨:\n{message}")
            await update.message.reply_text(f"✅ تم إرسال الرد إلى المستخدم {user_id}")
            
            # إزالة السؤال من قائمة الأسئلة غير المجابة
            global unanswered_questions
            unanswered_questions = [q for q in unanswered_questions if q['user_id'] != user_id]
            
            # مسح حالة الرد
            del context.user_data['replying_to']
            
        except Exception as e:
            await update.message.reply_text(f"❌ فشل في إرسال الرسالة: {e}")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None:
        await update.message.reply_text("لم يتم تعيين مسؤول بعد. استخدم /setadmin أولاً.")
        return
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("هذا الأمر متاح للمسؤول فقط.")
        return
    
    if not context.args:
        await update.message.reply_text("استخدم الأمر بالشكل: /broadcast [الرسالة]")
        return
    
    # استخراج الرسالة
    message = " ".join(context.args)
    
    # تحميل بيانات المستخدمين
    user_data = load_user_data()
    
    if not user_data:
        await update.message.reply_text("لا يوجد مستخدمين مسجلين بعد.")
        return
    
    # إرسال الرسالة لجميع المستخدمين
    success_count = 0
    fail_count = 0
    
    await update.message.reply_text(f"جاري إرسال الرسالة إلى {len(user_data)} مستخدم...")
    
    for user_id_str in user_data:
        try:
            await context.bot.send_message(chat_id=int(user_id_str), text=f"📢 إشعار من Clear Smile:\n\n{message}")
            success_count += 1
        except Exception as e:
            logger.error(f"فشل في إرسال الرسالة إلى المستخدم {user_id_str}: {e}")
            fail_count += 1
    
    await update.message.reply_text(
        f"تم الانتهاء من البث الجماعي:\n"
        f"✅ عدد الرسائل المرسلة بنجاح: {success_count}\n"
        f"❌ عدد الرسائل الفاشلة: {fail_count}"
    )

async def get_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    if ADMIN_ID is None:
        await update.message.reply_text("لم يتم تعيين مسؤول بعد. استخدم /setadmin أولاً.")
        return
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("هذا الأمر متاح للمسؤول فقط.")
        return
    
    # تحميل بيانات المستخدمين
    user_data = load_user_data()
    
    if not user_data:
        await update.message.reply_text("لا يوجد مستخدمين مسجلين بعد.")
        return
    
    total_users = len(user_data)
    active_users = sum(1 for user in user_data.values() if user.get("interaction_count", 0) > 0)
    
    stats_message = (
        f"📊 إحصائيات المستخدمين:\n\n"
        f"• إجمالي عدد المستخدمين: {total_users}\n"
        f"• عدد المستخدمين النشطين: {active_users}\n"
        f"• عدد الأسئلة غير المجابة: {len(unanswered_questions)}\n\n"
        f"لإرسال رسالة جماعية، استخدم الأمر /broadcast"
    )
    
    await update.message.reply_text(stats_message)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    # الحصول على التوكن من متغير البيئة
    token = TELEGRAM_BOT_TOKEN
    
    if not token:
        raise RuntimeError("الرجاء وضع توكن البوت في متغير البيئة TELEGRAM_BOT_TOKEN")
    
    # بناء التطبيق
    application = ApplicationBuilder().token(token).build()
    
    # إضافة handlers - الترتيب مهم!
    
    # 1. معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("cancel", cancel_keyboard))
    application.add_handler(CommandHandler("myid", get_my_id))
    # application.add_handler(CommandHandler("setadmin", set_admin))
    application.add_handler(CommandHandler("unanswered", get_unanswered_questions))
    application.add_handler(CommandHandler("clear_unanswered", clear_unanswered_questions))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    application.add_handler(CommandHandler("stats", get_user_stats))
    application.add_handler(CommandHandler("reply", reply_to_user))
    
    # 2. معالج الاستعلامات (Callbacks)
    application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^(reply|ignore)_\d+"))
    
    # 3. معالج النص العام (للأسئلة) - يجب أن يكون الأخير
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    logger.info("البوت يعمل...")
    application.run_polling()

if __name__ == "__main__":
    main()