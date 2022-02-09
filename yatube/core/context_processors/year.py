from datetime import date


def year(request):
    y = date.today().year
    print(y)
    return {
        'year': y
    }
