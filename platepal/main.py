from backend.recommender import initialRecommendations
from backend.optimizerModel import train, optimize
import schedule
import time


def main():
    # Get what they want for breakfast:
    optimize("Talley – Tuffy’s Diner")

    # # Get what they want for lunch:
    # optimize("Clark")

    # # Get what they want for dinner:
    # optimize("Fountain")

    # Get the user feedback somehow later down the line

    # Now train the model
    # train()


main()

while True:
    schedule.run_pending()
    time.sleep(10)
