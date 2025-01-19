#%% md
# ### Establish Workspace
#%%
import openai
from openai import OpenAI
import arcpy
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
#%% md
# ### Scrape Website (Simple)
#%%
# Set up the driver (example with Chrome)
service = Service(r'C:\ArcWorkSpace\PersonalProjects\NewReportsJapan\chromedriver-win64\chromedriver.exe')  # Use raw string to avoid issues with backslashes
driver = webdriver.Chrome(service=service)

# Open a webpage
driver.get("https://geocgi.com/")

# Wait for the page to load
driver.implicitly_wait(5)  # seconds

# Get the title of the page
page_title = driver.title

# Print the title
print(page_title)

# Close the browser
driver.quit()

#%% md
# ### Collect Article: Link, Title, Image
#%%
def extract_articles_from_link(driver, link):
    # Open the webpage
    driver.get(link)

    # Wait for the page to load
    driver.implicitly_wait(10)  # seconds

    try:
        # Find the specific content div (content-list content-6)
        content_div = driver.find_element(By.CSS_SELECTOR, 'ul.module--pickup-list')

        # Find all the article items under this div
        article_items = content_div.find_elements(By.CSS_SELECTOR, 'li.module--pickup-item')

        # Create a list to store article dictionaries
        articles = []

        # Loop through each article item and extract the necessary details
        for item in article_items:
            article_link = item.find_element(By.CSS_SELECTOR, 'a.module--pickup-link').get_attribute('href')
            
            # Exclude articles with the specific link
            if article_link == "https://www3.nhk.or.jp/news/special/lnews":
                continue
            
            title = item.find_element(By.CSS_SELECTOR, 'p.module--pickup-text').text
            image_url = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            
            # Handle relative image URLs
            if image_url.startswith('/'):
                image_url = f"https://www3.nhk.or.jp{image_url}"
            
            # Create a dictionary for each article and append it to the list
            article_dict = {
                'link': article_link,
                'title': title,
                'image_url': image_url
            }
            
            articles.append(article_dict)

        return articles

    except Exception as e:
        print(f"Error extracting articles from {link}: {str(e)}")
        return []

def main():
    # Set up the driver (example with Chrome)
    service = Service(r'C:\PATH-TO-CHROME-DRIVER')  # Use raw string to avoid issues with backslashes
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # List of weblinks to process
    weblinks = [
        "https://www3.nhk.or.jp/news/word/0002227.html",
        "https://www3.nhk.or.jp/news/word/0002230.html",
        "https://www3.nhk.or.jp/news/word/0002229.html",
        "https://www3.nhk.or.jp/news/word/0002225.html",
        "https://www3.nhk.or.jp/news/word/0002226.html",
        "https://www3.nhk.or.jp/news/word/0002228.html"
        # Add more links as needed
    ]

    all_articles = []

    for link in weblinks:
        articles = extract_articles_from_link(driver, link)
        all_articles.extend(articles)

    # Close the browser
    driver.quit()

    return all_articles

if __name__ == "__main__":
    all_articles = main()
    # Print the list of articles
    for article in all_articles:
        print(article)
#%% md
# ### Go to Article Pages, Get Article Content, Add to Dictionaries
#%%
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Setup the Chrome WebDriver
service = Service(r'C:\ArcWorkSpace\PersonalProjects\NewReportsJapan\chromedriver-win64\chromedriver.exe')  # Use raw string to avoid issues with backslashes
driver = webdriver.Chrome(service=service)

# Loop through each article and extract the content
for article in all_articles:
    driver.get(article['link'])
    
    # Wait for the page to load (increase time if necessary)
    time.sleep(3)
    
    # Extract all text elements
    try:
        text_elements = driver.find_elements(By.TAG_NAME, 'body')  # Start from <body> to capture all text
        article['content'] = " ".join([element.text for element in text_elements])  # Combine all text
    except Exception as e:
        print(f"Error extracting content for {article['title']}: {str(e)}")

# Close the WebDriver
driver.quit()

# Print the list of articles
for article in all_articles:
    print(article)
    print("")
#%% md
# ### Open AI translate and generate X,Y
#%%
client = openai.OpenAI(api_key="YOUR-API-KEY")

