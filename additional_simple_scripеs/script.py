import csv

d = {}
res = 0
total_requests = 0
total_tokens = 0

with open("amount-2026-5.csv", "r") as f:
    reader = csv.reader(f)
    headers = next(reader)
    total = 0
    for row in reader:
        api_key_name = row[3]
        amount = int(row[7]) if row[7] else 0

        if row[5] == "request_count":
            total_requests += amount
            continue

        try:
            price = float(row[6])
        except ValueError:
            print("Некорректное значение пропущено")
            continue

        total_tokens += amount
        d[api_key_name] = d.get(api_key_name, 0) + price * amount

    for k, v in d.items():
        # print(k, f"cost:{round(v, 2)}")
        res += v

    print()
    print(f"total:{round(res, 2)}")
    print(f"total_requests:{total_requests}")
    print(f"total_tokens:{total_tokens}")
    print()
    for k, v in d.items():
        percent = (v / res) * 100 if res != 0 else 0
        print(f"{k}  cost: {v:.6f}  ({percent:.2f}%)")
