import os
import re
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

# ضع التوكن في متغير البيئة DISCORD_TOKEN داخل منصة الاستضافة.
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# اسم القناة التي تُرسل فيها رسائل الترحيب تلقائيًا.
WELCOME_CHANNEL_NAME = "الترحيب"

# الأسئلة والأجوبة مرتبة حسب الأقسام.
FAQ = {
    "التصنيع والأدوات": {
        "أين أصنع فأس Fire Axe؟": "على طاولة التصنيع الأساسية Basic Workbench.",
        "ما المواد المطلوبة لصناعة Fire Axe؟": "4 خشب و2 حجر، على Basic Workbench.",
        "ما المواد المطلوبة لصناعة Stone Axe؟": "3 خشب و2 حجر، على Basic Workbench.",
        "ما الأداة المناسبة لقطع الأشجار؟": "الفأس، مثل Stone Axe أو Fire Axe.",
        "ما الأداة لاستخراج الحجر من الصخور الكبيرة؟": "Pickaxe.",
        "هل المنجل يجمع الخشب والحجر؟": "لا، المنجل سلاح قتال وليس أداة لقطع الأشجار أو تعدين الصخور.",
        "كيف أصنع Hammer؟": "تحتاج 2 خشب و3 Scrap على Basic Workbench.",
        "أين أصنع Flare Gun؟": "على Weapons Bench. علامة مهمة Watchers ترشدك إلى الطاولة.",
        "ما مكونات Flare Gun؟": "2 Metal Parts و2 Wire و1 Rubber على Weapons Bench.",
        "ما ذخيرة Flare Gun؟": "Flare Ammunition، وتُستهلك واحدة لكل طلقة.",
        "كيف أصنع Flare ammo؟": "على Basic Workbench: 1 Cloth و1 Wood و1 Scrap، وتعطيك 2 ذخيرة.",
        "كيف أصنع Bandage؟": "تحتاج 2 Cloth على Basic Workbench.",
        "ما وصفة AK-47؟": "8 Metal Parts و4 Wire و2 Rubber على Weapons Bench.",
        "ما الأداة المناسبة للبحث في السيارة المحطمة؟": "Crowbar.",
        "ما الأداة المناسبة لصناديق الجيش القابلة للكسر؟": "أداة من Tier 1 مثل Crowbar أو Hammer أو Axe أو Pickaxe.",
        "كيف أفتح صندوق الإمدادات العادي؟": "يمكن كسره بأي سلاح حسب المعلومات المتوفرة لدينا.",
    },
    "الموارد والنهب": {
        "من أين أحصل على Scrap؟": "من أكوام الخردة والحاويات القابلة للبحث.",
        "من أين أحصل على Metal Parts؟": "من السيارات المحطمة وبعض الصناديق العسكرية وAirdrops.",
        "من أين أحصل على Rubber؟": "من تفكيك السيارات المحطمة، وقد تجده في الصناديق العسكرية وAirdrops.",
        "ماذا يمكن أن أجد في السيارة المحطمة؟": "قد تحصل عشوائيًا على Scrap أو Metal Parts أو Iron أو Wires أو Rubber أو Screws أو Cloth أو Electronics أو Engine Parts أو Battery أو Fuel.",
        "من أين أحصل على Fuel can؟": "قد تحصل عليه من تفكيك سيارة، وأحيانًا من Supply Crate، لكنه نادر.",
        "أين أجد Apples؟": "في المطابخ والمنازل القابلة للبحث.",
        "أين أجد Berries؟": "من شجيرات التوت.",
        "هل أحتاج أداة لجمع التوت؟": "لا، يمكنك جمعه باليد.",
        "ماذا تفعل Water bottle؟": "تعيد العطش وتعيد قدرًا قليلًا من الصحة.",
        "من أين أحصل على Cloth؟": "من Medical Crates وSupply Crates.",
        "من أين أحصل على Painkillers؟": "من Medical Loot، ولا توجد لها وصفة تصنيع معروفة.",
        "هل السيارات المحطمة تتجدد عند الخروج والدخول؟": "لا، انتظر حوالي 10 دقائق لكل لاعب أو عالم. الخروج والدخول لا يعيدها فورًا.",
        "هل موارد العالم ترجع بمجرد إعادة الدخول؟": "لا، نقاط الإمداد لها مؤقتات تجدد منفصلة حسب النقطة والعالم. إعادة الدخول وحدها لا تعيدها.",
        "هل صناديق Airdrop تحتوي دائمًا Metal Parts وRubber؟": "حسب المعلومات المسجلة لدينا، تحتوي على الأقل على 2 Metal Parts و1 Rubber، لكن قد يختلف ذلك حسب تحديث اللعبة.",
        "هل Scrap وMetal Parts نفس المورد؟": "لا، هما موردان منفصلان.",
    },
    "المهمات والإرشاد": {
        "كيف أعرف وجهة المهمة الحالية؟": "افتح خريطة العالم واتبع علامة الوجهة المرتبطة بالهدف النشط.",
        "كيف أنهي مهمة First Light؟": "اجمع 4 خشب و2 حجر، اصنع Fire Axe، اقطع 3 أشجار، ثم اقتل زومبي واحد.",
        "أين أصنع الفأس لمهمة First Light؟": "على Basic Workbench. الخريطة ترشدك إلى الطاولة عندما تكون المهمة نشطة.",
        "كيف أنهي مهمة Ash group lookout؟": "نظّف 12 زومبي حول الكوخ، خذ مفتاح مخزن إزالة التلوث من الداخل، ثم ارجع إلى قائد البوابة.",
        "أين أجد مفتاح الكوخ في مهمة Ash؟": "داخل الكوخ عند نقطة المراقبة بعد إكمال هدف القضاء على المصابين.",
        "لمن أعيد المفتاح وما المكافأة؟": "أعده إلى قائد Ash group عند البوابة. المكافأة بدلة Hazmat صفراء والدخول إلى المنطقة المسيجة.",
        "ماذا أفعل بعد الاستيقاظ من كوابيس المستشفى؟": "اتبع مهمة Mountain group إلى محطة الإرسال المهجورة على حافة الجبل.",
        "ماذا أفعل بعد الوصول إلى محطة الإرسال؟": "أصلح جهاز الإرسال، أرسل الرسالة، ثم اركب المروحية.",
        "كيف أتقدم في مهمة Watchers؟": "اقرأ سجل الكشاف، افحص ثلاث مناظير، ثم اتبع المهمة إلى الدائرة الحجرية وأرسل الإشارة.",
        "ماذا أحتاج لإشارة Watchers؟": "تحتاج Flare Gun وFlare ammo. اتبع علامة المهمة إلى هدف الإشارة.",
        "ماذا أفعل إذا ما عندي Flare Gun في Watchers؟": "علامة المهمة تشير إلى Weapons Bench لصناعة Flare Gun.",
        "ماذا أفعل إذا ما عندي Flare ammo؟": "حسب تقدمك، قد ترشدك المهمة إلى صندوق الذخيرة عند الدائرة أو إلى Basic Workbench لصناعة المزيد.",
    },
    "القتال": {
        "كيف أهزم التنين؟": "اصنع AK واذهب إلى Roxwood لمواجهة التنين.",
        "هل AK هو السلاح المستخدم ضد التنين؟": "نعم، حسب المعلومات المتوفرة لدينا.",
        "ما أفضل سلاح للزومبي والزعماء؟": "AK خيار قوي حسب المعلومات المسجلة لدينا.",
        "كيف أهزم أبو فأس؟": "ابحث بين الصناديق عن Mini Gun واستخدمها ضده حتى يُهزم.",
        "هل توجد طريقة مؤكدة للهروب من التنين؟": "ما عندي إجابة مؤكدة لهذا السؤال حاليًا.",
    },
}


