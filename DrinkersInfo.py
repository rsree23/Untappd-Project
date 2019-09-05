from selenium import webdriver  # The "fake" browser library
import time
import pandas
import ast
from multiprocessing import Pool
import random
from collections import Counter

# Set up a browser session with selenium driver
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
time.sleep(5) #If the page isn't give enough time to load elements can't be found by the browser, so sleep for x seconds
driver.switch_to.frame('branch-banner-iframe') # The banner is in a different frame, so switch to it to click "x" then switch back
driver.find_element_by_id('branch-banner-close').click()
driver.switch_to.default_content()


# Click the "Show More" button 'i' times to load more checkins on a brewery's page
def showMoreActivity():
    i = 0
    mainstream = driver.find_element_by_class_name('content')
    while True:
        try:
            show_more_button = mainstream.find_element_by_xpath('//*[@id="slide"]/div/div/div[3]/div/a') # Specific location on a brewery page
            show_more_button.click()
            time.sleep(random.randint(5, 10)) # Need this for same reason as above
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
            show_more_button = user_mainstream.find_element_by_xpath('//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/a') #Specific location on beer history page
            show_more_button.click()
            time.sleep(random.randint(3, 4))
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


# To get only numerical values from ratings
def cut_out_text(text):
    if text.startswith('THEIR'):  # Deals with "THEIR RATING (X.XX)"
        text = text[:-1]  # Removes last character
        text = float(text[14:])
    elif text.startswith('GLOBAL'):  # Deals with "GLOBAL RATING (X.XX)"
        text = text[:-1]
        text = float(text[15:])
    elif text.endswith('ABV'):  # Deals with "4.8% ABV"
        if text.startswith('No'):
            text = 0.0
        else:
            text = float(text[:-5])
    elif text.endswith('IBU') or text.startswith('Total:'):
        for s in text.split():  # Deals with "12 IBU" or "Total: 1"
            if s.isdigit():
                text = int(s)
    return text

# Convert string to a dictionary
def str_to_dict(string):
    dict = ast.literal_eval(string)
    return dict

# Convert dictionary to DataFrame, handles columns with different lengths, accounts for null values
def dict_to_df(dict):
    keys_list = []
    values_list = []
    for item in dict.keys():
        keys_list.append(item)
    for item in dict.values():
        values_list.append(item)
    new_dict = {}
    df = pandas.DataFrame(new_dict)
    for i in range(len(keys_list)):
        df[keys_list[i]] = pandas.Series(values_list[i])
    return df

# Go to each user's profile page and get beer history
def getBeerHistory(list_of_profiles):
    user_names = []
    beers = []
    beer_styles = []
    breweries = []
    one_ratings = []
    two_ratings = []
    ABVs = []
    IBUs = []
    totals = []

    # Deals with multiple countings of any one checkin (i.e. one user checking in multiple times, only need first checkin)
    link_df = pandas.DataFrame.from_dict(Counter(list_of_profiles), orient='index').reset_index()
    link_df.columns = ['Profile Link', 'Count']

    for link in link_df['Profile Link']:
        try:
            driver.get(link + '/beers?sort=checkin') # Orders beers based on how many beers have been drunk, highest to lowest
            beer_elements = driver.find_elements_by_class_name('beer-details')

            for i in range(len(beer_elements)):
                user_name_initial = driver.find_element_by_class_name('info')
                user_names.append(user_name_initial.find_element_by_tag_name('h1').get_attribute('innerText')) # Gets text bewteen opening and closing html tags
                # Get beer name
                beername = beer_elements[i].find_element_by_class_name('name')
                actual_beer_name = beername.find_element_by_tag_name("a").get_attribute('innerText')
                beers.append(actual_beer_name)

                # Get brewery name
                breweryname = beer_elements[i].find_element_by_class_name('brewery')
                actual_brewery_name = breweryname.find_element_by_tag_name("a").get_attribute('innerText')
                breweries.append(actual_brewery_name)

                # Get beer style
                actual_beer_style = beer_elements[i].find_element_by_class_name('style').get_attribute('innerText')
                beer_styles.append(actual_beer_style)

                # Get ratings
                rating_element = beer_elements[i].find_element_by_class_name('ratings')
                for rating in rating_element.find_elements_by_tag_name('p'):
                    beer_rating = rating.get_attribute('innerText')
                    if beer_rating.startswith('THEIR') == True:
                        one_ratings.append(cut_out_text(beer_rating))
                    elif beer_rating.startswith('GLOBAL') == True:
                        two_ratings.append(cut_out_text(beer_rating))

            # Get specific beer stats
            beer_stats = driver.find_elements_by_class_name('details')
            for stat in beer_stats:
                # Get ABV
                beer_abv = stat.find_element_by_class_name('abv').get_attribute('innerText')
                ABVs.append(cut_out_text(beer_abv))

                # Get IBU
                beer_ibu = stat.find_element_by_class_name('ibu').get_attribute('innerText')
                IBUs.append(cut_out_text(beer_ibu))

                # Get total number of times this beer has been consumed
                beer_total = stat.find_element_by_class_name('check-ins').get_attribute('innerText')
                totals.append(cut_out_text(beer_total))
            time.sleep(random.randint(3,4))

        except Exception as e:
            print(e)
            break

    data_dictionary = {'Name': user_names,
                    'Beer': beers,
                    'Beer Style': beer_styles,
                    'Brewery': breweries,
                    'User Rating': one_ratings,
                    'Global Rating': two_ratings,
                    'ABV': ABVs,
                    'IBU': IBUs,
                    'Total': totals}

    return data_dictionary


# Apply Multiprocessing on the main function, getBeerHistory
# if __name__ == '__main__':
#     pool = Pool(processes=4)
#     result = pool.apply_async(getBeerHistory, (profilepage_URLs,))
#     untappd_dictionary = result.get()


untappd_dictionary = getBeerHistory(profilepage_URLs) # comment out this line if you want to do multiprocessing
# # Put all scraped data into a gigantic DataFrame
untappd_df = dict_to_df(untappd_dictionary)
pandas.set_option("display.max_colwidth", 300)
pandas.set_option("display.max_info_columns", 200)
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1500)
untappd_df.to_csv('', index=False) # Make sure to change csv file name before each run so that data is not overwritten


# To close the browser session, only do at very end
driver.quit()
