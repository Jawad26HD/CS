import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
TELEGRAM_BOT_TOKEN ="8472115288:AAE4_l0rrrhNSeiGgjwZ_BAU6HUu0ConVTE"
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
ADMIN_ID = 7502265872

# إنشاء لوحة المفاتيح مع الأسئلة
def create_faq_keyboard():
    questions = list(FAQ.keys())
    keyboard = [questions[i:i+2] for i in range(0, len(questions), 2)]
    keyboard.append(["إغلاق لوحة المفاتيح"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="اختر سؤالاً من الأسئلة الشائعة")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_faq_keyboard()
    await update.message.reply_text(
        "مرحبا بك في ClearSmile bot, هذه بعض الاسئلة الشائعة  \n"
        "كيف يمكنني مساعدتك ؟",
        reply_markup=keyboard
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        unanswered_questions.append({
            "question": question,
            "user_info": user_info,
            "user_id": user.id
        })
        
        await update.message.reply_text(
            " تم ارسال سؤالك الى المسؤول, سيتم الاجابة على سؤالك في اقرب وقت ممكن "
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_faq_keyboard()
    await update.message.reply_text(
        "اختر أحد الأسئلة التالية:",
        reply_markup=keyboard
    )

async def cancel_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "تم إغلاق لوحة المفاتيح. اكتب /start لإعادة فتحها.",
        reply_markup=ReplyKeyboardRemove()
    )

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    await update.message.reply_text(
        f"معرفك هو: {user_id}\n\n"
        f"الاسم: {user.first_name} {user.last_name or ''}\n"
        f"اسم المستخدم: @{user.username or 'لا يوجد'}"
    )

async def set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    user_id = update.message.from_user.id
    ADMIN_ID = user_id
    await update.message.reply_text(
        f"تم تعيينك كمسؤول! معرف المسؤول الآن: {ADMIN_ID}\n\n"
        "يمكنك استخدام الأوامر التالية:\n"
        "/unanswered - رؤية الأسئلة غير المجابة\n"
        "/clear_unanswered - مسح الأسئلة غير المجابة"
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
    
    await update.message.reply_text(message)

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

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    # الحصول على التوكن من متغير البيئة (مطلوب للنشر على المنصات السحابية)
    # استخدم اسم متغير ثابت وليس التوكن نفسه!
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        # كخيار ثانوي، يمكنك وضع التوكن مباشرة هنا (غير آمن)
        # ولكن يجب عليك إبطال هذا التوكن فوراً لأنه معرض الآن!
        token = "8472115288:AAE4_l0rrrhNSeiGgjwZ_BAU6HUu0ConVTE"
    
    if not token:
        raise RuntimeError("الرجاء وضع توكن البوت في متغير البيئة TELEGRAM_BOT_TOKEN")
    
    # بناء التطبيق
    application = ApplicationBuilder().token(token).build()
    
    # إضافة handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("cancel", cancel_keyboard))
    application.add_handler(CommandHandler("myid", get_my_id))
    application.add_handler(CommandHandler("unanswered", get_unanswered_questions))
    application.add_handler(CommandHandler("clear_unanswered", clear_unanswered_questions))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    logger.info("البوت يعمل...")
    application.run_polling()

if __name__ == "__main__":
    main()