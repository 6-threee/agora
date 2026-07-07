import csv

def top_forms(n, csv_path):
    """Return the n most frequent word forms, rank order, header excluded."""
    forms = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip 'word,count' header
        for row in reader:
            if not row:
                continue
            forms.append(row[0])
            if len(forms) >= n:
                break
    return forms
