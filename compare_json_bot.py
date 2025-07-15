import json
import re
import logging
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatType

# --- JSON comparison logic (same as before, but as functions) ---

def is_date_string(s):
    # if not isinstance(s, str):
    #     return False
    date_patterns = [
        r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
    ]
    return any(re.match(p, s) for p in date_patterns)

def get_type(val):
    if isinstance(val, str) and is_date_string(val):
        return "date"
    elif isinstance(val, bool):
        return "bool"
    elif isinstance(val, int):
        return "int"
    elif isinstance(val, float):
        return "float"
    elif isinstance(val, str):
        return "string"
    elif isinstance(val, list):
        return "list"
    elif isinstance(val, dict):
        return "dict"
    elif val is None:
        return "null"
    else:
        return type(val).__name__

def get_level(path):
    if not path:
        return 1
    return path.count('.') + path.count('[') + 1

class JSONDiff:
    def __init__(self):
        self.differences = []

    def add(self, kind, path, base_type, target_type, base_val=None, target_val=None):
        self.differences.append({
            "kind": kind,
            "path": path,
            "level": get_level(path),
            "base_type": base_type,
            "target_type": target_type,
            "base_val": base_val,
            "target_val": target_val
        })

    def report(self):
        if not self.differences:
            return "✅ No format differences found. Second JSON fully complies with base JSON."
        lines = ["=== 1-by-1 JSON Format Compliance Report (Base vs Second JSON) ==="]

        # Group differences by kind
        grouped = {"missing_in_target": [], "extra_in_target": [], "type_mismatch": [], "list_length": []}
        for diff in self.differences:
            grouped.get(diff["kind"], []).append(diff)

        # Missing keys
        if grouped["missing_in_target"]:
            lines.append(f"\n❌ Missing in second JSON ({len(grouped['missing_in_target'])}):")
            for diff in grouped["missing_in_target"]:
                lines.append(
                    f"  - {diff['path']} : expected '{diff['base_type']}' (example: {repr(diff['base_val'])})"
                )

        # Extra keys
        if grouped["extra_in_target"]:
            lines.append(f"\n⚠️ Extra in second JSON ({len(grouped['extra_in_target'])}):")
            for diff in grouped["extra_in_target"]:
                lines.append(
                    f"  - {diff['path']} : found '{diff['target_type']}' (example: {repr(diff['target_val'])}) (not in base)"
                )

        # Type mismatches
        if grouped["type_mismatch"]:
            lines.append(f"\n❌ Type mismatches ({len(grouped['type_mismatch'])}):")
            for diff in grouped["type_mismatch"]:
                lines.append(
                    f"  - {diff['path']} : base '{diff['base_type']}' (example: {repr(diff['base_val'])}) vs target '{diff['target_type']}' (example: {repr(diff['target_val'])})"
                )

        # List length mismatches
        if grouped["list_length"]:
            lines.append(f"\n⚠️ List length mismatches ({len(grouped['list_length'])}):")
            for diff in grouped["list_length"]:
                lines.append(
                    f"  - {diff['path']} : base {diff['base_val']} vs target {diff['target_val']}"
                )

        lines.append("\n=== End of Report ===")
        return "\n".join(lines)

def compare_json_format(base, target, path="", diff=None):
    if diff is None:
        diff = JSONDiff()
    base_type = get_type(base)
    target_type = get_type(target)
    if base_type != target_type:
        diff.add("type_mismatch", path or "root", base_type, target_type, base, target)
        return diff

    if base_type == "dict":
        for key in base:
            new_path = f"{path}.{key}" if path else key
            if key not in target:
                diff.add("missing_in_target", new_path, get_type(base[key]), None, base[key], None)
            else:
                compare_json_format(base[key], target[key], new_path, diff)
        for key in target:
            if key not in base:
                new_path = f"{path}.{key}" if path else key
                diff.add("extra_in_target", new_path, None, get_type(target[key]), None, target[key])
    elif base_type == "list":
        if len(base) != len(target):
            diff.add("list_length", path, "list", "list", len(base), len(target))
        min_len = min(len(base), len(target))
        for i in range(min_len):
            compare_json_format(base[i], target[i], f"{path}[{i}]", diff)
    return diff

# --- Telegram Bot logic ---

BASE_JSON_PATH = "visit-sample.json"

# Add this function to check if the chat is a private group
def is_allowed_group(update: Update) -> bool:
    # Only allow in supergroups or groups (not private chats or channels)
    return update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        await update.message.reply_text("❌ This bot only works in private groups.")
        return
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Send me a JSON file (as a document). I will compare it to the base format and reply with the compliance report.\n\nYour chat ID: `{chat_id}`",
        parse_mode="Markdown"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        await update.message.reply_text("❌ This bot only works in private groups.")
        return
    document: Document = update.message.document
    if not document.file_name.endswith('.json'):
        await update.message.reply_text("Please upload a .json file.")
        return

    file = await document.get_file()
    content = await file.download_as_bytearray()
    try:
        target = json.loads(content.decode("utf-8"))
    except Exception as e:
        await update.message.reply_text(f"Could not parse your JSON file: {e}")
        return

    try:
        with open(BASE_JSON_PATH, "r", encoding="utf-8") as f:
            base = json.load(f)
    except Exception as e:
        await update.message.reply_text(f"Could not load base JSON: {e}")
        return

    diff = compare_json_format(base, target)
    report = diff.report()
    # Telegram messages have a 4096 char limit, so split if needed
    for i in range(0, len(report), 4000):
        await update.message.reply_text(f"```\n{report[i:i+4000]}\n```", parse_mode="Markdown")

def main():
    import os
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Please set TELEGRAM_BOT_TOKEN in your environment or .env file.")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()