from FPGrowth import fp_growth

# Set threshold of the algorithm
threshold = 0.30

# Get the transaction data as a list of lists
transaction_data = [['apples', 'berries'],['berries', 'coconut', 'donut'],['apples', 'coconut', 'donut', 'eggplant'],['apples', 'donut', 'eggplant'],
                    ['apples', 'berries', 'coconut'],['apples', 'berries', 'coconut', 'donut'],['apples'],['apples', 'berries', 'coconut'],
                    ['apples', 'berries', 'donut'],['berries', 'coconut', 'eggplant']]

# Run the FP-Growth algorithm with the set data and threshold
frequent_item_sets = fp_growth(transaction_data, threshold)

# View the frequent item sets returned by the algorithm
print(frequent_item_sets)


