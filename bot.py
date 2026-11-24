import os, re, random
from datetime import timedelta
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("ضع DISCORD_TOKEN في متغيرات البيئة.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

MAP_URL = "https://www.roblox.com/share?code=7186cb344aabe74f92750940522ecc31&type=ExperienceDetails&stamp=1795424194120"
WELCOME_CHANNEL_ID = None
WELCOME_CHANNEL_NAME = "الترحيب"
AUTO_ROLE_ID = None
AUTO_REPLIES = {}

async def dynamic_prefix(bot, message):
    return "!" if message.content.startswith("!") else "-" if message.content.startswith("-") else ""

bot = commands.Bot(command_prefix=dynamic_prefix, intents=intents, help_command=None)

RULES = [
    "احترم الجميع؛ يُمنع التنمر والإساءة والتمييز.",
    "يُمنع السبام والمنشن المتكرر والإعلانات غير المصرح بها.",
    "استخدم كل قناة لغرضها، ولا تكرر الاقتراح أو البلاغ.",
    "بلاغ اللعبة يتضمن المنصة وخطوات تكرار المشكلة، وصورة أو مقطعاً إن أمكن.",
    "لا تشارك كلمات المرور أو بياناتك الشخصية أو روابط مشبوهة.",
    "التزم بقواعد Roblox وDiscord واحترم حقوق أصحاب المحتوى.",
    "استخدم قنوات الدعم المخصصة، ولا تطلب صلاحيات إدارية.",
    "قد تؤدي المخالفة إلى تنبيه أو كتم أو حظر بحسب شدتها وتكرارها.",
    "ممنوع استغلال السيرفر كنشر لسيرفرك أو مابك.",
]

def rules_embed():
    e = discord.Embed(
        title="📜 قوانين مجتمع ISAJX",
        description=("مرحباً بك! هذا السيرفر يجمع مجتمع لعبة وهم: الكابوس الأخير ومحتوى الألعاب على YouTube وTikTok.\n\n"
        + "\n".join(f"**{i}.** {r}" for i, r in enumerate(RULES, 1))
        + "\n\nبدخولك للسيرفر فأنت توافق على هذه القواعد.\n— الإدارة"),
        color=discord.Color.blurple())
    return e

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
def parse_duration(value):
    m = re.fullmatch(r"(\\d+)(s|m|h|d)", value.lower())
    if not m: return None
    n, unit = int(m.group(1)), m.group(2)
    seconds = n * {"s":1, "m":60, "h":3600, "d":86400}[unit]
    return timedelta(seconds=seconds) if 1 <= seconds <= 28*86400 else None

def hierarchy_error(guild, actor, member):
    if member.id == actor.id: return "ما تقدر تستخدم الأمر على نفسك."
    if member.id == guild.owner_id: return "ما تقدر تستخدم الأمر على مالك السيرفر."
    if member.id == bot.user.id: return "ما أقدر أطبق الأمر على نفسي."
    if actor.id != guild.owner_id and member.top_role >= actor.top_role: return "رتبة العضو أعلى من رتبتك أو مساوية لها."
    if member.top_role >= guild.me.top_role: return "رتبة العضو أعلى من رتبة البوت. ارفع رتبة البوت."
    return None

class FAQCategorySelect(discord.ui.Select):
    def __init__(self):
        opts = [discord.SelectOption(label=k, value=k) for k in FAQ]
        super().__init__(placeholder="اختر قسم الأسئلة...", options=opts)
    async def callback(self, interaction):
        await interaction.response.send_message("اختر السؤال:", view=FAQQuestionView(interaction.user.id, self.values[0]), ephemeral=True)

class FAQQuestionSelect(discord.ui.Select):
    def __init__(self, owner, category):
        self.owner, self.category = owner, category
        self.questions = list(FAQ[category])
        super().__init__(placeholder="اختر السؤال...", options=[discord.SelectOption(label=q[:100], value=str(i)) for i,q in enumerate(self.questions)])
    async def callback(self, interaction):
        if interaction.user.id != self.owner:
            return await interaction.response.send_message("هذه القائمة ليست مخصصة لك.", ephemeral=True)
        q = self.questions[int(self.values[0])]
        await interaction.response.send_message(embed=discord.Embed(title=q, description=FAQ[self.category][q], color=discord.Color.green()), ephemeral=True)

class FAQQuestionView(discord.ui.View):
    def __init__(self, owner, category):
        super().__init__(timeout=300)
        self.add_item(FAQQuestionSelect(owner, category))

class FAQView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(FAQCategorySelect())

class TicketPanel(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="فتح تذكرة", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="isajx:ticket_open")
    async def open_ticket(self, interaction, button):
        g = interaction.guild
        old = discord.utils.get(g.text_channels, name=f"ticket-{interaction.user.id}")
        if old: return await interaction.response.send_message(f"لديك تذكرة مفتوحة: {old.mention}", ephemeral=True)
        perms = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        ch = await g.create_text_channel(f"ticket-{interaction.user.id}", overwrites=perms)
        await ch.send(f"مرحباً {interaction.user.mention}، اكتب طلبك هنا وسيقوم فريق الإدارة بمساعدتك.")
        await interaction.response.send_message(f"تم فتح تذكرتك: {ch.mention}", ephemeral=True)

class ActivityView(discord.ui.View):
    def __init__(self, kind, creator):
        super().__init__(timeout=7200)
        self.kind, self.creator = kind, creator
        self.players, self.started = [creator], False
    def embed(self):
        people = "\\n".join(f"• <@{u}>" for u in self.players)
        return discord.Embed(title=f"🎮 {self.kind}", description=f"**المشاركون: {len(self.players)}/15**\\n{people}\\n\\nاستخدم الأزرار للدخول أو الخروج.", color=discord.Color.blurple())
    @discord.ui.button(label="دخول اللعبة", style=discord.ButtonStyle.success, emoji="➕")
    async def join(self, interaction, button):
        if self.started: return await interaction.response.send_message("اللعبة بدأت بالفعل.", ephemeral=True)
        if interaction.user.id in self.players: return await interaction.response.send_message("أنت مسجل بالفعل.", ephemeral=True)
        if len(self.players) >= 15: return await interaction.response.send_message("اكتمل العدد 15/15.", ephemeral=True)
        self.players.append(interaction.user.id)
        await interaction.response.edit_message(embed=self.embed(), view=self)
    @discord.ui.button(label="الخروج من اللعبة", style=discord.ButtonStyle.secondary, emoji="➖")
    async def leave(self, interaction, button):
        if self.started: return await interaction.response.send_message("اللعبة بدأت بالفعل.", ephemeral=True)
        if interaction.user.id not in self.players: return await interaction.response.send_message("أنت غير مسجل.", ephemeral=True)
        self.players.remove(interaction.user.id)
        await interaction.response.edit_message(embed=self.embed(), view=self)
    @discord.ui.button(label="بدء اللعبة", style=discord.ButtonStyle.primary, emoji="▶️")
    async def start(self, interaction, button):
        if interaction.user.id != self.creator and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("بدء اللعبة للمنظم أو الإدارة فقط.", ephemeral=True)
        if self.started: return await interaction.response.send_message("اللعبة بدأت بالفعل.", ephemeral=True)
        minimum = 4 if self.kind == "المافيا" else 2
        if len(self.players) < minimum: return await interaction.response.send_message(f"تحتاج {minimum} لاعبين على الأقل.", ephemeral=True)
        self.started = True
        for item in self.children:
            if item.label in ("دخول اللعبة", "الخروج من اللعبة", "بدء اللعبة"): item.disabled = True
        if self.kind == "الروليت":
            result = f"🎯 الفائز العشوائي: <@{random.choice(self.players)}>"
        elif self.kind == "الغميضة":
            result = f"🙈 الباحث هو <@{random.choice(self.players)}>، وعلى المنظم إدارة وقت الاختباء."
        elif self.kind == "الكراسي":
            result = f"🪑 اختيار الجولة العشوائي: <@{random.choice(self.players)}>."
        elif self.kind == "المافيا":
            roles = ["مافيا"] * (2 if len(self.players) >= 7 else 1) + ["محقق", "دكتور"]
            roles += ["مواطن"] * (len(self.players)-len(roles))
            random.shuffle(roles)
            sent = 0
            for uid, role in zip(self.players, roles):
                member = interaction.guild.get_member(uid)
                if member:
                    try: await member.send(f"🎭 دورك في المافيا: **{role}**. لا تكشف دورك."); sent += 1
                    except discord.Forbidden: pass
            result = f"🕵️ بدأت المافيا. أُرسلت الأدوار على الخاص إلى {sent} لاعباً. المنظم يدير الجولات."
        else: result = f"بدأت فعالية {self.kind} بمشاركة {len(self.players)} لاعباً."
        await interaction.response.edit_message(content=result, embed=None, view=self)
    @discord.ui.button(label="إنهاء اللعبة", style=discord.ButtonStyle.danger, emoji="⛔")
    async def end(self, interaction, button):
        if interaction.user.id != self.creator and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("إنهاء اللعبة للمنظم أو الإدارة فقط.", ephemeral=True)
        for item in self.children: item.disabled = True
        await interaction.response.edit_message(content=f"⛔ انتهت فعالية {self.kind}.", embed=None, view=self)

async def make_activity(interaction, kind):
    view = ActivityView(kind, interaction.user.id)
    await interaction.response.send_message(embed=view.embed(), view=view)

@bot.event
async def on_ready():
    if not getattr(bot, "ticket_view_ready", False):
        bot.add_view(TicketPanel())
        bot.ticket_view_ready = True
    try:
        for g in bot.guilds:
            ref = discord.Object(id=g.id)
            bot.tree.copy_global_to(guild=ref)
            await bot.tree.sync(guild=ref)
    except Exception as e: print("Sync error:", repr(e))
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if AUTO_ROLE_ID:
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            try: await member.add_roles(role, reason="رتبة تلقائية عند الدخول")
            except discord.Forbidden: print("تعذر منح الرتبة؛ تحقق من صلاحيات البوت وترتيب الرتب.")
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID) if WELCOME_CHANNEL_ID else discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        e = discord.Embed(title="يا هلا ومرحبا! 🎉", description=f"نورت السيرفر {member.mention}\\nنتمنى لك وقتاً ممتعاً معنا ❤️", color=discord.Color.blurple())
        e.set_thumbnail(url=member.display_avatar.url)
        e.set_footer(text=f"أنت العضو رقم {member.guild.member_count}")
        await channel.send(embed=e)

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    content = message.content.strip().casefold()
    if "السلام عليكم" in content or "سلام عليكم" in content:
        await message.reply("وعليكم السلام ورحمة الله وبركاته 🌷", mention_author=False)
    if content in ("وين الماب", "رابط الماب", "الماب", "وين الماب؟", "رابط الماب؟"):
        await message.reply(f"هذا رابط الماب 🎮\\n{MAP_URL}", mention_author=False)
    if content == ".": await message.reply("منوّر يا عسل 🍯", mention_author=False)
    for key, value in AUTO_REPLIES.items():
        if key.casefold() in content:
            await message.reply(value, mention_author=False); break
    await bot.process_commands(message)

