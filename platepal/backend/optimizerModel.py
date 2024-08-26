import tensorflow as tf
import numpy as np
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.engine import data_adapter
from .recommender import initialRecommendations
import tensorflow.python.keras as tf_keras
from keras import __version__
from .connectDb import connectToMongo


# Handling the issue with distributed datasets
def _is_distributed_dataset(ds):
    return isinstance(ds, data_adapter.input_lib.DistributedDatasetSpec)


data_adapter._is_distributed_dataset = _is_distributed_dataset

# Manual fix on bug found through StackOverFlow
tf_keras.__version__ = __version__


def load_or_initialize_model():

    # Load the model or create a new one
    try:
        model = tf.keras.models.load_model("/userFeedback.keras")
    except:
        model = Sequential()
        model.add(Dense(64, activation="relu"))
        model.add(Dense(32, activation="relu"))
        model.add(Dense(16, activation="relu"))
        model.add(Dense(1, activation="sigmoid"))
    return model


# Function to handle optimization
def optimize(location):
    model = load_or_initialize_model()
    # Function to generate initial recommendations
    foodItemVector, similarities, itemList, recommended_list = initialRecommendations(
        location
    )

    training_data = np.hstack((foodItemVector, similarities.reshape(-1, 1)))
    predicted_scores = model.predict(training_data).flatten()
    new_recs = np.argsort(predicted_scores)[::-1][:10]
    recommended_items = [itemList[i] for i in new_recs]
    print("Recommended items:", [item["name"] for item in recommended_items])


# Function to handle model training
def train(location):
    model = load_or_initialize_model()
    # Function to generate initial recommendations
    foodItemVector, similarities, itemList, recommended_list = initialRecommendations(
        location
    )
    db, collection = connectToMongo()
    collection = db["userFeedback"]
    changeStream = collection.watch()

    userFeedback = {}
    for change in changeStream:
        if change["operationType"] == "insert":
            print("New feedback detected. Retraining the model...")
            new_feedback = change["fullDocument"]
            item_name = new_feedback["name"]
            rating = new_feedback["rating"]
            userFeedback[item_name] = rating

            feedback_labels = []
            training_data = []

            for item in itemList:
                if item["name"] in userFeedback:
                    rating = userFeedback[item["name"]]
                    feedback_labels.append(rating)
                    item_index = itemList.index(item)
                    combined_vector = np.hstack(
                        (foodItemVector[item_index], similarities[item_index])
                    )
                    training_data.append(combined_vector)

            training_data = np.array(training_data)
            feedback_labels = np.array(feedback_labels)

            model.compile(
                optimizer="adam",
                loss="mean_squared_error",
            )

            model.fit(training_data, feedback_labels, epochs=10, batch_size=8)
            model.save("userFeedback.keras", compile=True)
