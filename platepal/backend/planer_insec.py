from pulp import *
import pandas as pd
from platepal.backend.connectDb_insec import connectToMongo

calorieConstraint = 3000  # in cals
sodiumConstraint = 2000  # in mg
proteinConstraint = 180  # in g
carbohydrateConstraint = 150  # in g


def optimalMenu(data):

    # db, collection = connectToMongo()
    # data = pd.DataFrame(list(collection.find()))

    # Store the menu_items dicts in foodVariables
    foodVariables = []

    for item in data["items"]:
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
