from pymongo import MongoClient
import certifi


def connectToMongo():
    connection_string = "mongodb+srv://dineshkarnati100:agre2u9tQ7v2V1XL@cluster0.nq5d7.mongodb.net/?tls=true"

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
