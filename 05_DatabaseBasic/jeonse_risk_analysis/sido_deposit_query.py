from queries import fetch_sido_deposit_amount

df = fetch_sido_deposit_amount()
print(df.to_string())
