import re


def escape_md(text: str) -> str:
    """
    Экранирует все зарезервированные символы для MarkdownV2
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))