# Prefix moderation commands
@bot.command(name="✈️")
@commands.has_guild_permissions(ban_members=True)
@commands.bot_has_guild_permissions(ban_members=True)
async def ban_prefix(ctx, member: discord.Member, *, reason="لم يُذكر سبب"):
    err = hierarchy_error(ctx.guild, ctx.author, member)
    if err: return await ctx.reply(err, mention_author=False)
    await member.ban(reason=f"{ctx.author}: {reason}")
    await ctx.reply(f"✈️ تم حظر {member.mention}. السبب: {reason}", mention_author=False)

@bot.command(name="طرد")
@commands.has_guild_permissions(kick_members=True)
@commands.bot_has_guild_permissions(kick_members=True)
async def kick_prefix(ctx, member: discord.Member, *, reason="لم يُذكر سبب"):
    err = hierarchy_error(ctx.guild, ctx.author, member)
    if err: return await ctx.reply(err, mention_author=False)
    await member.kick(reason=f"{ctx.author}: {reason}")
    await ctx.reply(f"تم طرد {member.mention}. السبب: {reason}", mention_author=False)

@bot.command(name="t!")
@commands.has_guild_permissions(moderate_members=True)
@commands.bot_has_guild_permissions(moderate_members=True)
async def time_prefix(ctx, member: discord.Member, duration: str, *, reason="لم يُذكر سبب"):
    err = hierarchy_error(ctx.guild, ctx.author, member)
    parsed = parse_duration(duration)
    if err: return await ctx.reply(err, mention_author=False)
    if not parsed: return await ctx.reply("استخدم مدة مثل 10m أو 2h أو 1d (الحد 28d).", mention_author=False)
    await member.timeout(parsed, reason=f"{ctx.author}: {reason}")
    await ctx.reply(f"تم إعطاء {member.mention} تايم لمدة {duration}.", mention_author=False)

