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

async def dynamic_prefix(bot_instance, message):
    content = message.content
    if content.startswith("!"):
        return "!"
    if content.startswith("-"):
        return "-"
    # منع تشغيل التايم بدون ! مع إبقاء بقية الاختصارات بدون بادئة.
    if content.startswith(("t ", "t\n")):
        return "!"
    return ""

bot = commands.Bot(
    command_prefix=dynamic_prefix,
    intents=intents,
    help_command=None
)

# اسم القناة التي تُرسل فيها رسائل الترحيب تلقائيًا.
WELCOME_CHANNEL_NAME = "الترحيب"
WELCOME_CHANNEL_ID = None
AUTO_ROLE_ID = None
AUTO_REPLIES = {}

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
        bot.add_view(TicketPanel())
        await bot.tree.sync()
        bot._faq_initialized = True
    print(f"تم تسجيل الدخول باسم {bot.user}")


# الترحيب التلقائي في قناة اسمها "الترحيب".
@bot.event
async def on_member_join(member: discord.Member):
    if AUTO_ROLE_ID:
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="رتبة تلقائية عند دخول العضو")
            except discord.Forbidden:
                print("لا يملك البوت صلاحية إدارة الرتب أو أن الرتبة أعلى من رتبته.")
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID) if WELCOME_CHANNEL_ID else discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
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

    # الرد على التحية.
    greetings = ("السلام عليكم", "سلام عليكم", "السلام عليكم ورحمة الله")
    if any(greeting in content for greeting in greetings):
        await message.reply("وعليكم السلام ورحمة الله وبركاته 🌷", mention_author=False)

    # إرسال رابط الماب عند السؤال عنه.
    map_phrases = ("وين الماب", "رابط الماب", "الماب")
    if any(phrase in content for phrase in map_phrases):
        await message.reply(
            "هذا رابط الماب 🎮\\n"
            "https://www.roblox.com/share?code=7186cb344aabe74f92750940522ecc31&type=ExperienceDetails&stamp=1795424194120",
            mention_author=False,
        )

    # الرد إذا كتب العضو نقطة فقط.
    if content == ".":
        await message.reply("منوّر يا عسل 🍯", mention_author=False)

    for keyword, response in AUTO_REPLIES.items():
        if keyword.casefold() in content:
            await message.reply(response, mention_author=False)
            break

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
        "**أوامر الإدارة:**\n"
        "`✈️ @العضو السبب` باند | `/ban`\n"
        "`طرد @العضو السبب` كيك | `/kick`\n"
        "`!t @العضو 10m السبب` تايم أوت | `/time`\n"
        "`ق` قفل الروم | `/lock`\n"
        "`ف` فتح الروم | `/unlock`\n"
        "`-روليت` روليت | `/roulette`\n"
        "`-مافيا` مافيا | `/mafia`\n"
        "`-xo` لعبة XO | `/xo`\n"
        "`-فعالية اسم` فعالية | `/event`\n"
        "`/welcome` الترحيب، `/autoreply` الردود، `/autorole` الرتبة\n"
        "`/ticket-create` إنشاء لوحة التكت، `/ticket-deploy` تنزيلها في روم"
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



# =========================
# أوامر الإدارة بالسلاش والاختصار
# =========================

