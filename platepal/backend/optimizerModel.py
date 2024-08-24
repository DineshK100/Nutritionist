import tensorflow as tf
import numpy as np
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.engine import data_adapter
from recommender import initialRecommendations
import tensorflow.python.keras as tf_keras
from keras import __version__
from connectDb import connectToMongo


# Manual fix on bug found through StackOverFlow
tf_keras.__version__ = __version__

foodItemVector, similarities, itemList, recommended_list = initialRecommendations()


# Manually changed this as per a few StackOverflow similar issues with distributed data set specs
def _is_distributed_dataset(ds):
    return isinstance(ds, data_adapter.input_lib.DistributedDatasetSpec)


data_adapter._is_distributed_dataset = _is_distributed_dataset


db, collection = connectToMongo()
collection = db["userFeedback"]

changeStream = collection.watch()


try:
    model = tf.keras.models.load_model("userFeedback.keras")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="mean_squared_error",
    )

except:
    # activation functions
    model = Sequential()
    model.add(Dense(64, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))

    adam = tf.keras.optimizers.Adam(learning_rate=0.001)

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
    )

userFeedback = {
    "Combo - Fries/Drink": 3,
    "Combo - Tots/Drink": 1,
    "Bacon Cheeseburger": 2,
    "Tuffy Tots": 5,
    "Three Grilled Cheese Sandwich": 4,
}

# Temporary simulated user feedback
feedback_labels = []

training_data = []

for change in changeStream:
    if change["operationType"] == "insert":
        # New feedback detected
        print("New feedback detected. Retraining the model...")

        # Retrieve and prepare the new feedback data
        new_feedback = change["fullDocument"]
        item_name = new_feedback["name"]
        rating = new_feedback["rating"]

        # Update userFeedback dictionary
        userFeedback[item_name] = rating

        # Prepare training data from user feedback
        feedback_labels = []
        training_data = []

        for item in itemList:
            item_name = item["name"]
            if item_name in userFeedback:
                rating = userFeedback[item_name]
                feedback_labels.append(rating)
                item_index = itemList.index(item)

                combined_vector = np.hstack(
                    (foodItemVector[item_index], similarities[item_index])
                )
                training_data.append(combined_vector)

        training_data = np.array(training_data)
        feedback_labels = np.array(feedback_labels)

        # Continue training the model with the new feedback
        model.fit(training_data, feedback_labels, epochs=10, batch_size=8)

        # Save the model after retraining
        model.save("userFeedback.keras")

        # Generate new recommendations
        predicted_scores = model.predict(training_data).flatten()
        new_recs = np.argsort(predicted_scores)[::-1][:10]
        recommended_items = [itemList[i] for i in new_recs]

        print("Recommended items:", [item["name"] for item in recommended_items])
