from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import pandas as pd
import time
from splinter import Browser
import webbrowser

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    mars = {}
    
    #NEWS & PARAGRAPH
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    
    #find latest news title
    #find newsP

    news_title = soup.find(class_='content_title').text
    news_p = soup.find(class_='article_teaser_body').text
    mars["title"]=news_title
    mars["paragraph"]=news_p
    
    #featured img
    
    # URL of page to be scraped
    img_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_url)
 
    # featured_image_url = soup.find("a",class_="button fancybox")["data-fancybox-href"]
    full_image = browser.find_by_id("full_image")

    full_image.click()
    time.sleep(5)

    more_info = browser.find_link_by_partial_text("more info")
    more_info.click()
    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    img= soup.find(class_="lede")
    imgs = img.find(class_="main_image")["src"]

    # final_img = webbrowser.open("https://www.jpl.nasa.gov/"+imgs)
    # final_img
    mars["featured_img"]=("https://www.jpl.nasa.gov/"+imgs)
    
    #retrieve latest tweet
    twitter_url = u'https://twitter.com/marswxreport?lang=en'
    query= u'@marswxreport'

    r = requests.get(twitter_url+query)
    soup = BeautifulSoup(r.text, 'html.parser')

    tweets=[p.text for p in soup.findAll('p', class_='tweet-text')]
    mars["latest_tweet"]=tweets[1]
    
    #
    spaceUrl = 'https://space-facts.com/mars/'
    marsTbls = pd.read_html(spaceUrl)

    #find the initial table, create DF

    marsTbls[0]
    df = marsTbls[0]

    #create HTML table, open in web page

    html_table = df.to_html(classes="table table-striped")
    html_table
    html_table.replace('\n', '')
    # newTbl= df.to_html('table.html')
    #create and show dataframe

    df = df.iloc[0:]
    df.columns = ['Description', 'Value']
    df.set_index("Description", inplace=True)
    table = df.to_html()
    table = table.replace("\n"," ")
    mars["table"]=table
    
    #find jpg hemisphere images
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    imgItemListings = soup.find('div', class_='collapsible results')
    results = imgItemListings.find_all('div', class_='item')

    imageTitles = []
    hemisphere_image_urls = []


    for result in results:
        try: 
            title = result.find('h3')
            imageTitle = title.text.strip()
            imageTitles.append(imageTitle)
            titleFound = result.find('h3').text.strip()


            img_url = result.a['href'] 
            browser.visit('https://astrogeology.usgs.gov'+img_url)
            findLink = browser.find_link_by_text("Sample").first
            urlFound = findLink["href"]

        #Run only if title, URL are available
            if (titleFound and urlFound):

                post = {
                    'title': titleFound,
                    'image_url': urlFound,
                }

                hemisphere_image_urls.append(dict(post))
  


        except AttributeError as e:
            print(e)
        
    mars["hemisphere_images"]=hemisphere_image_urls    
    return mars
