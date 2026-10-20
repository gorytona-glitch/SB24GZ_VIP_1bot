import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# FreeNewsApi: no key required, supports country=NG filtering for Nigerian news[citation:4]
NEWS_API_URL = "https://freenewsapi.ai/v1/search"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello! I am @SB24GZ_VIP_1bot.\n"
        "I provide the latest news updates from Nigeria.\n\n"
        "Send /news to get today's headlines."
    )

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching Nigerian news, please wait...")

    params = {
        "country": "NG",
        "date": "today",
        "sort": "date",
        "size": 8
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(NEWS_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = data.get("articles", data.get("data", []))

        if not articles:
            await update.message.reply_text("No Nigerian news available at the moment. Please try again later.")
            return

        lines = []
        for i, article in enumerate(articles[:8], 1):
            title = article.get("title", "No title")
            source = article.get("source", article.get("publisher", ""))
            url = article.get("url", article.get("link", ""))
            
            line = f"{i}. {title}"
            if source:
                line += f"\n   📌 {source}"
            if url:
                line += f"\n   🔗 {url}"
            lines.append(line)

        reply = "🇳🇬 Latest Nigeria Updates:\n\n" + "\n\n".join(lines)
        await update.message.reply_text(reply, disable_web_page_preview=True)

    except httpx.TimeoutException:
        logger.error("News API timeout")
        await update.message.reply_text("⚠️ Request timed out, please try again later.")
    except Exception as e:
        logger.error(f"News API error: {e}")
        await update.message.reply_text("⚠️ Failed to fetch news, please try again later.")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", get_news))

    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