def make_embed():
    embed = discord.Embed(
        title="دليل المساعدة والأسئلة الشائعة",
        description=(
            "اختر القسم من القائمة بالأسفل، وبعدها اختر سؤالك.\n"
            "الإجابة ستظهر لك بشكل خاص، ولن يراها بقية أعضاء السيرفر."
        ),
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="الأقسام",
        value="🛠️ التصنيع والأدوات\n📦 الموارد والنهب\n🧭 المهمات والإرشاد\n⚔️ القتال",
        inline=False,
    )
    embed.set_footer(text="اضغط على القائمة لاختيار القسم")
    return embed


class PrivateQuestionSelect(discord.ui.Select):
    def __init__(self, owner_id: int, category: str):
        self.owner_id = owner_id
        self.category = category
        options = [
            discord.SelectOption(label=q[:100], value=str(i), description="اضغط لعرض الإجابة")
            for i, q in enumerate(FAQ[category].keys())
        ]
        super().__init__(
            placeholder="اختر السؤال الذي تريده...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("هذه القائمة ليست مخصصة لك.", ephemeral=True)
            return
        question = list(FAQ[self.category].keys())[int(self.values[0])]
        answer = FAQ[self.category][question]
        embed = discord.Embed(title=question, description=answer, color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PrivateQuestionView(discord.ui.View):
    def __init__(self, owner_id: int, category: str):
        super().__init__(timeout=300)
        self.add_item(PrivateQuestionSelect(owner_id, category))

    @discord.ui.button(label="رجوع للأقسام", style=discord.ButtonStyle.secondary, emoji="↩️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = PrivateCategoryView(interaction.user.id)
        await interaction.response.edit_message(
            content="اختر القسم الذي تريد تصفحه:",
            embed=None,
            view=view,
        )


class PublicCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, value=category, emoji=emoji)
            for category, emoji in [
                ("التصنيع والأدوات", "🛠️"),
                ("الموارد والنهب", "📦"),
                ("المهمات والإرشاد", "🧭"),
                ("القتال", "⚔️"),
            ]
        ]
        super().__init__(
            placeholder="اختر قسم الأسئلة...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="faq:category",
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        view = PrivateQuestionView(interaction.user.id, category)
        await interaction.response.send_message(
            f"**قسم {category}**\nاختر السؤال الذي تريد معرفة إجابته:",
            view=view,
            ephemeral=True,
        )


class PublicFAQView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PublicCategorySelect())


class PrivateCategorySelect(discord.ui.Select):
    def __init__(self, owner_id: int):
        self.owner_id = owner_id
        options = [
            discord.SelectOption(label=category, value=category, emoji=emoji)
            for category, emoji in [
                ("التصنيع والأدوات", "🛠️"),
                ("الموارد والنهب", "📦"),
                ("المهمات والإرشاد", "🧭"),
                ("القتال", "⚔️"),
            ]
        ]
        super().__init__(
            placeholder="اختر قسمًا آخر...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("هذه القائمة ليست مخصصة لك.", ephemeral=True)
            return
        category = self.values[0]
        await interaction.response.edit_message(
            content=f"**قسم {category}**\nاختر السؤال الذي تريد معرفة إجابته:",
            view=PrivateQuestionView(self.owner_id, category),
        )


class PrivateCategoryView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=300)
        self.add_item(PrivateCategorySelect(owner_id))


def hierarchy_check(ctx: commands.Context, member: discord.Member) -> str | None:
    """التحقق من أن العضو المستهدف ليس أعلى من المنفذ أو البوت."""
    if member.id == ctx.author.id:
        return "ما تقدر تستخدم الأمر على نفسك."
    if member.id == ctx.guild.owner_id:
        return "ما تقدر تستخدم الأمر على مالك السيرفر."
    if member.id == bot.user.id:
        return "ما أقدر أطبق الأمر على نفسي."
    if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
        return "رتبة العضو أعلى من رتبتك أو مساوية لها."
    if member.top_role >= ctx.guild.me.top_role:
        return "رتبة العضو أعلى من رتبة البوت أو مساوية لها. ارفع رتبة البوت."
    return None


def parse_duration(value: str) -> timedelta | None:
    """أمثلة: 30s، 10m، 2h، 1d. الحد الأقصى 28 يومًا."""
    match = re.fullmatch(r"(\d+)(s|m|h|d)", value.lower())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    seconds = amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    if seconds < 1 or seconds > 28 * 86400:
        return None
    return timedelta(seconds=seconds)


@bot.event
async def on_ready():
    if not getattr(bot, "_faq_initialized", False):
        bot.add_view(PublicFAQView())
        await bot.tree.sync()
        bot._faq_initialized = True
    print(f"تم تسجيل الدخول باسم {bot.user}")


# الترحيب التلقائي في قناة اسمها "الترحيب".
@bot.event
async def on_member_join(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel is None:
        print(f"لم أجد قناة نصية باسم {WELCOME_CHANNEL_NAME} في السيرفر {member.guild.name}")
        return

    embed = discord.Embed(
        title="يا هلا ومرحبا! 🎉",
        description=f"نورت السيرفر {member.mention}\nنتمنى لك وقتًا ممتعًا معنا ❤️",
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"أنت العضو رقم {member.guild.member_count}")
    await channel.send(embed=embed)


# رد تلقائي بسيط على التحية.
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.guild is None:
        return

    content = message.content.strip().casefold()
    greetings = ("السلام عليكم", "سلام عليكم", "السلام عليكم ورحمة الله")
    if any(greeting in content for greeting in greetings):
        await message.reply("وعليكم السلام ورحمة الله وبركاته 🌷", mention_author=False)

    await bot.process_commands(message)


# !✈️ @العضو السبب
@bot.command(name="✈️", help="حظر عضو من السيرفر: !✈️ @العضو السبب")
@commands.guild_only()
@commands.has_guild_permissions(ban_members=True)
@commands.bot_has_guild_permissions(ban_members=True)
async def ban_member(ctx: commands.Context, member: discord.Member, *, reason: str = "لم يُذكر سبب"):
    problem = hierarchy_check(ctx, member)
    if problem:
        await ctx.reply(problem, mention_author=False)
        return
    await member.ban(reason=f"{ctx.author} | {reason}")
    await ctx.reply(f"تم حظر {member.mention} بنجاح. السبب: {reason}", mention_author=False)


# !طرد @العضو السبب
@bot.command(name="طرد", help="طرد عضو من السيرفر: !طرد @العضو السبب")
@commands.guild_only()
@commands.has_guild_permissions(kick_members=True)
@commands.bot_has_guild_permissions(kick_members=True)
async def kick_member(ctx: commands.Context, member: discord.Member, *, reason: str = "لم يُذكر سبب"):
    problem = hierarchy_check(ctx, member)
    if problem:
        await ctx.reply(problem, mention_author=False)
        return
    await member.kick(reason=f"{ctx.author} | {reason}")
    await ctx.reply(f"تم طرد {member.mention} بنجاح. السبب: {reason}", mention_author=False)


# !t @العضو 10m السبب
@bot.command(name="t", help="إعطاء تايم أوت: !t @العضو 10m السبب")
@commands.guild_only()
@commands.has_guild_permissions(moderate_members=True)
@commands.bot_has_guild_permissions(moderate_members=True)
async def timeout_member(
    ctx: commands.Context,
    member: discord.Member,
    duration_text: str,
    *,
    reason: str = "لم يُذكر سبب",
):
    problem = hierarchy_check(ctx, member)
    if problem:
        await ctx.reply(problem, mention_author=False)
        return

    duration = parse_duration(duration_text)
    if duration is None:
        await ctx.reply(
            "المدة غير صحيحة. استخدم مثلًا `30s` أو `10m` أو `2h` أو `1d`، والحد الأقصى 28d.",
            mention_author=False,
        )
        return

    await member.timeout(duration, reason=f"{ctx.author} | {reason}")
    await ctx.reply(
        f"تم إعطاء {member.mention} تايم أوت لمدة `{duration_text}`. السبب: {reason}",
        mention_author=False,
    )


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        message = "ما عندك صلاحية استخدام هذا الأمر."
    elif isinstance(error, commands.BotMissingPermissions):
        message = "البوت ما عنده الصلاحيات المطلوبة. تأكد من صلاحياته ورتبته."
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "ناقصك تحديد العضو أو المدة. راجع طريقة الاستخدام في `/help`."
    elif isinstance(error, commands.MemberNotFound):
        message = "ما قدرت ألقى العضو. استخدم منشن للعضو أو معرّفه."
    elif isinstance(error, commands.NoPrivateMessage):
        message = "هذا الأمر يعمل داخل السيرفر فقط."
    else:
        print(f"حدث خطأ في أمر {ctx.command}: {error}")
        message = "حدث خطأ أثناء تنفيذ الأمر."
    await ctx.reply(message, mention_author=False)


@bot.tree.command(name="faqpost", description="إرسال رسالة الأسئلة الشائعة في هذه القناة")
@app_commands.checks.has_permissions(administrator=True)
async def faqpost(interaction: discord.Interaction):
    await interaction.channel.send(embed=make_embed(), view=PublicFAQView())
    await interaction.response.send_message("تم إرسال قائمة الأسئلة الشائعة.", ephemeral=True)


@faqpost.error
async def faqpost_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        message = "هذا الأمر للمشرفين فقط."
    else:
        message = "حدث خطأ أثناء إرسال القائمة."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


# الأوامر القديمة المعروفة
@bot.tree.command(name="help", description="عرض أوامر البوت")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="أوامر البوت", color=discord.Color.blurple())
    embed.description = (
        "`/help` عرض هذه القائمة\n"
        "`/faqpost` إرسال قائمة الأسئلة الشائعة (للمشرفين)\n"
        "`/axe` معلومات Stone Axe\n"
        "`/fireaxe` معلومات Fire Axe\n"
        "`/stoneaxe` معلومات Stone Axe\n"
        "`/ask` البحث عن إجابة في الأسئلة الشائعة\n\n"
        "**أوامر الإدارة (بادئة !):**\n"
        "`!✈️ @العضو السبب` باند\n"
        "`!طرد @العضو السبب` كيك\n"
        "`!t @العضو 10m السبب` تايم أوت\n"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="axe", description="عرض معلومات صناعة الفأس")
async def axe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "لصناعة Stone Axe تحتاج 3 خشب و2 حجر على Basic Workbench.",
        ephemeral=True,
    )


