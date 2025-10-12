def generate_html(data: dict) -> str:
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчёт по данным</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f9f9f9;
        }
        h2 {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 8px;
        }
        .block {
            background-color: white;
            border: 1px solid #ccc;
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .entry {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .key {
            font-weight: bold;
        }
        ul {
            padding-left: 20px;
        }
        .value {
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <h1>Отчёт</h1>
"""

    items = data.get("data", {}).get("items", [])

    for item in items:
        source = item.get("source", {})
        collection = source.get("collection", "Без названия")
        html += f'<div class="block">\n<h2>{collection}</h2>\n'

        hits = item.get("hits", {}).get("items", [])
        for hit in hits:
            html += '<div class="entry">\n'
            for key, value in hit.items():
                html += f'<div class="key">{key}:</div>'
                html += f'<div class="value">{format_value(value)}</div>\n'
            html += '</div>\n'
        html += '</div>\n'

    html += """
</body>
</html>
"""
    return html


def format_value(value):
    """Рекурсивно форматирует значение для HTML"""
    if isinstance(value, dict):
        return "<ul>" + "".join(f"<li><strong>{k}:</strong> {format_value(v)}</li>" for k, v in value.items()) + "</ul>"
    elif isinstance(value, list):
        return "<ul>" + "".join(f"<li>{format_value(v)}</li>" for v in value) + "</ul>"
    else:
        return str(value)
