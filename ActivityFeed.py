from selenium import webdriver # The "fake" browser library
import time
import pandas
import ast
from multiprocessing import Pool
import random
from collections import Counter


# Set up browser session with selenium driver
driver = webdriver.Chrome()

# Fake account on Untappd, takes no time at all to make one, put your info here
my_username = ''
my_password = ''

# Login
driver.get('https://untappd.com/login') # get() goes makes the request to access a url
username = driver.find_element_by_id('username')
username.send_keys(my_username) # The browser can type using send_keys()
password = driver.find_element_by_id('password')
password.send_keys(my_password)
sign_in_button = driver.find_element_by_xpath('/html/body/div/div/div/form/span') # can find elements by xpath, css selector, id, tag name, etc.

sign_in_button.click()

# A banner asking you to enter a phone number shows up, blocking the show mre button; this needs to be closed
driver.get('https://untappd.com/thepub')
time.sleep(5) # If the page isn't give enough time tp load elements can't be found by the browser, so sleep for x seconds
driver.switch_to.frame('branch-banner-iframe') # The banner is in a different frame, so switch to it to close it then switch back
driver.find_element_by_id('branch-banner-close').click()
driver.switch_to.default_content()


# Click the "Show More" button 'i' times to load more checkins
def showMoreActivity():
    i = 0
    mainstream = driver.find_element_by_class_name('content')
    while True:
        try:

            show_more_button = mainstream.find_element_by_xpath('//*[@id="slide"]/div/div/div[3]/div/a') # Specific location on a brewery page
            show_more_button.click()
            time.sleep(random.randint(3,5)) # Need this for same reason as above
            print("show more button pressed")
            i += 1
        except Exception as e:
            print(e)
            break
    print(i)
# For each user's beer history
def showMoreHistory():
    # i = 0
    user_mainstream = driver.find_element_by_class_name('content')
    while True:
        try:
            show_more_button = user_mainstream.find_element_by_xpath('//*[@id="slide"]/div/div[2]/div[2]/div/a') #Specific location on user's page
            show_more_button.click()
            time.sleep(random.randint(2, 4))
            print("show more button pressed")
            # i += 1
        except Exception as e:
            print(e)
            break

# This gets all of the users who checked into a brewery's feed
def getUsers(brewer_url):
    driver.get(brewer_url)
    name_list = []
    profilepage_list = []
    showMoreActivity()
    name_elements = driver.find_elements_by_class_name('user')
    for name in name_elements:
        name_list.append(name.get_attribute('innerText'))
        profilepage_list.append(name.get_attribute('href'))
    return name_list, profilepage_list


# Get the names and profile pages of each user who is checking in on a brewery's page
url = ''  # Can change to any brewery URL on Untappd
results = getUsers(url)
names = results[0]
profilepage_URLs = results[1]
print(profilepage_URLs)


# Go to each user's profile page and get beer history
def getBeerHistory(list_of_profiles):
    time_consumed_list = []
    user_name_list = []
    beer_list = []
    brewery_list = []
    location_name_list = []
    location_link_list = []
    medium_list = []
    rating_list = []
    purchased_list = []
    comment_list = []

    # Deals with multiple counting of any one checkin
    link_df = pandas.DataFrame.from_dict(Counter(list_of_profiles), orient='index').reset_index()
    link_df.columns = ['Profile Link', 'Count']

    for link in link_df['Profile Link']:
        try:
            driver.get(link)
            showMoreHistory()
            check_in_elements = driver.find_elements_by_class_name('checkin')
            for checkin in check_in_elements:

                # Get time beer is consumed
                time_consumed = checkin.find_element_by_css_selector('a.time.timezoner.track-click').get_attribute(
                    'data-gregtime')
                time_consumed_list.append(time_consumed)

                # Get checkin name, beer, brewery, and location
                checkin_text_initial = checkin.find_element_by_class_name('text')
                checkin_text_elements = checkin_text_initial.find_elements_by_tag_name('a')

                # Get username
                user_name = checkin_text_elements[0].get_attribute('innerText')
                user_name_list.append(user_name)

                # Get beer name
                beer_name = checkin_text_elements[1].get_attribute('innerText')
                beer_list.append(beer_name)

                # Get brewery name
                brewery_name = checkin_text_elements[2].get_attribute('innerText')
                brewery_list.append(brewery_name)

                # Get location
                if len(checkin_text_elements) >= 4:
                    location_name = checkin_text_elements[3].get_attribute('innerText')
                    location_name_list.append(location_name)
                    location_link = checkin_text_elements[3].get_attribute('href')
                    location_link_list.append(location_link)
                else:
                    location_name_list.append("None")
                    location_link_list.append("None")

                # Get medium
                try:
                    medium_initial = checkin.find_element_by_class_name('serving')
                    medium = medium_initial.find_element_by_tag_name('span').get_attribute('innerText')
                    medium_list.append(medium)
                except Exception:
                    medium_list.append('None')

                # Get rating
                try:
                    rating_initial = checkin.find_element_by_class_name('rating-serving')
                    medium_and_rating = rating_initial.find_elements_by_tag_name('span')
                    if len(medium_and_rating) > 1:
                        rating_raw = medium_and_rating[1].get_attribute('class')
                        rating = rating_raw[-3:]
                        rating_list.append(rating)
                    elif len(medium_and_rating) == 1:
                        rating_raw = medium_and_rating[0].get_attribute('class')
                        rating = rating_raw.split[-3:]
                        rating_list.append(rating)
                except Exception:
                    rating_list.append('None')

                # Get purchase location
                try:
                    purchased_initial = checkin.find_element_by_class_name('purchased')
                    purchased_location = purchased_initial.find_element_by_tag_name('a').get_attribute('innerText')
                    purchased_list.append(purchased_location)
                except Exception:
                    purchased_list.append('None')

                # Get checkin comment
                try:
                    comment = checkin.find_element_by_class_name('comment-text').get_attribute('innerText')
                    comment_list.append(comment)
                except Exception:
                    comment_list.append('None')
            time.sleep(random.randint(5, 8))

        except Exception as e:
            print(e)
            break

    data_dictionary = {'Name': user_name_list,
                    'Time (UTC)': time_consumed_list,
                    'Beer': beer_list,
                    'Brewery': brewery_list,
                    'Location': location_name_list,
                    'Purchase Location': purchased_list,
                    'Rating': rating_list,
                    'Medium': medium_list,
                    'Comment': comment_list}

    return data_dictionary


# Apply Multiprocessing on the main function, getBeerHistory
# if __name__ == '__main__':
#     pool = Pool(processes=4)
#     result = pool.apply_async(getBeerHistory, (profilepage_URLs,))
#     untappd_dictionary = result.get()


untappd_dictionary = getBeerHistory(profilepage_URLs) # comment out this line if you want to do multiprocessing
# Put all scraped data into a gigantic DataFrame
untappd_df = pandas.DataFrame(untappd_dictionary)
pandas.set_option("display.max_colwidth", 300)
pandas.set_option("display.max_info_columns", 200)
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1500)
untappd_df.to_csv('', index=False) # Make sure to change csv file name before each run so that data is not overwritten


# To close the browser session, only do at very end
driver.quit()