@bot.tree.command(name="fireaxe", description="عرض معلومات صناعة Fire Axe")
async def fireaxe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "لصناعة Fire Axe تحتاج 4 خشب و2 حجر على Basic Workbench.",
        ephemeral=True,
    )


@bot.tree.command(name="stoneaxe", description="عرض معلومات Stone Axe")
async def stoneaxe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "لصناعة Stone Axe تحتاج 3 خشب و2 حجر على Basic Workbench.",
        ephemeral=True,
    )


@bot.tree.command(name="ask", description="اسأل عن معلومة موجودة في دليل اللعبة")
@app_commands.describe(question="اكتب سؤالك")
async def ask(interaction: discord.Interaction, question: str):
    normalized = question.strip().casefold()
    for category, items in FAQ.items():
        for saved_question, answer in items.items():
            if normalized == saved_question.casefold() or normalized in saved_question.casefold():
                await interaction.response.send_message(
                    f"**{saved_question}**\n{answer}",
                    ephemeral=True,
                )
                return
    await interaction.response.send_message(
        "ما عندي إجابة مؤكدة لهذا السؤال حاليًا. جرّب اختيار سؤال من قائمة `/faqpost`.",
        ephemeral=True,
    )


if not TOKEN:
    raise RuntimeError("لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")

bot.run(TOKEN)
