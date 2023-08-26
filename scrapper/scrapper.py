# Import necessary libraries and modules
import time

import pandas as pd
import scrapper.constants as const
from genderize import Genderize
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions


# Define the Journal class that inherits from Chrome
class Journal(Chrome):
    def __init__(self, teardown=False, headless=True):
        # Constructor docstring
        """
        Constructor for the Journal class. It initializes the base class and sets the implicit wait time.

        :param teardown: Flag to determine whether to shut down the driver after usage.
        """

        # Initialize ChromeOptions and set to headless mode
        self.options = ChromeOptions()
        self.options.headless = headless

        # Set the teardown flag
        self.teardown = teardown
        # Initialize the super class (Chrome) with options
        super(Journal, self).__init__(options=self.options, use_subprocess=True,
                                      driver_executable_path="chromedriver.exe")
        # Set an implicit wait time for 5 seconds
        self.implicitly_wait(1)

    def login(self):
        # Open the login page using the constant path.
        self.open_link(const.LOGIN_PATH)

        # Accept cookies if prompted.
        self.accept_cookies()

        # Type in the name of the institution in the input box.
        self.find_element(By.CSS_SELECTOR, "input[class='form-control js--autocomplete-element']").send_keys(
            "Bar-Ilan University")

        # Create an action chain to simulate keypress.
        action = ActionChains(self)

        # Simulate pressing the 'Enter' key.
        action.send_keys(Keys.ENTER)

        # Click on the first autocomplete result for the institution.
        self.find_element(By.CSS_SELECTOR, "div[id='autoComplete_result_0']").click()

        # Click on another element - possibly a confirmation or next step button.
        self.find_element(By.CSS_SELECTOR, "div[class='ORRU02D-k-a']").click()

        time.sleep(2)

        self.find_element(By.CSS_SELECTOR, "#i0116").send_keys(
            const.EMAIL + Keys.ENTER)

        try:
            self.find_element(By.CSS_SELECTOR,
                              "#credentialList > div > div > div > div.table-cell.text-left.content").click()
        except:
            pass

        time.sleep(2)

        self.find_element(By.CSS_SELECTOR, "#i0118").send_keys(
            const.PASSWORD + Keys.ENTER)

        self.find_element(By.CSS_SELECTOR,
                          "#idDiv_SAOTCS_Proofs > div:nth-child(1) > div > div > div.table-cell.text-left.content").click()

        # Print a message to console notifying about a 60-second waiting period.
        print("Waiting 60 seconds for code verification")

        # Pause the execution for 60 seconds to allow the login process to complete.
        time.sleep(60)

    def land_first_page(self):
        """Navigates the driver to the base URL specified in constants."""
        self.get(const.BASE_URL)

    def accept_cookies(self):
        """Tries to locate and click the "Accept Cookies" button if present."""
        try:
            accept_cookies_button = self.find_element(By.CLASS_NAME, "css-1mgww4f")
            accept_cookies_button.click()
        except:
            print("No accept cookies button")

    def go_to_all_issues(self):
        """Navigates to the 'All Issues' section of the journal."""
        all_issues = self.find_element(By.CSS_SELECTOR, "a[data-id='all-issues']")
        all_issues.click()

    def get_decades(self):
        """
        Returns the decades available in the journal's 'All Issues' section.

        :return: List of WebElement representing the decades.
        """
        ul = self.find_element(By.CSS_SELECTOR, "ul[class='tab__nav rlist loi__tab__nav loi__list']")
        decades = ul.find_elements(By.TAG_NAME, "li")

        return decades

    def get_years(self):
        """
        Waits and fetches the years available for the selected decade in the journal's 'All Issues' section.

        :return: List of WebElement representing the years.
        """

        # Define a wait object with a timeout of 15 seconds
        wait = WebDriverWait(self, 1)

        # Wait for the presence of the outer div
        outer_div = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='tab__pane nested-tab active']")))

        # Now wait for the ul inside the outer div
        ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "div[class='tab__pane nested-tab active'] ul[class='tab__nav rlist loi__tab__nav loi__list']")))

        # Once ul is located, fetch all li elements
        years = ul.find_elements(By.TAG_NAME, "li")

        return years

    def get_issues(self, year):
        """
        Fetches the journal issues for a specific year.

        :param year: Year for which issues need to be fetched.
        :return: List of URLs of the issues for the specified year.
        """

        # Define a wait object with a timeout of 5 seconds
        wait = WebDriverWait(self, 1)

        # Wait for the presence of the outer div
        outer_div = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='tab__pane nested-tab active']")))

        # Wait for the specific div associated with the given year
        issues = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            f"div[class='tab__pane nested-tab active'] div[id$='{year}']")))

        # Extract the URLs (href) of all issues
        issues = [issue.get_attribute('href') for issue in
                  issues.find_elements(By.CSS_SELECTOR, "a[class='loi__issue__link']")]

        return issues

    def get_articles(self):
        """
        Attempts to get article links from the "Regular Articles" section.
        If not found, it continues to subsequent sections until an h4 tag is encountered.
        """

        # Fetch the "Regular Articles" section and collect subsequent sections until an h4 tag is found
        try:
            regular_articles_section = self.find_element(By.XPATH, "//section[h4[text()='Regular Articles']]")

            # List to store relevant sections
            sections_to_collect = [regular_articles_section]

            # Traverse through sibling sections and add them to the list until an h4 tag is found
            next_sibling = regular_articles_section
            while True:
                try:
                    next_sibling = next_sibling.find_element(By.XPATH, "./following-sibling::section[1]")

                    # Check if the sibling section contains an h4 tag and break if found
                    try:
                        if next_sibling.find_element(By.TAG_NAME, "h4"):
                            break
                    except NoSuchElementException as e:
                        pass
                    sections_to_collect.append(next_sibling)
                except NoSuchElementException as e:
                    break

            # Extract article links from the collected sections
            articles = [article.find_element(By.TAG_NAME, "a").get_attribute("href") for article in
                        sections_to_collect]

            return articles

        except Exception:
            # Print a message if no "Regular Articles" section is found on the page
            # print("No Regular Article on this page")
            pass

    def open_link(self, url):
        """Navigates the browser to the provided URL."""
        self.get(url)

    def get_details(self):

        # Initializing an empty dictionary to store the details
        details = {}

        # Extracting the name/title of the article
        article_name = self.find_element(By.CSS_SELECTOR, "h1[property='name']").text

        # Extracting the DOI (Digital Object Identifier) of the article
        doi = self.find_element(By.CSS_SELECTOR, "div[class='doi'] a").get_attribute("href")

        # Extracting the publication date and stripping the prefix
        publish_date = self.find_element(By.CSS_SELECTOR, "div[class='meta-panel__onlineDate']").text.split(
            "First published online ")[
            1]

        # Extracting all authors
        authors = self.find_elements(By.CSS_SELECTOR, "span[property='author']")

        # Calculating the total number of authors
        number_of_authors = len(authors)

        # Extracting the name of the first author
        first_author_name = authors[0].find_element(By.CSS_SELECTOR, "span[property='givenName']").text + " " + authors[
            0].find_element(By.CSS_SELECTOR, "span[property='familyName']").text

        # Predicting the gender of the first author using their name
        first_author_gender = Genderize().get1(first_author_name.split()[0])

        # Extracting affiliations
        affiliations = self.find_elements(By.CSS_SELECTOR, "div[property='affiliation']")

        # Extracting all images present in the article
        images = self.find_elements(By.CSS_SELECTOR, "figure[class='graphic']")

        # Taking the first half of all the images
        img_half_length = int(len(images) / 2)
        images = images[:img_half_length]

        # Extracting all tables present in the article
        tables = self.find_elements(By.CSS_SELECTOR, "figure[class='table']")

        # Taking the first half of all the tables
        tab_half_length = int(len(tables) / 2)
        tables = tables[:tab_half_length]

        # Populating the 'details' dictionary
        details["Paper title"] = article_name
        details["Paper DOI"] = doi
        details["Publication Date"] = publish_date
        details["Number of authors"] = number_of_authors
        details["Name of the first author"] = first_author_name
        details["Gender of the first author"] = first_author_gender["gender"]
        details["First author gender probability"] = first_author_gender["probability"]

        # Extracting affiliation of the first author using JavaScript execution
        first_affiliation = affiliations[0].find_element(By.CSS_SELECTOR, "span[property='name']")
        details["Affiliation of the first author"] = self.execute_script("return arguments[0].textContent",
                                                                         first_affiliation)

        # Checking if there's more than one author and then extracting details of the last author
        if number_of_authors > 1:
            last_author_name = authors[-1].find_element(By.CSS_SELECTOR, "span[property='givenName']").text + " " + \
                               authors[-1].find_element(By.CSS_SELECTOR, "span[property='familyName']").text
            last_author_gender = Genderize().get1(last_author_name.split()[0])
            details["Name of the last author"] = last_author_name
            details["Gender of the last author"] = last_author_gender["gender"]
            details["Last author gender probability"] = last_author_gender["probability"]

            # Extracting affiliation of the last author using JavaScript execution
            last_affiliation = affiliations[-1].find_element(By.CSS_SELECTOR, "span[property='name']")
            details["Affiliation of the last author"] = self.execute_script("return arguments[0].textContent",
                                                                            last_affiliation)

        # Storing the number of images
        details["Number of Images"] = len(images)

        # Extracting caption and link for each image in the first half
        for i in range(img_half_length):
            details[f"Image {i + 1} caption"] = images[i].find_element(By.CSS_SELECTOR, "figcaption").text
            details[f"Image {i + 1} Link"] = images[i].find_element(By.CSS_SELECTOR, "img").get_attribute("src")

        # Storing the number of tables
        details["Number of Tables"] = len(tables)

        # Extracting caption for each table in the first half
        for i in range(tab_half_length):
            details[f"Table {i + 1} caption"] = tables[i].find_element(By.CSS_SELECTOR, "figcaption").text

        # Printing the 'details' dictionary
        print(details)

        # Returning the 'details' dictionary
        return details

    def create_dataframe(self):
        # Define the column names in a list
        columns = [
            "Paper title",
            "Paper DOI",
            "Publication Date",
            "Number of authors",
            "Name of the first author",
            "Name of the last author",
            "Gender of the first author",
            "Gender of the last author",
            "First author gender probability",
            "Last author gender probability",
            "Affiliation of the first author",
            "Affiliation of the last author",
            "Number of Images"
        ]

        # Add image caption and link columns
        for i in range(1, 11):
            columns.append(f"Image {i} caption")

        for i in range(1, 11):
            columns.append(f"Image {i} Link")

        columns.append("Number of Tables")

        # Add table caption columns
        for i in range(1, 11):
            columns.append(f"Table {i} caption")

        # Create an empty DataFrame with the columns
        df = pd.DataFrame(columns=columns)

        return df

    def populate_df(self, df: pd.DataFrame, data: dict) -> pd.DataFrame:
        """
        Populates the given DataFrame with data from the provided dictionary.

        :param df: The pandas DataFrame to which data needs to be appended.
        :param data: Dictionary containing the data to be appended.

        :return: The updated DataFrame with appended data.
        """

        # Using the 'loc' accessor to add a new row to the end of the DataFrame
        df.loc[len(df)] = data

        return df
