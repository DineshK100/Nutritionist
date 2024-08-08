from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
import time

url = "https://dining.ncsu.edu/locations/"


def scraper(meal):
    driver_main = webdriver.Chrome()
    driver_detail = webdriver.Chrome()
    driver_main.get(url)

    diningHallsList = [
        "Talley – Los Lobos Global Kitchen",
        "Talley – Tuffy’s Diner",
        "Clark",
        "Case",
        "University Towers",
        "One Earth",
    ]

    try:

        def get_location_tiles(driver):
            return WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "location-tile--open")
                )
            )

        location_tiles = get_location_tiles(driver_main)

        for tile in location_tiles:
            try:
                name_element = tile.find_element(
                    By.CLASS_NAME, "location-tile__bar"
                ).find_element(By.TAG_NAME, "h4")

                name = name_element.text

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

                    menu_tiles = WebDriverWait(driver_detail, 20).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "dining-menu-category")
                        )
                    )

                    if not menu_tiles:
                        print("No menu items found.")
                    else:
                        for menu in menu_tiles:
                            menu_items = menu.find_elements(By.TAG_NAME, "li")
                            print(f"Scraping {meal} for {name}")
                            for item in menu_items:
                                item_name = item.find_element(By.TAG_NAME, "a").text
                                print(f"Found item: {item_name}")

                                item.find_element(By.TAG_NAME, "a").click()

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

                                for row in nutrient_rows:
                                    nutrient_name = row.find_element(
                                        By.TAG_NAME, "strong"
                                    ).text
                                    nutrient_value = row.find_element(
                                        By.CLASS_NAME, "menu-nutrition-row-value"
                                    ).text
                                    print(f"{nutrient_name}: {nutrient_value}")

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


schedule.every().day.at("08:00").do(scrapeBreakfast)
schedule.every().day.at("13:00").do(scrapeLunch)
schedule.every().day.at("16:00").do(scrapeDinner)

while True:
    schedule.run_pending()
    time.sleep(60)
