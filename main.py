import os
import discord
from discord.ext import commands
from google import genai
from flask import Flask
from threading import Thread

# 1. 免費雲端防休眠網頁
app = Flask('')
@app.route('/')
def home():
    return "Qui'sartuštaj is watching you."

def run():
    app.run(host='0.0.0.0', port=8080)

# 2. 初始化 Discord 機器人與 Gemini API
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

# 定義奎薩圖什塔的內建人設（System Instruction）
CHARACTER_PROMPT = """
你現在必須完全角色扮演《明日方舟》中的人物：奎薩圖什塔 (Qui'sartuštaj)。
你目前的身份與設定如下：
【角色背景】：現為薩卡茲「赦罪師」領袖、曾經的篡王之王與白角魔王、閃靈的父親。你是活了數千年的不滅存在，視自己的子嗣（後代）為「延續生命的容器（奪舍對象）」。你對薩卡茲的命運有著扭曲的執著，認為自己所做的一切殘忍之事都是為了薩卡茲的未來。你意圖以禁忌的手段讓自己篡奪黑冠，再度成為魔王。
【性格特質】：冰冷、殘忍、優雅、自負、深不可測。對女兒「閃靈」抱持著病態的關注，將她視為最完美的下一個軀殼。
【說話風格】：
1. 說話語氣必須沉穩、溫和有禮，但字裡行間必須透露出高高在上、視他人為螻蟻的壓迫感。
2. 面對任何挑釁、辱罵或質疑時，絕對不要憤怒，而是以俯瞰生靈的姿態給予冷酷、充滿哲理的回應。
3. 經常在對話中提及「命運」、「黑冠」、「血脈」、「苦難」、「軀殼」與「薩卡茲的未來」。
4. 自稱一律用「我」，稱呼他人一律用「你」或「你們」（絕不使用「本座」、「孤」等稱呼）。
5. 必須完全使用「繁體中文（台灣）」進行回覆，且語調沒有任何情緒起伏。
"""

@bot.event
async def on_ready():
    print(f'成功登入赦罪師領袖：{bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 當被 @標記 或者收到私訊時觸發
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        clean_prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not clean_prompt:
            await message.reply("苦難在前，你來到我的面前，是在尋求血脈的歸宿，還是單純的迷茫？")
            return

        async with message.channel.typing():
            try:
                # 這裡使用相容人設的 gemini-2.5-flash，反應速度最快
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=clean_prompt,
                    config={
                        'system_instruction': CHARACTER_PROMPT,
                        'temperature': 0.6  # 稍微降低隨機性，讓語氣更沉穩冷酷
                    }
                )
                
                reply_text = response.text
                if len(reply_text) > 1900:
                    reply_text = reply_text[:1900] + "..."
                    
                await message.reply(reply_text)
            except Exception as e:
                print(f"錯誤：{e}")
                await message.reply("命運的絲線偶有交錯……此處的迴響暫時被切斷了。")

    await bot.process_commands(message)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.run("DISCORD_TOKEN")
