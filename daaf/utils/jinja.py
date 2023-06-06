from datetime import datetime, timedelta

def format_currency(value, currency = '€'):
    return ("{:0.2f} " + currency ) .format(round(value, 2)) if ( (value != None) & (round(value, 2) != 0)) else ' - '

def variation_mercuriale(value):
    return ' ' if value == 0 else ( '▼ {:0.1f} %'.format(value) if value < 0 else '▲ {:0.1f} %'.format(value)  )

def date_formate(date, format = '%A %w %B %Y', origine = '%Y-%m-%d'):
    pass
    if type(date) == str : date = datetime.strptime(date, origine)
    return date.strftime(format)

def datetime_formate(date, format = '%A %w %B %Y à %H:%M', origine = '%Y-%m-%d %H:%M:%S.%f'):
    return date_formate(date, format, origine)

def lastMonth(date, origine = '%Y-%m-%d'):
    if type(date) == str : date = datetime.strptime(date, origine)
    return date_formate(date.replace(day=1) - timedelta(days=1), origine)