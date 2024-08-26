from pymongo import MongoClient
import certifi


def connectToMongo():
    with open("auth.txt", "r") as f:
        connection_string = f.read

    try:
        client = MongoClient(
            connection_string,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
        )
    except Exception as e:
        print("Error:", e)

    db = client["diningMenus"]
    collection = db["menus"]

    return db, collection
