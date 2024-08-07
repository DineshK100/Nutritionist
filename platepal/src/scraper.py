from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://dining.ncsu.edu/locations/"

driver = webdriver.Chrome()

driver.get(url)

diningHallsList = [
    "Talley – Los Lobos Global Kitchen",
    "Fountain",
    "Clark",
    "Case",
    "University Towers",
    "One Earth",
]

try:

    def get_location_tiles():
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "location-tile--open"))
        )

    location_tiles = get_location_tiles()

    for tile in location_tiles:
        name_element = tile.find_element(
            By.CLASS_NAME, "location-tile__bar"
        ).find_element(By.TAG_NAME, "h4")

        name = name_element.text

        if name in diningHallsList:
            print(f"Found dining hall: {name}")
            link = tile.find_element(By.TAG_NAME, "a")
            link.click()

            # Wait for the menu page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dining-menu-category"))
            )

            menu_tiles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "dining-menu-category")
                )
            )

            if not menu_tiles:
                print("No menu items found.")
            else:
                for menu in menu_tiles:
                    menu_items = menu.find_elements(By.TAG_NAME, "li")

                    for item in menu_items:
                        item_name = item.find_element(By.TAG_NAME, "a").text
                        print(f"Found item: {item_name}")

                        item.find_element(By.TAG_NAME, "a").click()

                        WebDriverWait(driver, 20).until_not(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "fa-refresh")
                            )
                        )

                        nutrients_container = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "menu-dining-menu-modal-nutrition")
                            )
                        )

                        nutrient_rows = nutrients_container.find_elements(
                            By.CLASS_NAME, "menu-nutrition-row"
                        )

                        print(f"Found {len(nutrient_rows)} nutrient rows.")

                        for row in nutrient_rows:
                            nutrient_name = row.find_element(By.TAG_NAME, "strong").text
                            nutrient_value = row.find_element(
                                By.CLASS_NAME, "menu-nutrition-row-value"
                            ).text
                            print(f"{nutrient_name}: {nutrient_value}")

                        close_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "modal-close"))
                        )
                        close_button.click()

            driver.back()

            location_tiles = get_location_tiles()

finally:
    driver.quit()