for article in all_articles:
    # Translate the title to English
    response_title = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "translate title to English"
            },
            {
                "role": "user",
                "content": article['title']
            }
        ]
    )
    article['title-en'] = response_title.choices[0].message.content
    
    # Provide an article summary in English
    response_articleSummary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Create a summary of the article in English. The summary should be around one-third to one-quarter the length of the original article. Meaning if the article was 1000 words long, your summary should be around 250 to 330 words."
            },
            {
                "role": "user",
                "content": article['content']
            }
        ]
    )
    article['summary-en'] = response_articleSummary.choices[0].message.content
    
    # Provide an article summary in Japanese
    response_articleSummary_JP = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Create a summary of the article in Japanese. The summary should be around one-third to one-quarter the length of the original article. Meaning if the article was 1000 words long, your summary should be around 250 to 330 words."
            },
            {
                "role": "user",
                "content": article['content']
            }
        ]
    )
    article['summary-jp'] = response_articleSummary_JP.choices[0].message.content

    # Extract geographical coordinates from content
    response_coords = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Analyze the following text to identify any mentioned geographical locations. "
                    "If a location is found, extract its approximate geographical coordinates "
                    "(latitude and longitude) in the format: [Latitude: {value}, Longitude: {value}]. "
                    "If no specific coordinates are mentioned, infer approximate coordinates based on "
                    "the described location or skip the response if no geographic data is present."
                )
            },
            {
                "role": "user",
                "content": article['content']
            }
        ]
    )
    
    try:
        coords = response_coords.choices[0].message.content.strip()
        
        # Use regex to extract coordinates from the response
        match = re.search(r"Latitude:\s*([\d.-]+).*?Longitude:\s*([\d.-]+)", coords)
        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            article['x'] = latitude
            article['y'] = longitude

            # Ask the AI to explain its choice of geographical location in English
            response_explanation_en = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain why you chose the geographical location you did in the previous response. "
                            "Provide details on how you inferred the coordinates based on the text."
                        )
                    },
                    {
                        "role": "user",
                        "content": article['content']
                    },
                    {
                        "role": "assistant",
                        "content": coords
                    }
                ]
            )

            # Extract the explanation from the response
            explanation_en = response_explanation_en.choices[0].message.content
            article['coords_explanation'] = explanation_en
            
            # Ask the AI to explain its choice of geographical location in Japanese
            response_explanation_jp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Translate the following explanation to Japanese: "
                            f"{explanation_en}"
                        )
                    }
                ]
            )

            # Extract the explanation from the response
            explanation_jp = response_explanation_jp.choices[0].message.content
            article['coords_explanation_JP'] = explanation_jp

        else:
            # Handle cases where coordinates are not found
            print(f"No coordinates found for article {article['title']}")
            article['x'] = None
            article['y'] = None
            article['coords_explanation'] = None
            article['coords_explanation_JP'] = None
    except Exception as e:
        print(f"Error extracting coordinates for article {article['title']}: {e}")
        article['x'] = None
        article['y'] = None
        article['coords_explanation'] = None
        article['coords_explanation_JP'] = None

# Print the updated articles list for verification
for article in all_articles:
    print(article)
#%% md
# ### Connect to the "News Reports (Kansai)" Feature Class
#%%
arcpy.env.workspace = r"C:\ArcWorkSpace\PersonalProjects\NewReportsJapan\NewReportsJapan.gdb"
newsReportsKansai = "kansai_news"
#%% md
# ### Create a feature within the "News Reports (Kansai)" Feature Class
#%%
import arcpy

arcpy.env.workspace = r"C:\ArcWorkSpace\PersonalProjects\NewReportsJapan\NewReportsJapan.gdb"
newsReportsKansai = "kansai_news"

# Get the spatial reference of the feature class
input_spatial_ref = arcpy.SpatialReference(4326)
output_spatial_ref = arcpy.Describe(newsReportsKansai).spatialReference

# Debugging: Print spatial references
print(f"Input Spatial Reference: {input_spatial_ref.factoryCode}")
print(f"Output Spatial Reference: {output_spatial_ref.factoryCode}")

# Debugging: Print field information
fields = arcpy.ListFields(newsReportsKansai)
for field in fields:
    print(f"Field: {field.name}, Type: {field.type}, Length: {field.length}")

for article in all_articles:
    # Points to add (WGS 84 lat/long)
    new_features = [
        [(article['y'], article['x'])]  # Example coordinates
    ]
    
    # Define the dictionary for feature values
    featureValues = {
        "prefecture": "Osaka",
        "summary_en": article['summary-en'],
        "summary_jp": article['summary-jp'],
        "article_title_en": article['title-en'],
        "article_title_jp": article['title'],
        "article_link": article['link'],
        "image_link": article['image_url'],
        "location_reason_en": article['coords_explanation'],
        "location_reason_jp": article['coords_explanation_JP'],
    }
    
    try:
        # Start an edit session on the workspace
        editor = arcpy.da.Editor(arcpy.env.workspace)  # Editor applied to the workspace
        editor.startEditing(False, True)  # Start editing, False = no undo, True = versioned
        editor.startOperation()  # Start the edit operation
    
        # Insert new points
        with arcpy.da.InsertCursor(newsReportsKansai, ["SHAPE@", "prefecture", "summary_en", "summary_jp", "article_title_en", "article_title_jp", "article_link", "image_link", "location_reason_en", "location_reason_jp"]) as cursor:
            for coords in new_features:
                # Create point geometry
                point = arcpy.PointGeometry(arcpy.Point(*coords[0]), input_spatial_ref)
                if input_spatial_ref.factoryCode != output_spatial_ref.factoryCode:
                    point = point.projectAs(output_spatial_ref)
                
                # Debugging: Print the values being inserted
                print(f"Inserting point: {point}")
                print(f"Feature values: {featureValues}")
                
                cursor.insertRow([point, featureValues["prefecture"], featureValues["summary_en"], featureValues["summary_jp"], featureValues["article_title_en"], featureValues["article_title_jp"], featureValues["article_link"], featureValues["image_link"], featureValues["location_reason_en"], featureValues["location_reason_jp"]])
    
        editor.stopOperation()  # Stop the edit operation
        editor.stopEditing(True)  # Commit the changes
    
        print("Points added successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")

# Verify the features were added
print("Verifying added features:")
with arcpy.da.SearchCursor(newsReportsKansai, ["SHAPE@XY", "prefecture", "summary_en", "summary_jp", "article_title_en", "article_title_jp", "article_link", "image_link", "location_reason_en", "location_reason_jp"]) as cursor:
    for row in cursor:
        print(row)

# Check the attribute table
print("Checking attribute table:")
with arcpy.da.SearchCursor(newsReportsKansai, ["prefecture", "summary_en", "summary_jp", "article_title_en", "article_title_jp", "article_link", "image_link", "location_reason_en", "location_reason_jp"]) as cursor:
    for row in cursor:
        print(row)
#%%
