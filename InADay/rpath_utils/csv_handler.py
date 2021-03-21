import csv

def csv_to_records(filepath, encoding='utf-8'):

    with open(filepath, 'r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        records = list(reader)
        records = [dict(record) for record in records]

    return records