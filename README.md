# Kansai News Today Web Map

This project displays a 3D web map of Kansai News using the ArcGIS API for JavaScript and Google 3D Tiles in both Japanese and English.  
The underlying data is created using Python. 
The Python script uses web scraping to gather article information.
The openai module then generates:
- A translated English title
- A summary in English and Japanese
- A x-y coordinate pair for the articles estimated location based on the content of the article
- A reason for the above chosen location in both English and Japanese.

---

## Prerequisites

- [Google Maps Platform API Key](https://developers.google.com/maps/documentation/tile/get-api-key)
- [OpenAI API Key](https://openai.com/index/openai-api/)
- [ChromeDriver](https://developer.chrome.com/docs/chromedriver)
- [ArcGIS Online Account](https://www.esri.com/en-us/home)

---

## Setup

### 1. **Install ChromeDriver**
- Download the appropriate version of ChromeDriver from the link above.  
- ChromeDriver is needed to perform the web scraping tasks in the Python file.

### 2. **Configure API Keys**

#### Google Cloud API Key:
1. Go to the [Google Maps Platform API Key](https://developers.google.com/maps/documentation/tile/get-api-key).
2. Scroll down until you see "Creating API keys" and follow the instructions there.
3. Create an API key and restrict it to your domain (e.g., `https://gismagician.github.io`).  
4. Replace `YOUR_API_KEY` in `scripts.js` with your actual API key.

#### OpenAI API Key:
1. Sign up for an API key at [OpenAI API Key](https://openai.com/index/openai-api/).
2. You will have purchase some credits for this to work. In my experience, running the script once cost $0.01 to $0.02
3. Replace `YOUR_OPENAI_API_KEY` in `pythonNewsReport.py` with your actual API key.

#### ArcGIS Online Account:
1. Sign in to your [ArcGIS Online](https://www.esri.com/en-us/home) account.  
2. Create a empty webscene.  
3. Replace `YOUR_WEBSCENE_ID` in `scripts.js` with your actual webscene ID.
4. You will have to make your own target feature layer for the data to be stored.
5. You can look at the one I used [here](https://gismagican.maps.arcgis.com/home/item.html?id=1c4b4999d63e4beeba518e3a375ce5ba) as a guide.

---

## File Structure

- `index.html`: The main HTML file that sets up the web page.  
- `style.css`: The CSS file for styling the web page.  
- `scripts.js`: The JavaScript file that initializes the ArcGIS web scene and adds layers.  
- `pythonNewsReport.py`: A Python script for scraping news articles and updating the ArcGIS Online layer.

## Any questions?
If you had problems with getting this setup, or want to talk more about it, please tell me!
My email is wmbroll@gmail.com
Thank you for taking the time to read this and I hope you have a good rest of your day.
