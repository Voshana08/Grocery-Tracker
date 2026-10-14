from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


def money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


templates.env.filters["money"] = money
