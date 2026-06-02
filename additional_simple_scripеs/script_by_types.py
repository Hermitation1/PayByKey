import csv

d = {}

with open("amount-2026-5.csv", "r") as f:
    reader = csv.reader(f)
    headers = next(reader)
    total = 0
    for row in reader:
        api_key_name = row[3]
        iotype = row[5]
        amount = int(row[7])
        try:
            price = float(row[6])
        except ValueError:
            # print("Некорректное значение пропущено")
            continue

        key = f"{api_key_name}_{iotype}"

        if key in d:
            d[key][0] += price
            d[key][1] += amount
        else:
            d.setdefault(key, [price, amount])

    for k, v in d.items():
        print(k, f"{v[0] * v[1]:.2f}CNY")