@bot.command(name="تكلم")
@commands.has_guild_permissions(moderate_members=True)
@commands.bot_has_guild_permissions(moderate_members=True)
async def untime_prefix(ctx, member: discord.Member):
    err = hierarchy_error(ctx.guild, ctx.author, member)
    if err: return await ctx.reply(err, mention_author=False)
    if not member.timed_out_until: return await ctx.reply("العضو ما عليه تايم حالياً.", mention_author=False)
    await member.timeout(None, reason=f"فك التايم بواسطة {ctx.author}")
    await ctx.reply(f"تم فك التايم عن {member.mention}.", mention_author=False)

@bot.command(name="ق")
@commands.has_guild_permissions(manage_channels=True)
async def lock_prefix(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.reply("🔒 تم قفل الروم.", mention_author=False)

@bot.command(name="ف")
@commands.has_guild_permissions(manage_channels=True)
async def unlock_prefix(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.reply("🔓 تم فتح الروم.", mention_author=False)

# Slash moderation
@bot.tree.command(name="ban", description="حظر عضو")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction, member: discord.Member, reason: str="لم يُذكر سبب"):
    err = hierarchy_error(interaction.guild, interaction.user, member)
    if err: return await interaction.response.send_message(err, ephemeral=True)
    await member.ban(reason=f"{interaction.user}: {reason}")
    await interaction.response.send_message(f"✈️ تم حظر {member.mention}.")

@bot.tree.command(name="kick", description="طرد عضو")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction, member: discord.Member, reason: str="لم يُذكر سبب"):
    err = hierarchy_error(interaction.guild, interaction.user, member)
    if err: return await interaction.response.send_message(err, ephemeral=True)
    await member.kick(reason=f"{interaction.user}: {reason}")
    await interaction.response.send_message(f"تم طرد {member.mention}.")

