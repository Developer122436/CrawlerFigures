# Import the necessary constants and classes
import os
import re

from scrapper import file_handling
from scrapper.constants import OUT_PATH, IMAGE_PATH
from scrapper.scrapper import Journal

# Start the web scraper for the journal
bot = Journal(headless=False)
# Create an empty dataframe to store the scraped data
dataframe = bot.create_dataframe()

# Initiate logging process
bot.login()

# Navigate to the initial page of the journal
bot.land_first_page()

# Accept any cookies if presented on the website
bot.accept_cookies()

# Navigate to the section that displays all issues of the journal
bot.go_to_all_issues()

# Fetch the available decades from the "All Issues" section
decades = bot.get_decades()

# Iterate over each decade
for decade_index in range(len(decades)):
    # Click on the specific decade to see its years
    decades[decade_index].click()

    # Fetch the list of years available in the clicked decade
    years = bot.get_years()

    # Iterate over each year in the clicked decade
    for year_index in range(len(years)):
        # Re-fetch the years each time to avoid stale references
        year = years[year_index]

        # Store year
        year_text = year.text

        # Click on the specific year (only clicking on "2018" is currently commented out)
        year.click()

        # Fetch the journal issues for the clicked year
        issues = bot.get_issues(year.text)

        # Iterate over each issue in the clicked year
        for issue_index in reversed(range(len(issues))):
            # Open a new window/tab
            bot.execute_script("window.open('');")

            # Switch to the new window
            bot.switch_to.window(bot.window_handles[-1])

            # Open the link for the specific issue using the second bot instance
            bot.open_link(issues[issue_index])

            # Fetch all articles available in the clicked issue
            articles = bot.get_articles()

            # If there are any articles, iterate over each one
            if articles:
                for article_index in range(len(articles)):
                    # Open the link for the specific article using the second bot instance
                    bot.open_link(articles[article_index])

                    # Extract details of the article
                    details = bot.get_details()

                    # Assuming details is your dictionary
                    matching_keys = [i for i in details.keys() if re.match(r'^Image .+ Link$', i)]

                    # Now extract the values for these matching keys
                    image_links = [details[key] for key in matching_keys]
                    # Checks if list contains image
                    if image_links:
                        title = details['Paper title']
                        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
                        for char in invalid_chars:
                            title = title.replace(char, '_')

                        # Get the path to store image
                        article_dir = os.path.join(IMAGE_PATH, year_text, title)
                        # Create image folder
                        file_handling.create_dir(article_dir)
                        for image in image_links:
                            # Open the image in a new window in headless mode
                            bot2 = Journal()
                            bot2.get(image)
                            # Get cookies
                            cookies = bot2.get_cookies()
                            # Convert cookies to a dictionary format
                            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                            cookie = next(iter(cookie_dict.values()))
                            # Download image file
                            file_handling.download_file(image, article_dir, cookie)
                            # Close window
                            bot2.close()
                    # Populate the dataframe with the article details
                    new_dataframe = bot.populate_df(dataframe, details)

                    # Update the original dataframe with the new data
                    dataframe = new_dataframe

        # Close current tab/window
        bot.close()

        # Switch back to the original window
        bot.switch_to.window(bot.window_handles[0])

# Fill any NaN values in the dataframe with the text "Not Available"
dataframe = dataframe.fillna("Not Available")

# Save the populated dataframe to an Excel file
dataframe.to_excel(OUT_PATH, index=False)

# Close window
bot.close()
