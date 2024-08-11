from pulp import *
from pymongo import MongoClient
import pandas as pd
import certifi

calorieConstraint = 3000
sodiumConstraint = 1000  # in mg
proteinConstraint = 180  # in g

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


# I'm literally going to store the menu_items dicts in here
# calroies, sodium, protei
foodVariables = []

# x1 + x2 + x3 + x4

items = data["items"]
for item_id in items:
    item = db.items.find_one({"_id": item_id})
    foodVariables.append(item)

print(foodVariables)

MY_PROBLEM = LpProblem("platepal", LpMaximize)

MY_PROBLEM += (
    lpSum(foodVariables["nutrients"][2])
    + lpSum(foodVariables["nutrients"][8])
    + lpSum(foodVariables["nutrients"][1])
)

MY_PROBLEM += (
    lpSum([food["nutrients"][2] for food in foodVariables]) <= proteinConstraint
)
MY_PROBLEM += (
    lpSum([food["nutrients"][8] for food in foodVariables]) <= sodiumConstraint
)
MY_PROBLEM += (
    lpSum([food["nutrients"][1] for food in foodVariables]) <= calorieConstraint
)

# The variables should be teh food items
# Goal is to optimize the number of food items so the optimization problem is to max them

solution = MY_PROBLEM.solve()

print(
    str(pulp.LpStatus[solution])
    + " ; max value = "
    + str(pulp.value(MY_PROBLEM.objective))
)