@bot.tree.command(name="time", description="إعطاء عضو تايم أوت")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_time(interaction, member: discord.Member, duration: str, reason: str="لم يُذكر سبب"):
    err = hierarchy_error(interaction.guild, interaction.user, member)
    parsed = parse_duration(duration)
    if err: return await interaction.response.send_message(err, ephemeral=True)
    if not parsed: return await interaction.response.send_message("استخدم 10m أو 2h أو 1d (الحد 28d).", ephemeral=True)
    await member.timeout(parsed, reason=f"{interaction.user}: {reason}")
    await interaction.response.send_message(f"تم إعطاء {member.mention} تايم لمدة {duration}.")

@bot.tree.command(name="تكلم", description="فك التايم أوت")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_untime(interaction, member: discord.Member):
    err = hierarchy_error(interaction.guild, interaction.user, member)
    if err: return await interaction.response.send_message(err, ephemeral=True)
    if not member.timed_out_until: return await interaction.response.send_message("العضو ما عليه تايم حالياً.", ephemeral=True)
    await member.timeout(None, reason=f"فك التايم بواسطة {interaction.user}")
    await interaction.response.send_message(f"تم فك التايم عن {member.mention}.")

@bot.tree.command(name="lock", description="قفل الروم")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم قفل الروم.")

@bot.tree.command(name="unlock", description="فتح الروم")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
    await interaction.response.send_message("🔓 تم فتح الروم.")

