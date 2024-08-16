import tensorflow as tf
import numpy as np
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.engine import data_adapter
import recommender
from recommender import initialRecommendations

foodItemVector, similarities, itemList, recommended_list = initialRecommendations()


# Manually changed this as per a few StackOverflow similar issues with distributed data set specs
def _is_distributed_dataset(ds):
    return isinstance(ds, data_adapter.input_lib.DistributedDatasetSpec)


data_adapter._is_distributed_dataset = _is_distributed_dataset

# Watching videos understaind neural networks

# inputs -> hidden layers -> outputs

# activation functions
model = Sequential()
model.add(Dense(32, activation="relu"))
model.add(Dense(16, activation="relu"))
model.add(Dense(1, activation="sigmoid"))

adam = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
)

# Temporary simulated user feedback
feedback_labels = np.random.randint(0, 2, size=(len(similarities)))

training_data = np.hstack((foodItemVector, similarities.reshape(-1, 1)))

model.fit(training_data, feedback_labels, epochs=10, batch_size=8)

predicted_scores = model.predict(training_data).flatten()

new_recs = np.argsort(predicted_scores)[::-1][:10]

recommended_items = [itemList[i] for i in new_recs]

print("Recommended items:", [item["name"] for item in recommended_list])
