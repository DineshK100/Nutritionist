import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from connectDb import connectToMongo


def initialRecommendations():
    db, collection = connectToMongo()

    data = pd.DataFrame(list(collection.find()))

    userPreferences = np.array([500, 50, 1000])  # cals, protein, sodium

    foodItemVector = []
    itemList = []

    for menu in data["items"]:
        for _id in menu:
            item = db.items.find_one({"_id": _id})

            if (
                item
                # Below statement is done to make 100% sure that only the user preferences are being recommended
                and float(item["nutrients"][len(item["nutrients"]) - 1]["value"])
                <= 1500
            ):
                vectorElement = [
                    float(item["nutrients"][1]["value"]),
                    float(item["nutrients"][2]["value"]),
                    float(item["nutrients"][len(item["nutrients"]) - 1]["value"]),
                ]
                foodItemVector.append(vectorElement)
                itemList.append(item)

    # Converted userPreferences array to 2d array to compare as "vectors"
    similarities = cosine_similarity(foodItemVector, [userPreferences])

    # since similiarities is an np array I made use of np functions
    # using argsort because it returns the indices of the elements
    # reversing the list because argsort inately goes smallest to largest
    # Get indices of top 10 similarities
    recommended_indices = np.argsort(similarities.flatten())[::-1][:10]

    recommended_list = [itemList[i] for i in recommended_indices]

    print([item["name"] for item in recommended_list])

    return (foodItemVector, similarities, itemList, recommended_list)
