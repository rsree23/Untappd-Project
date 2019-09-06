This README discusses the purpose of (1) ActivityFeed.py and (2) DrinkersInfo.py

# Overview
The purpose of this project is to conduct social listening on the subject of craft beer,
so that insights can be gained in regard to consumers of any particular company's brand.
The insights will help with marketing the product.

This project involves social listening, through which market research is done by analyzing social media platforms.
This is more beneficial than surveying the consumers, as individuals tend to view
social media as an outlet for more honest reflections and reviews.

# Information about Untappd
The social media scraped here is Untappd, a social network that allows users to share beers
that they drink, when they drink them, how they are drinking them.
These are called "check-ins."

A brewery can have a page on Untappd, and users' check-ins are provided in an activity feed.
Each user also has his/her own activity feed on his/her own profile page.
Individual beers and locations have their own feeds as well.

# File 1: ActivityFeed.py
ActivityFeed.py accomplishes the task of getting profile page links to each user who checks-in to a brewery's activity feed.
It then goes to each user's own feed and scrapes all of their checkins since they joined Untappd.
It accomplishes this using the selenium library in Python, which creates a fake web browsing session using a web driver.
This "bot" will collect user data, which is all public, by locating the html elements on the page.

A "show more" button appears at the bottom of every activity feed of Untappd.
On a brewery's page, the show more button can only be clicked until two days prior to the current date, and thus
only users who have checked-in from the past two days will be analyzed.

The program therefore must be run every ~ 2 days to get more users.

However, on each user's individual page, the show more button will never disappear, allowing any one user's entire drinking history
to be scraped, even if the first check-in was from 2012.

It should also be noted that one should insert time.sleep() statements before navigating to the next user's page,
as Untappd.com will get suspicious after many requests and can block one's IP address. Even with sleep, the program
will automatically slow down farther, in an attempt to prevent IP address blocking.
If one's IP address is blocked, it will unblock a few days later.

# File 2: DrinkersInfo.py
DrinkersInfo.py has a seemingly identical structure to ActivityFeed.py, but once on each user's page, the programs differ.
Each user also has a "Beer History," which displays  in an organized list every beer the user has checked-in,
providing the beer's style, ABV, IBU, and other data.
Also, the total count of how many times that beer has been consumed by that user is given.
DrinkersInfo.py scrapes this part of a user's profile: their "Beer History".

For both, scraped data is exported to a .csv file.

# Other Important Notes
Jupyter notebooks that I used for analysis of the data are not included due to confidentiality of the brewery.
They import the .csv files that the other two Python files create, and uses pandas and matplotlib Python libraries
to do data analysis/visualization.

For location analysis, gmaps is the Python library used to geocode (get latitude/longitude) the named locations scraped from Untappd.
Folium is the library used to actually plot coordinates onto a map (via OpenStreetMap).
An API key is needed, and one must register with Google Maps API (for the geocoding part).
Map creation is done via folium.

******* The two scraping Python files can scrape any brewery. Just change the URL in the first .get()
request to do similar analysis on a client's competitors. In addition, any individual beer can be scraped in
the same way, just make the get() request begin at that beer's Untappd page, not a brewery's page (see files for more information).

******* Here are some of the analyses I did with the data, but I cannot include due to confidentiality:  
Most common genders  
Most popular beers  
Most popular breweries  
Distribution of the most frequent hours of the day  
Most popular locations  
Distribution of user ratings  
******* Other exploratory analysis I would have liked to do include the following:  
Most popular beer styles among multiple breweries,  
Most popular mediums (can, bottle, growler) based on time of day (or month)  
Most popular beer styles based on time of day (or month)  
Most popular mediums based on beer style  
Do people rate beers higher/lower depending on time of day/month/year? Location?  
Are certain beer styles more popular at certain locations? At certain times?  
If two breweries are selling the same beer style at the same location, but one is selling more, why is there a difference? Can this data help answer that?  
How does the beer's label influence popularity (and therefore sales)? Image analysis of the beer label could be done?  