@bot.command(name="ق")
@commands.guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def lock_prefix(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.reply("🔒 تم قفل الروم.", mention_author=False)

@bot.command(name="ف")
@commands.guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def unlock_prefix(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.reply("🔓 تم فتح الروم.", mention_author=False)

@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يذكر سبب"):
    if member.id == interaction.guild.owner_id or member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("لا يمكنك حظر هذا العضو بسبب رتبة العضو.", ephemeral=True); return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("ارفع رتبة البوت فوق رتبة العضو.", ephemeral=True); return
    await member.ban(reason=f"{interaction.user} | {reason}")
    await interaction.response.send_message(f"✈️ تم حظر {member.mention}.")

@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يذكر سبب"):
    if member.id == interaction.guild.owner_id or (member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id):
        await interaction.response.send_message("لا يمكنك طرد هذا العضو بسبب رتبة العضو.", ephemeral=True); return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("ارفع رتبة البوت فوق رتبة العضو.", ephemeral=True); return
    await member.kick(reason=f"{interaction.user} | {reason}")
    await interaction.response.send_message(f"تم طرد {member.mention}.")

@bot.tree.command(name="time", description="إعطاء عضو تايم أوت")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_time(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "لم يذكر سبب"):
    parsed = parse_duration(duration)
    if parsed is None:
        await interaction.response.send_message("اكتب المدة مثل 10m أو 2h أو 1d (الحد 28d).", ephemeral=True); return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("ارفع رتبة البوت فوق رتبة العضو.", ephemeral=True); return
    await member.timeout(parsed, reason=f"{interaction.user} | {reason}")
    await interaction.response.send_message(f"تم إعطاء {member.mention} تايم أوت لمدة {duration}.")

@bot.tree.command(name="lock", description="قفل الروم الحالي")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم قفل الروم.")

@bot.tree.command(name="unlock", description="فتح الروم الحالي")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
    await interaction.response.send_message("🔓 تم فتح الروم.")


# إعدادات الترحيب والردود والرتبة التلقائية
@bot.tree.command(name="welcome", description="تحديد روم الترحيب التلقائي")
@app_commands.checks.has_permissions(manage_guild=True)
async def slash_welcome(interaction: discord.Interaction, channel: discord.TextChannel):
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"تم ضبط روم الترحيب على {channel.mention}.", ephemeral=True)

@bot.command(name="ترحيب")
@commands.has_guild_permissions(manage_guild=True)
async def prefix_welcome(ctx, channel: discord.TextChannel):
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await ctx.reply(f"تم ضبط روم الترحيب على {channel.mention}.", mention_author=False)

@bot.tree.command(name="autorole", description="تحديد الرتبة التي يحصل عليها العضو عند دخوله")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_autorole(interaction: discord.Interaction, role: discord.Role):
    global AUTO_ROLE_ID
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message("ارفع رتبة البوت فوق الرتبة المطلوبة.", ephemeral=True); return
    AUTO_ROLE_ID = role.id
    await interaction.response.send_message(f"تم ضبط الرتبة التلقائية: {role.mention}.", ephemeral=True)

@bot.command(name="رتبة")
@commands.has_guild_permissions(manage_roles=True)
async def prefix_autorole(ctx, role: discord.Role):
    global AUTO_ROLE_ID
    if role >= ctx.guild.me.top_role:
        await ctx.reply("ارفع رتبة البوت فوق الرتبة المطلوبة.", mention_author=False); return
    AUTO_ROLE_ID = role.id
    await ctx.reply(f"تم ضبط الرتبة التلقائية: {role.mention}.", mention_author=False)

@bot.tree.command(name="autoreply", description="إضافة رد تلقائي لكلمة أو عبارة")
@app_commands.checks.has_permissions(manage_guild=True)
async def slash_autoreply(interaction: discord.Interaction, keyword: str, response: str):
    AUTO_REPLIES[keyword.strip()] = response[:1800]
    await interaction.response.send_message(f"تم إضافة رد تلقائي لعبارة **{keyword}**.", ephemeral=True)

@bot.command(name="رد")
@commands.has_guild_permissions(manage_guild=True)
async def prefix_autoreply(ctx, keyword: str, *, response: str):
    AUTO_REPLIES[keyword.strip()] = response[:1800]
    await ctx.reply(f"تم إضافة رد تلقائي لعبارة **{keyword}**.", mention_author=False)


# =========================
# ألعاب وفعاليات: حد أقصى 15 مشاركًا
# =========================

active_lobbies = {}

class ActivityView(discord.ui.View):
    def __init__(self, kind: str, creator_id: int):
        super().__init__(timeout=None)
        self.kind = kind
        self.creator_id = creator_id
        self.players = []
        self.started = False
        self.message = None

    async def refresh(self, interaction):
        label = f"المشاركون: {len(self.players)}/15"
        embed = discord.Embed(title=f"🎮 {self.kind}", description=f"{label}\n" + ("\n".join(f"• <@{x}>" for x in self.players) if self.players else "لا يوجد مشاركون بعد"), color=discord.Color.blurple())
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="دخول اللعبة", style=discord.ButtonStyle.success, custom_id="activity:join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.started:
            await interaction.response.send_message("اللعبة بدأت بالفعل.", ephemeral=True); return
        if interaction.user.id in self.players:
            await interaction.response.send_message("أنت مسجل بالفعل.", ephemeral=True); return
        if len(self.players) >= 15:
            await interaction.response.send_message("اكتمل العدد (15/15).", ephemeral=True); return
        self.players.append(interaction.user.id)
        await self.refresh(interaction)

    @discord.ui.button(label="الخروج من اللعبة", style=discord.ButtonStyle.secondary, custom_id="activity:leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.players:
            await interaction.response.send_message("أنت غير مسجل.", ephemeral=True); return
        self.players.remove(interaction.user.id)
        await self.refresh(interaction)

    @discord.ui.button(label="بدء اللعبة", style=discord.ButtonStyle.primary, custom_id="activity:start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creator_id and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("بدء اللعبة للمنظم أو الإدارة فقط.", ephemeral=True); return
        if self.started:
            await interaction.response.send_message("اللعبة بدأت بالفعل.", ephemeral=True); return
        if len(self.players) < 2:
            await interaction.response.send_message("تحتاج لاعبين اثنين على الأقل.", ephemeral=True); return
        if self.kind == "المافيا" and len(self.players) < 4:
            await interaction.response.send_message("لعبة المافيا تحتاج 4 لاعبين على الأقل.", ephemeral=True); return
        self.started = True
        if self.kind == "الروليت":
            winner = interaction.guild.get_member(__import__('random').choice(self.players))
            await interaction.response.edit_message(content=f"🎯 بدأت الروليت! الفائز العشوائي: {winner.mention}", view=self)
        elif self.kind == "المافيا":
            import random
            count = len(self.players)
            mafia_count = 2 if count >= 7 else 1
            roles = ["مافيا"] * mafia_count + ["محقق", "دكتور"] + ["مواطن"] * (count-mafia_count-2)
            random.shuffle(roles)
            for uid, role in zip(self.players, roles):
                try: await interaction.guild.get_member(uid).send(f"🎭 دورك في لعبة المافيا: **{role}**. لا تكشف دورك.")
                except (discord.Forbidden, AttributeError): pass
            await interaction.response.edit_message(content=f"🕵️ بدأت لعبة المافيا مع {count} لاعبين. تم إرسال الأدوار على الخاص؛ تبدأ جولة الليل بإدارة المنظم.", view=self)
        else:
            await interaction.response.edit_message(content=f"بدأت فعالية {self.kind} بمشاركة {len(self.players)} لاعبًا!", view=self)

    @discord.ui.button(label="إنهاء اللعبة", style=discord.ButtonStyle.danger, custom_id="activity:end")
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creator_id and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("إنهاء اللعبة للمنظم أو الإدارة فقط.", ephemeral=True); return
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(content=f"⛔ انتهت {self.kind}.", view=self)

async def create_activity(interaction: discord.Interaction, kind: str):
    view = ActivityView(kind, interaction.user.id)
    view.players.append(interaction.user.id)
    embed = discord.Embed(title=f"🎮 {kind}", description=f"المشاركون: 1/15\n• {interaction.user.mention}\n\nاضغط دخول اللعبة للمشاركة.", color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="roulette", description="إنشاء روليت عشوائية بحد أقصى 15 مشاركًا")
async def slash_roulette(interaction: discord.Interaction): await create_activity(interaction, "الروليت")

@bot.command(name="روليت")
async def prefix_roulette(ctx):
    view = ActivityView("الروليت", ctx.author.id); view.players.append(ctx.author.id)
    embed = discord.Embed(title="🎯 الروليت", description=f"المشاركون: 1/15\n• {ctx.author.mention}", color=discord.Color.blurple())
    await ctx.send(embed=embed, view=view)

@bot.tree.command(name="mafia", description="إنشاء لعبة مافيا بحد أقصى 15 مشاركًا")
async def slash_mafia(interaction: discord.Interaction): await create_activity(interaction, "المافيا")

@bot.command(name="مافيا")
async def prefix_mafia(ctx):
    view = ActivityView("المافيا", ctx.author.id); view.players.append(ctx.author.id)
    embed = discord.Embed(title="🕵️ المافيا", description=f"المشاركون: 1/15\n• {ctx.author.mention}", color=discord.Color.blurple())
    await ctx.send(embed=embed, view=view)

@bot.tree.command(name="xo", description="إنشاء فعالية XO بحد أقصى 15 مشاركًا")
async def slash_xo(interaction: discord.Interaction): await create_activity(interaction, "XO")

@bot.command(name="xo")
async def prefix_xo(ctx):
    view = ActivityView("XO", ctx.author.id); view.players.append(ctx.author.id)
    await ctx.send(embed=discord.Embed(title="❎⭕ فعالية XO", description=f"المشاركون: 1/15\n• {ctx.author.mention}", color=discord.Color.blurple()), view=view)

@bot.tree.command(name="event", description="إنشاء فعالية عامة بحد أقصى 15 مشاركًا")
@app_commands.describe(title="اسم الفعالية")
async def slash_event(interaction: discord.Interaction, title: str): await create_activity(interaction, title[:80])

@bot.command(name="فعالية")
async def prefix_event(ctx, *, title="فعالية جديدة"):
    view = ActivityView(title[:80], ctx.author.id); view.players.append(ctx.author.id)
    await ctx.send(embed=discord.Embed(title=f"🎉 {title[:80]}", description=f"المشاركون: 1/15\n• {ctx.author.mention}", color=discord.Color.blurple()), view=view)

# =========================
# نظام التذاكر - Slash فقط
# =========================

class TicketPanel(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="فتح تذكرة", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="ticket:open")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            await interaction.response.send_message(f"لديك تذكرة مفتوحة: {existing.mention}", ephemeral=True); return
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", overwrites=overwrites, reason="فتح تذكرة دعم")
        await channel.send(f"مرحبًا {interaction.user.mention}، اكتب طلبك هنا. سيقوم فريق الإدارة بمساعدتك.")
        await interaction.response.send_message(f"تم فتح تذكرتك: {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticket-create", description="إنشاء لوحة تذاكر في الروم الحالي")
@app_commands.checks.has_permissions(manage_guild=True)
async def ticket_create(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 الدعم الفني", description="اضغط الزر بالأسفل لفتح تذكرة خاصة مع الإدارة.", color=discord.Color.blurple())
    await interaction.channel.send(embed=embed, view=TicketPanel())
    await interaction.response.send_message("تم إنشاء لوحة التذاكر في هذا الروم.", ephemeral=True)

@bot.tree.command(name="ticket-deploy", description="تنزيل لوحة التذاكر في روم تختاره")
@app_commands.checks.has_permissions(manage_guild=True)
async def ticket_deploy(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(title="🎫 الدعم الفني", description="اضغط الزر بالأسفل لفتح تذكرة خاصة مع الإدارة.", color=discord.Color.blurple())
    await channel.send(embed=embed, view=TicketPanel())
    await interaction.response.send_message(f"تم تنزيل لوحة التذاكر في {channel.mention}.", ephemeral=True)


if not TOKEN:
    raise RuntimeError("لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")

bot.run(TOKEN)