# Welcome, autorole, auto replies
@bot.tree.command(name="welcome", description="تحديد روم الترحيب")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_welcome(interaction, channel: discord.TextChannel):
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"تم ضبط روم الترحيب: {channel.mention}", ephemeral=True)

@bot.tree.command(name="autorole", description="تحديد رتبة الأعضاء الجدد")
@app_commands.checks.has_permissions(manage_roles=True)
async def set_role(interaction, role: discord.Role):
    global AUTO_ROLE_ID
    if role >= interaction.guild.me.top_role:
        return await interaction.response.send_message("ارفع رتبة البوت فوق الرتبة المطلوبة.", ephemeral=True)
    AUTO_ROLE_ID = role.id
    await interaction.response.send_message(f"تم ضبط الرتبة التلقائية: {role.mention}", ephemeral=True)

@bot.tree.command(name="autoreply", description="إضافة رد تلقائي")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_reply(interaction, keyword: str, response: str):
    AUTO_REPLIES[keyword.strip()] = response[:1800]
    await interaction.response.send_message(f"تمت إضافة رد تلقائي لعبارة {keyword}.", ephemeral=True)

# Rules and FAQ
@bot.tree.command(name="rules", description="عرض قوانين مجتمع ISAJX")
async def rules_slash(interaction):
    await interaction.response.send_message(embed=rules_embed())

@bot.command(name="قوانين")
async def rules_prefix(ctx):
    await ctx.send(embed=rules_embed())

@bot.tree.command(name="faqpost", description="إرسال قائمة الأسئلة الشائعة")
@app_commands.checks.has_permissions(administrator=True)
async def faqpost(interaction):
    e = discord.Embed(title="دليل المساعدة والأسئلة الشائعة", description="اختر القسم ثم السؤال. الإجابة تظهر لك بشكل خاص.", color=discord.Color.blurple())
    await interaction.channel.send(embed=e, view=FAQView())
    await interaction.response.send_message("تم إرسال القائمة.", ephemeral=True)

@bot.tree.command(name="axe", description="معلومات صناعة الفأس")
async def axe(interaction):
    await interaction.response.send_message("لصناعة Stone Axe تحتاج 3 خشب و2 حجر على Basic Workbench.", ephemeral=True)

@bot.tree.command(name="fireaxe", description="معلومات صناعة Fire Axe")
async def fireaxe(interaction):
    await interaction.response.send_message("لصناعة Fire Axe تحتاج 4 خشب و2 حجر على Basic Workbench.", ephemeral=True)

@bot.tree.command(name="stoneaxe", description="معلومات Stone Axe")
async def stoneaxe(interaction):
    await interaction.response.send_message("لصناعة Stone Axe تحتاج 3 خشب و2 حجر على Basic Workbench.", ephemeral=True)

@bot.tree.command(name="ask", description="البحث في الأسئلة الشائعة")
async def ask(interaction, question: str):
    qn = question.strip().casefold()
    for cat, items in FAQ.items():
        for q, a in items.items():
            if qn == q.casefold() or qn in q.casefold():
                return await interaction.response.send_message(f"**{q}**\\n{a}", ephemeral=True)
    await interaction.response.send_message("ما عندي إجابة مؤكدة. استخدم /faqpost.", ephemeral=True)

@bot.tree.command(name="help", description="عرض أوامر البوت")
async def help_slash(interaction):
    e = discord.Embed(title="أوامر بوت ISAJX", color=discord.Color.blurple())
    e.description = (
        "**الإدارة:** `/ban` `/kick` `/time` `/تكلم` `/lock` `/unlock`\\n"
        "**الإعدادات:** `/welcome` `/autorole` `/autoreply`\\n"
        "**المجتمع:** `/rules` أو `-قوانين`، `/faqpost`، `/ask`\\n"
        "**الألعاب:** `/roulette` `/mafia` `/xo` `/chairs` `/hideandseek` `/event`\\n"
        "**التكت:** `/ticket-create` `/ticket-deploy`\\n"
        "**اختصارات:** `!✈️`، `!طرد`، `!t!`، `!تكلم`، `-روليت`، `-مافيا`، `-xo`، `-كراسي`، `-غميضه`، `-فعالية اسم`."
    )
    await interaction.response.send_message(embed=e, ephemeral=True)

