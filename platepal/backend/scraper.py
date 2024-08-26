from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
import time
import datetime
from pymongo import MongoClient
import certifi

url = "https://dining.ncsu.edu/locations/"

# look into cacheing the stuff to avoid repetition
# Also since the menus are available at the beginning of the day, scrape at once
# Also scrape the allergens
with open("auth.txt", "r") as f:
    connection_string = f.read()

try:
    client = MongoClient(
        connection_string, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True
    )
except Exception as e:
    print("Error:", e)


db = client["diningMenus"]


# for the diningHalls cluster this will be the format:
# name, menus (an array of menus representing breakfast, lunch, and dinner)
def scraper(meal):
    driver_main = webdriver.Chrome()
    driver_detail = webdriver.Chrome()
    driver_main.get(url)

    # will add more as they open
    diningHallsList = [
        "Talley – Tuffy’s Diner",
        "Fountain",
        "Clark",
        "Case",
        "University Towers",
        "One Earth",
        "Talley – Los Lobos Global Kitchen",
        "Talley – 1887 Bistro",
    ]

    try:

        # Waits for the website to load in all the restaurant info and breaks them into tiles (only open ones)
        def get_location_tiles(driver):
            return WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "location-tile--open")
                )
            )

        location_tiles = get_location_tiles(driver_main)

        for tile in location_tiles:

            try:

                # name of the restaurant
                name_element = tile.find_element(
                    By.CLASS_NAME, "location-tile__bar"
                ).find_element(By.TAG_NAME, "h4")

                name = name_element.text

                # Check to see if the element is already there before inserting

                diningHallId = db.diningHalls.insert_one(
                    {"name": name, "menus": []}
                ).inserted_id

                if name in diningHallsList:

                    print(f"Found dining hall: {name}")

                    link = tile.find_element(By.TAG_NAME, "a")

                    dining_hall_url = link.get_attribute("href")

                    driver_detail.get(dining_hall_url)

                    # Wait for the menu page to load
                    WebDriverWait(driver_detail, 20).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "dining-menu-category")
                        )
                    )
                    # the previous code waits for it to load and then this code adds it to a variable
                    menu_tiles = WebDriverWait(driver_detail, 20).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "dining-menu-category")
                        )
                    )

                    if not menu_tiles:
                        print("No menu items found.")
                    else:

                        menu_id = db.menus.insert_one(
                            {
                                "diningHall_id": diningHallId,
                                "mealType": meal,
                                "date": datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "items": [],
                            }
                        ).inserted_id

                        db.diningHalls.update_one(
                            {"_id": diningHallId}, {"$push": {"menus": menu_id}}
                        )

                        for menu in menu_tiles:

                            menu_items = menu.find_elements(By.TAG_NAME, "li")
                            print(f"Scraping {meal} for {name}")

                            for item in menu_items:

                                item_name = item.find_element(By.TAG_NAME, "a").text
                                print(f"Found item: {item_name}")

                                # clicks into the nutrient popup
                                item.find_element(By.TAG_NAME, "a").click()

                                # waits for the loading icon in the popup to go away to start scraping
                                WebDriverWait(driver_detail, 20).until_not(
                                    EC.presence_of_element_located(
                                        (By.CLASS_NAME, "fa-refresh")
                                    )
                                )

                                nutrients_container = WebDriverWait(
                                    driver_detail, 20
                                ).until(
                                    EC.presence_of_element_located(
                                        (
                                            By.CLASS_NAME,
                                            "menu-dining-menu-modal-nutrition",
                                        )
                                    )
                                )

                                nutrient_rows = nutrients_container.find_elements(
                                    By.CLASS_NAME, "menu-nutrition-row"
                                )
                                nutrients = []
                                allergens = []
                                for row in nutrient_rows:

                                    nutrient_name = row.find_element(
                                        By.TAG_NAME, "strong"
                                    ).text

                                    nutrient_value = row.find_element(
                                        By.CLASS_NAME, "menu-nutrition-row-value"
                                    ).text

                                    print(f"{nutrient_name}: {nutrient_value}")
                                    # dining-menu-allergen-contains dining-menu-allergen-contains-traits
                                    nutrients.append(
                                        {
                                            "nutrient": nutrient_name,
                                            "value": nutrient_value,
                                        }
                                    )

                                    # allergens_list = row.find_element(
                                    #     By.CLASS_NAME,
                                    #     "dining-menu-allergen-contains dining-menu-allergen-contains-traits",
                                    # ).text

                                    # allergens_list.replace("and", "")

                                    # allergens = allergens_list.split(", ")
                                    # print(allergens)

                                menu_item_id = db.items.insert_one(
                                    {
                                        "name": item_name,
                                        "nutrients": nutrients,
                                        "allergens": allergens,
                                    }
                                ).inserted_id

                                db.menus.update_one(
                                    {"_id": menu_id},
                                    {"$push": {"items": menu_item_id}},
                                )

                                # closes the popup once the items have been scraped and the close button shows up
                                close_button = WebDriverWait(driver_detail, 20).until(
                                    EC.element_to_be_clickable(
                                        (By.ID, "dining-menu-modal-close")
                                    )
                                )

                                close_button.click()

                    driver_detail.back()

            except Exception as e:
                print(f"Error processing dining hall {name}: {e}")

    finally:
        driver_main.quit()
        driver_detail.quit()


def scrapeBreakfast():
    scraper("Breakfast")


def scrapeLunch():
    scraper("Lunch")


def scrapeDinner():
    scraper("Dinner")


schedule.every().day.at("18:04").do(scrapeBreakfast)
schedule.every().day.at("13:00").do(scrapeLunch)
schedule.every().day.at("16:00").do(scrapeDinner)

while True:
    schedule.run_pending()
    time.sleep(10)
