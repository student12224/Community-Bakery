from stock import Stock

stock1 = Stock()
stock2 = Stock()

print("Before modification:")
print("Stock 1:", stock1.quantities["flour"])
print("Stock 2:", stock2.quantities["flour"])

stock1.quantities["flour"] = 500

print("\nAfter modification:")
print("Stock 1:", stock1.quantities["flour"])
print("Stock 2:", stock2.quantities["flour"])

assert stock1.quantities["flour"] == 500
assert stock2.quantities["flour"] == 1000

print("\nSUCCESS: Stock objects are independent.")
stock = Stock()

remaining = {
    "flour": 3,
    "butter": 3,
    "fruit": 3
}

print(stock.discarded(remaining))