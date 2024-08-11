from pulp import *
from pymongo import MongoClient
import pandas as pd
import certifi

calorieConstraint = 3000
sodiumConstraint = 2000  # in mg
proteinConstraint = 180  # in g
carbohydrateConstraint = 150  # in g

connection_string = "mongodb+srv://dineshkarnati100:agre2u9tQ7v2V1XL@cluster0.nq5d7.mongodb.net/?tls=true"

try:
    client = MongoClient(
        connection_string, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True
    )
except Exception as e:
    print("Error:", e)

db = client["diningMenus"]
collection = db["menus"]

data = pd.DataFrame(list(collection.find()))

# Store the menu_items dicts in foodVariables
foodVariables = []

for menu in data["items"]:
    for _id in menu:
        item = db.items.find_one({"_id": _id})
        foodVariables.append(item)

MY_PROBLEM = LpProblem("platepal", LpMaximize)

food_item_vars = {
    item["name"]: LpVariable(item["name"], lowBound=0, cat="Binary")
    for item in foodVariables
}

MY_PROBLEM += (
    lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][2]["value"])
            for item in foodVariables
        ]
    )
    + lpSum(
        [
            food_item_vars[item["name"]]
            * float(item["nutrients"][len(item["nutrients"]) - 1]["value"])
            for item in foodVariables
        ]
    )
    + lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][1]["value"])
            for item in foodVariables
        ]
    )
    + lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][3]["value"])
            for item in foodVariables
        ]
    )
)

MY_PROBLEM += (
    lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][2]["value"])
            for item in foodVariables
        ]
    )
    <= proteinConstraint
)
MY_PROBLEM += (
    lpSum(
        [
            food_item_vars[item["name"]]
            * float(item["nutrients"][len(item["nutrients"]) - 1]["value"])
            for item in foodVariables
        ]
    )
    <= sodiumConstraint
)
MY_PROBLEM += (
    lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][1]["value"])
            for item in foodVariables
        ]
    )
    <= calorieConstraint
)
MY_PROBLEM += (
    lpSum(
        [
            food_item_vars[item["name"]] * float(item["nutrients"][3]["value"])
            for item in foodVariables
        ]
    )
    <= carbohydrateConstraint
)

solution = MY_PROBLEM.solve()

print(f"Solution Status: {LpStatus[solution]}")

for item in MY_PROBLEM.variables():
    if item.varValue == 1:
        print(item.name)
