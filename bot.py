import os
import discord
from discord import app_commands
from discord.ext import commands

# ضع توكن البوت في متغير بيئة اسمه DISCORD_TOKEN في منصة الاستضافة.
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

FAQ = {
    "fire axe": "تصنع Fire Axe على Basic Workbench باستخدام 4 خشب و2 حجر.",
    "فاير اكس": "تصنع Fire Axe على Basic Workbench باستخدام 4 خشب و2 حجر.",
    "stone axe": "تصنع Stone Axe باستخدام 3 خشب و2 حجر.",
    "ستون اكس": "تصنع Stone Axe باستخدام 3 خشب و2 حجر.",
}

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"تم تسجيل {len(synced)} أمر سلاش.")
    except Exception as error:
        print(f"تعذر تسجيل أوامر السلاش: {error}")
    print(f"تم تسجيل الدخول باسم {bot.user}")

@bot.tree.command(name="help", description="عرض أوامر بوت المساعدة")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="مساعدة بوت اللعبة",
        description="الأوامر المتاحة:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="/axe", value="معلومات عن الفؤوس", inline=False)
    embed.add_field(name="/fireaxe", value="طريقة تصنيع Fire Axe", inline=False)
    embed.add_field(name="/stoneaxe", value="طريقة تصنيع Stone Axe", inline=False)
    embed.add_field(name="/ask", value="اسأل عن Fire Axe أو Stone Axe", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="axe", description="معلومات عن الفؤوس")
async def axe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🪓 **Fire Axe:** 4 خشب + 2 حجر على Basic Workbench.\n"
        "🪓 **Stone Axe:** 3 خشب + 2 حجر.",
        ephemeral=False
    )

@bot.tree.command(name="fireaxe", description="طريقة تصنيع Fire Axe")
async def fireaxe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🪓 **Fire Axe**\nالمواد: 4 خشب و2 حجر.\nمكان التصنيع: Basic Workbench."
    )

@bot.tree.command(name="stoneaxe", description="طريقة تصنيع Stone Axe")
async def stoneaxe(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🪓 **Stone Axe**\nالمواد: 3 خشب و2 حجر."
    )

@bot.tree.command(name="ask", description="اسأل البوت عن معلومات التصنيع")
@app_commands.describe(question="اكتب سؤالك عن أدوات اللعبة")
async def ask(interaction: discord.Interaction, question: str):
    normalized = question.lower()
    for keyword, answer in FAQ.items():
        if keyword in normalized:
            await interaction.response.send_message(answer)
            return
    await interaction.response.send_message(
        "ما عندي إجابة محفوظة لهذا السؤال حاليًا. جرّب السؤال عن Fire Axe أو Stone Axe.",
        ephemeral=True
    )

if not TOKEN:
    raise RuntimeError("لم يتم ضبط DISCORD_TOKEN. أضف التوكن كمتغير سري في منصة الاستضافة.")
bot.run(TOKEN)