# Games, each lobby capped at 15 members
@bot.tree.command(name="roulette", description="إنشاء روليت")
async def roulette(interaction): await make_activity(interaction, "الروليت")
@bot.tree.command(name="mafia", description="إنشاء مافيا")
async def mafia(interaction): await make_activity(interaction, "المافيا")
@bot.tree.command(name="xo", description="إنشاء فعالية XO")
async def xo(interaction): await make_activity(interaction, "XO")
@bot.tree.command(name="chairs", description="إنشاء لعبة الكراسي")
async def chairs(interaction): await make_activity(interaction, "الكراسي")
@bot.tree.command(name="hideandseek", description="إنشاء لعبة الغميضة")
async def hideandseek(interaction): await make_activity(interaction, "الغميضة")
@bot.tree.command(name="event", description="إنشاء فعالية عامة")
async def event_slash(interaction, title: str): await make_activity(interaction, title[:80])

@bot.command(name="روليت")
async def roulette_cmd(ctx):
    v=ActivityView("الروليت",ctx.author.id); await ctx.send(embed=v.embed(),view=v)
@bot.command(name="مافيا")
async def mafia_cmd(ctx):
    v=ActivityView("المافيا",ctx.author.id); await ctx.send(embed=v.embed(),view=v)
@bot.command(name="xo")
async def xo_cmd(ctx):
    v=ActivityView("XO",ctx.author.id); await ctx.send(embed=v.embed(),view=v)
@bot.command(name="كراسي")
async def chairs_cmd(ctx):
    v=ActivityView("الكراسي",ctx.author.id); await ctx.send(embed=v.embed(),view=v)
@bot.command(name="غميضه")
async def hide_cmd(ctx):
    v=ActivityView("الغميضة",ctx.author.id); await ctx.send(embed=v.embed(),view=v)
@bot.command(name="فعالية")
async def event_cmd(ctx, *, title="فعالية جديدة"):
    v=ActivityView(title[:80],ctx.author.id); await ctx.send(embed=v.embed(),view=v)

# Ticket commands: slash only
@bot.tree.command(name="ticket-create", description="إنشاء لوحة تذاكر في الروم الحالي")
@app_commands.checks.has_permissions(manage_guild=True)
async def ticket_create(interaction):
    e=discord.Embed(title="🎫 الدعم الفني",description="اضغط الزر لفتح تذكرة خاصة مع الإدارة.",color=discord.Color.blurple())
    await interaction.channel.send(embed=e,view=TicketPanel())
    await interaction.response.send_message("تم إنشاء لوحة التذاكر.",ephemeral=True)

@bot.tree.command(name="ticket-deploy", description="تنزيل لوحة التذاكر في روم تختاره")
@app_commands.checks.has_permissions(manage_guild=True)
async def ticket_deploy(interaction, channel: discord.TextChannel):
    e=discord.Embed(title="🎫 الدعم الفني",description="اضغط الزر لفتح تذكرة خاصة مع الإدارة.",color=discord.Color.blurple())
    await channel.send(embed=e,view=TicketPanel())
    await interaction.response.send_message(f"تم تنزيل لوحة التذاكر في {channel.mention}.",ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    if isinstance(error, commands.MissingPermissions): msg="ما عندك صلاحية استخدام هذا الأمر."
    elif isinstance(error, commands.BotMissingPermissions): msg="البوت ما عنده الصلاحيات المطلوبة أو رتبته منخفضة."
    elif isinstance(error, commands.MissingRequiredArgument): msg="ناقصك تحديد العضو أو المدة. راجع /help."
    elif isinstance(error, commands.MemberNotFound): msg="ما قدرت ألقى العضو. استخدم منشن أو معرّف العضو."
    else:
        print("Command error:", repr(error)); msg="حدث خطأ أثناء تنفيذ الأمر."
    await ctx.reply(msg, mention_author=False)

bot.run(TOKEN)
