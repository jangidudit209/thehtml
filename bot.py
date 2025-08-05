
import os
import json
import logging
import tempfile
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TEMPLATE_FILE = "Test.html"

def get_option_label(index):
    return chr(65 + index)

def generate_html_from_json(json_data, html_template_path):
    with open(html_template_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for q in soup.find_all(class_="question-card"):
        q.decompose()

    container = soup.find(class_="container")
    if not container:
        container = soup.body

    for idx, q in enumerate(json_data, 1):
        card = soup.new_tag("div", attrs={"class": "question-card"})

        header = soup.new_tag("div", attrs={"class": "question-header"})
        number = soup.new_tag("div", attrs={"class": "question-number"})
        icon = soup.new_tag("i", attrs={"class": "fas fa-question-circle"})
        number.append(icon)
        number.append(f" Question {idx}")
        header.append(number)

        qbox = soup.new_tag("div", attrs={"class": "question-box"})
        qbox.append(BeautifulSoup(q["question"], "html.parser"))

        options = soup.new_tag("div", attrs={"class": "options-container"})
        for i in range(4):
            key = f"option_{i + 1}"
            if q.get(key):
                opt = soup.new_tag("div", attrs={"class": "option-card", "data-option": get_option_label(i)})
                if str(i + 1) == q["answer"]:
                    opt["class"].append("correct")
                opt.append(BeautifulSoup(q[key], "html.parser"))
                options.append(opt)

        solution = soup.new_tag("div", attrs={"class": "question-box"})
        solution["style"] = "background: #e6ffe6; margin-top: 1rem;"
        solution.append(BeautifulSoup(f"<strong>Solution:</strong><br>{q['solution_text']}", "html.parser"))

        card.extend([header, qbox, options, solution])
        container.append(card)

    return str(soup)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document or not document.file_name.endswith(".json"):
        await update.message.reply_text("Please send a valid `.json` file.")
        return

    file = await document.get_file()
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "input.json")
        output_path = os.path.join(tmpdir, "final_test.html")

        await file.download_to_drive(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        final_html = generate_html_from_json(data, TEMPLATE_FILE)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        await update.message.reply_document(document=open(output_path, "rb"), filename="updated_test.html")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
