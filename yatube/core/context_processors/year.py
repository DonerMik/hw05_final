from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now_yer = int(datetime.now().year)
    return {
        'year': now_yer
    }
