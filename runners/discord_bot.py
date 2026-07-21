# runners/discord_bot.py — 디스코드 얼굴.
# 채널에 "!회사 <의뢰>" 를 올리면 회사가 일해서 산출물을 채널에 올려준다.
# 상시 실행 프로세스(봇이 접속 유지). 봇 토큰은 .env 의 DISCORD_BOT_TOKEN.

import asyncio
import os

import discord
from dotenv import load_dotenv

from company import Company

OUTPUT_DIR = "output"
DELIVERABLES = [
    "requirements.md", "design.html", "app.html",
    "qa.md", "marketing.md", "summary.md",
]


def build_client() -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True  # 메시지 내용 읽기 (개발자 포털에서도 켜야 함)
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"디스코드 봇 접속 완료: {client.user}")

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:      # 봇 자기 말은 무시(무한루프 방지)
            return
        if not message.content.startswith("!회사"):
            return

        request = message.content[len("!회사"):].strip()
        if not request:
            await message.channel.send("사용법: `!회사 <프로젝트 의뢰 한 줄>`")
            return

        await message.channel.send(f"🏢 '{request}' 착수합니다. 잠시만요...")

        # build()는 LLM 호출로 오래 걸리는 '블로킹' 작업 → 별도 스레드에서 돌려
        # 봇의 이벤트 루프를 막지 않는다.
        company = Company()
        await asyncio.to_thread(company.build, request)

        # 산출물 파일들을 채널에 첨부로 올린다.
        files = [
            discord.File(os.path.join(OUTPUT_DIR, name))
            for name in DELIVERABLES
            if os.path.exists(os.path.join(OUTPUT_DIR, name))
        ]
        await message.channel.send("✅ 완료! 산출물입니다.", files=files)

    return client


def main():
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN 이 .env 에 없습니다.")
    build_client().run(token)


if __name__ == "__main__":
    main()