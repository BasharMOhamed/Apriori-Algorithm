import pandas as pd
from itertools import permutations


# VERTICAL FORMAT (TEST)
data_path = r"Vertical_Format.xlsx"
# HORIZONTAL FORMAT (TEST)
#data_path = r"Horizontal_Format.xlsx"
data = pd.read_excel(data_path)

if data.columns[0] == "itemset":
    print(f"Data Before Convert:\n {data}")
    converted_data = {'TID': [], 'items': []}

    for i, row in data.iterrows():
        itemset = row['itemset']
        TID_set = str(row['TID_set']).split(',') 

        # INSERT ROW WITH TID AND ITEM
        for TID in TID_set:
            converted_data['TID'].append(TID.strip())
            converted_data['items'].append(itemset)

    converted_df = pd.DataFrame(converted_data)

    # JOIN ITEMS WITH THE SAME TID
    horizontal_df = converted_df.groupby('TID')['items'].apply(','.join).reset_index()

    # Print the horizontal DataFrame
    print(f"Data After Convert:\n {horizontal_df}")
    data = horizontal_df
else:
    print(f"Horizontal Data:\n {data}")

# HAVE ALL TRANSACTIONS
Transactions = []

# HAVE ALL FREQUENT ITEMSETS
Frequent = []

# HAVE ALL ASSOCIATION RULES
Association_rules = []
C1 = []
Min_support = int(input("Enter The Minimum Support (Number n): "))
Min_Confidence = float(input("Enter The Minimum Confidence (Percent %): "))
############################################################


def calculate_support(itemset, frequent_itemsets):
    count = 0
    for transaction in frequent_itemsets:
        if set(itemset).issubset(transaction):
            count += 1
    return count


def calculate_confidence(antecedent, rule, freq_itemset):
    antecedent_set = set(antecedent)
    rule_set = set(rule)
    support_rule = calculate_support(rule_set, freq_itemset)
    support_antecedent = calculate_support(antecedent_set, freq_itemset)
    confidence = support_rule / support_antecedent if support_antecedent > 0 else 0

    return confidence * 100


def calculate_prob(rule, total_transactions, freq_itmset):
    return calculate_support(rule, freq_itmset) / total_transactions


def calculate_lift(antecedent, consequent, frequent_itmset):
    rule_prob = calculate_prob(set(antecedent + consequent), len(data["items"]), frequent_itmset)
    antecedent_prob = calculate_prob(set(antecedent), len(data["items"]), frequent_itmset)
    consequent_prob = calculate_prob(set(consequent), len(data["items"]), frequent_itmset)
    denominator = antecedent_prob * consequent_prob
    return round(rule_prob / denominator, 2)


# STORE TRANSACTIONS
for i in range(0, len(data["items"])):
    Transactions.append(tuple(sorted(set(data["items"][i].split(',')))))
    C1.extend(sorted(set(data["items"][i].split(','))))
print(f"Transactions: {Transactions}")
C1 = sorted(set(C1))

C1 = {key: calculate_support(key,data["items"]) for key in C1}
print(f"C1: {C1}")

# FILTER THE CANDIDATES TO GET THE FREQUENT
L1 = {key: value for key, value in C1.items() if (value >= Min_support)}
print(f"L1: {L1}")

LK = L1
k = 2
while 1:
    # MAKING A CANDIDATE WITH LENGTH OF K (JOIN)
    CK = {tuple(sorted(set(item1).union(set(item2)))): calculate_support(tuple(sorted(set(item1).union(set(item2)))), data["items"])
          for item1 in LK for item2 in LK
          if(len(set(item1).union(set(item2))) == k and sorted(set(item1[:-1])) == sorted(set(item2[:-1])))}


    # FILTER THE DICTIONARY TO GET THE FREQUENT ITEMSET (ITS SUPPORT >= MINIMUM SUPPORT)
    LK = {key: value for key, value in CK.items() if value >= Min_support}

    if len(LK) == 0:
        break

    print(f"C{k} : {CK}")
    print(f"L{k}: {LK}")
    Frequent.append(LK)
    k += 1
print(Frequent)
# MAKING ALL ASSOCIATION RULES
for itemset in Frequent:
    for element in itemset:
        for i in range(1, len(element)):
            for subset in permutations(element, i):
                rule = (tuple(sorted(subset)), tuple(sorted(item for item in element if item not in subset)))
                Association_rules.append(rule)

# REMOVE DUPLICATED RULES
unique_rules = set(sorted(Association_rules))

# MAKING DICTIONARY FOR ALL ASSOCIATION RULES AND HAS THE CONFIDENCE FOR EACH ONE
confdic = {f"{key[0]} --> {key[1]}": calculate_confidence(key[0], key[0]+key[1], data["items"]) for key in unique_rules}

# FILTER THE ASSOCIATION RULES TO GET THE STRONG RULES (ITS CONFIDENCE > MINIMUM CONFIDENCE)
strong = {key: value for key, value in confdic.items() if(value >= Min_Confidence)}

print("---------------------------------------------------------------------------------------------")
print("ALL ASSOCIATION RULES OF FREQUENT ITEMSETS WITH THIER CONFIDENCE:")
for key, value in confdic.items():
    print(f"{key}: {value}")

print("---------------------------------------------------------------------------------------------")
if strong == {}:
    print("NO STRONG RULES FOUND!")
else:
    print("ALL STRONG RULES:")
    for key, value in strong.items():
        print(f"{key}: {value}")


lift_dic = {f"{key[0]} --> {key[1]}": calculate_lift(key[0], key[1], data["items"]) for key in unique_rules}
print("---------------------------------------------------------------------------------------------")
print("ALL ASSOCIATION RULES WITH LIFT")
for key, value in lift_dic.items():
    print(f"{key}: {value}")

negative_correlated = {key: value for key, value in lift_dic.items() if(value < 1)}
print("---------------------------------------------------------------------------------------------")
if negative_correlated == {}:
    print("NO NEGATIVE CORRELATION FOUND!")
else:
    print("DEPENDENT RULES WITH NEGATIVE CORRELATION")
    for key, value in negative_correlated.items():
        print(f"{key}: {value}")

positive_correlated = {key: value for key, value in lift_dic.items() if(value > 1)}
print("---------------------------------------------------------------------------------------------")
if positive_correlated == {}:
    print("NO POSITIVE CORRELATION FOUND!")
else:
    print("DEPENDENT RULES WITH POSITIVE CORRELATION")
    for key, value in positive_correlated.items():
        print(f"{key}: {value}")


Independent = {key: value for key, value in lift_dic.items() if(value == 1)}
print("---------------------------------------------------------------------------------------------")
if Independent == {}:
    print("NO INDEPENDENT CORRELATION FOUND!")
else:
    print("INDEPENDENT RULES")
    for key, value in Independent.items():
        print(f"{key}: {value}")