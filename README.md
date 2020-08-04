<h1> OLX and OTODOM flats advertisements scraper </h1>

Purpose of this project was to create functional scraper of housing advertisements in Warsaw from site olx.pl and otodom.pl for further analysis of the data for learning purposes.
Project uses framework scrapy and saves results as json and csv format.
There is also attached example bayesian linear model created on cleaned data from the scraper.

<h1> How to run</h1>
To run the scraper:

    pip install -r requirements.txt
    python run_scraping.py
    
Results will be saved in "scraped" directory.