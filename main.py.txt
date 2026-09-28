import os
import discord
from discord.ext import commands
from google import genai
from flask import Flask
from threading import Thread

# 1. 為了讓免費雲端不睡著，建立一個簡單的網頁伺服器
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# 2. 初始化 Discord 機器人與 Gemini API
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 讀取環境變數（稍後在雲端後台設定）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

@bot.event
async def on_ready():
    print(f'成功登入機器人：{bot.user}')

@bot.event
async def on_message(message):
    # 忽略機器人自己的訊息
    if message.author == bot.user:
        return

    # 當被 @標記 或者收到私訊時觸發 AI
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # 移除訊息中的 @標記 乾淨字串
        clean_prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not clean_prompt:
            await message.reply("找我有什麼事嗎？")
            return

        # 觸發 Discord 的「正在輸入中...」特效，同時自動處理延遲回應
        async with message.channel.typing():
            try:
                # 呼叫免費的 Gemini 2.5 Flash 模型
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=clean_prompt,
                )
                
                # Discord 單則訊息上限 2000 字，進行簡單截斷防止報錯
                reply_text = response.text
                if len(reply_text) > 1900:
                    reply_text = reply_text[:1900] + "...(字數過長已截斷)"
                    
                await message.reply(reply_text)
            except Exception as e:
                print(f"錯誤：{e}")
                await message.reply("抱歉，我現在大腦有點混亂，請稍後再試。")

    await bot.process_commands(message)

# 啟動網頁伺服器與機器人
if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.run(DISCORD_TOKEN)
