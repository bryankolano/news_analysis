#packages for scraping and driver
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

#baseline python packages needed
from datetime import datetime
import re
import argparse

#Pandas for data collection/ indexing
import pandas as pd



#create custom exception to check to see if output file name is a csv or not.
class BadExtensionException(Exception):

    def __init__(self, bad_ext):
        self.ext = bad_ext.split('.')[1]

    def __str__(self):
        return ('This must be a file extension CSV')





class CNN:

    def __init__(self, topic, driver_loc = None):

        """
        This class will open a Selenium webdriver through Chrome, grab the HTML
        contents of a particular CNN page (politics, sports, etc.) and it will 
        return a JSON of the scrapped informaton

        Parameters for initialization:
        topic (str): Select which news topic page to scrape (politics, sports), required.
        driver_loc (str): Tell the class the path to the chrome driver executable, default
                        is None if chrome driver in current directory


        Methods:
        - article_names_and_urls(): This method takes no inputs.
            We go to the topic page of interest, grab all the article title and urls and save them in the class variables: cnn_titles and cnn_urls

        - grab_and_parse_articles(): This method takes no inputs.
            This method grabs list of URLs in the cnn_url variables and then runs the webdriver through each one of these.  Through a loop, this method
            will collect all the text and the date of each article and will put them into a list.

        -append_csv(filename): This method takes a required input of file name with extension(which must be a .CSV file) for where to write the output
            This method takes the titles and urls found in the article_names_and_urls method and the article dates and text from the grab_and_parse_articles method
            It then combines everything into a Pandas dataframe and writes the output to the filename

        Returns:
        This class and all methods do not return anything.  The output of the append_csv method is to append to a CSV file.


        """
        self.topic = topic
        self.driver_loc = driver_loc
        
        #if driver is in working dir, then find driver executable.
        #otherwise, use the path provided to find the executable
        if driver_loc is None:
            self.service = Service(executable_path='chromedriver.exe')
        else:
            self.service = Service(executable_path= driver_loc)

        #get the base URL for cnn and append the topic to it
        self.base_url = 'https://www.cnn.com'
        self.topic_url = f"{self.base_url}/{topic}"


    def article_names_and_urls(self):
        
        #give the driver options to ignore errors   
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f"user-agent={user_agent}")
        options.headless = True
        
        driver = webdriver.Chrome(service= self.service, options= options)

        try:
            #get the topic URL in the driver and grab the page source
            driver.get(self.topic_url)
            topic_homepage_html = driver.page_source

            #soupify the page, turn into soup object
            topic_page_soup = BeautifulSoup(topic_homepage_html,'html.parser' )

            #grab the html of titles of all articles on the page
            self.politic_titles = topic_page_soup.select('.container__headline')

            #create list of all titles
            self.cnn_titles = [title.text.strip() for title in self.politic_titles]

            #create list of all titles' URLs extensionss
            url_extensions = [url['href'] for item in topic_page_soup.select('div.container_lead-plus-headlines__field-links') for url in item.select('a') ]
            
            #if no titles have been pulled (because CNN changed their HTML/ CSS structure) raise an error to notify.
            if len(url_extensions) == 0:
                raise ValueError('Need to recheck the CNN code, not pulling URLs')

            #combine base URL with each URL extension
            self.cnn_urls = [self.base_url + url for url in url_extensions]
        
        #if the webdriver runs into a driver exception issue, then state that an error exists
        except WebDriverException:
            print('Error getting main page')

        finally:
            driver.close()
      
     

    def grab_and_parse_articles(self):
  
        #set up blank lists to append to
        self.cnn_text_of_articles = []
        self.cnn_date = []

        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service= self.service, options= options)

        #loops across all URLs on the politics page
        for url in self.cnn_urls:

            try:
                #tell driver to grab each url
                driver.get(url)

                #turn each page into BS element and grab HTML
                page_soup = BeautifulSoup(driver.page_source,'html.parser' )
                
                #find HTML section that contains the text of the article
                article_contents =  page_soup.select('body > div.layout__content-wrapper.layout-with-rail__content-wrapper > section.layout__wrapper.layout-with-rail__wrapper > section.layout__main-wrapper.layout-with-rail__main-wrapper > section.layout__main.layout-with-rail__main > article > section > main > div.article__content-container > div.article__content > p')

                #take all the <p> of the article sections and join them together
                article_text = ' '.join([x.text.strip() for x in article_contents]) 

                #append article text to our holder list
                self.cnn_text_of_articles.append(article_text)

                #Need to grab the date from the article
                #find the line in the page HTML that has the date
                date_line = page_soup.select('div.timestamp')[0].text.strip()
                
                #create regex object to rip out the date
                date_re = re.compile(r'\w{3,}\s\d{1,2},\s\d{4}')
                #find the date from the pattern
                date = date_re.findall(date_line)[0]
                #turn into datetime object
                date = datetime.strptime(date, '%B %d, %Y')
                #return the date as a string in the format MM/DD/YYYY
                current_date = f"{date.month}/{date.day}/{date.year}"
                #append the current date to the date holder list
                self.cnn_date.append(current_date)

            except:
                continue

        driver.close()


    def append_csv(self,filename):
        self.filename = filename

        #in case of only providing filename and not extension, raise custom error
        if 'csv' not in self.filename.lower():
            raise BadExtensionException(filename)

        #set up blank dataframe with column names
        cnn_df = pd.DataFrame(list(zip(self.cnn_titles, self.cnn_date, self.cnn_urls, self.cnn_text_of_articles)), columns = ['title','date','url', 'article_text'])

        #creat new column in dataframe with the source of the articles
        cnn_df['source'] = 'CNN'

        #write the dataframe to a CSV
        cnn_df.to_csv(self.filename, index = False, header = False, mode= 'a')



class Fox:

    def __init__(self, topic):

        """
        This class instantiation will conduct a get request for a particular Fox News website
        

        Parameters for initialization:
        topic (str): Select which news topic page to scrape (politics, sports), required.



        Methods:
       

        - grab_and_parse_html(): This method takes no inputs.
            This method grabs all the URL extensions listed on the topic's main site (politics).  It also grabs the titles of the stories.
            Through a loop, this method will collect all the text and the date of each article and will put them into individual lists.

        -append_csv(filename): This method takes a required input of file name with extension (which must be a .CSV file) for where to write the output
            This method takes the titles and urls found in the article_names_and_urls method and the article dates and text from the grab_and_parse_articles method
            It then combines everything into a Pandas dataframe and writes the output to the filename

        Returns:
        This class and all methods do not return anything.  The output of the append_csv method is to append to a CSV file.


        """
        self.topic = topic

        #set the base url and append the topic type to it (politics, sports, etc.)
        self.base_url = 'https://www.foxnews.com'
        self.topic_url = f"{self.base_url}/{topic}"

    def grab_parse_html(self):

        #make GET request to Fox New's politics page and grab the HTML
        resp = requests.get(self.topic_url).text

        #turn HTML into Beautiful Soup Object
        self.fox_soup = BeautifulSoup(resp,'html.parser')

        #set up blank holder lists
        self.fox_urls = []
        self.fox_titles = []
        self.fox_text_of_articles = []
        self.fox_date = []

        #loop across all articles on the politics home page
        for article in self.fox_soup.select('main.main-content .content .article'):
            
            #a few of the elements in this particular CSS selector cause errors, so errors will be skipped with this try/ except
            try:
                #some of the links are video "articles" and I don't want to scrape those pages; there is very little information
                if 'VIDEO' in article.text:
                    continue
                #Take the URL extension, concatanate it with the base URL, and then add to the holder list
                self.fox_urls.append(self.base_url + article.find('a')['href'])
        
        
            except:
                continue

        #if no titles have been pulled (because fox news changed their HTML/ CSS structure) raise an error to notify.
        if len(self.fox_urls) == 0:
            raise ValueError('Need to recheck the Fox code, not pulling URLs')     

        #Loop across all URLs on the politics page to grab their article information
        for url in self.fox_urls:
                            
            #GET request of each page, grab the HTML text, and turn into BS object
            html = requests.get(url).text
            soup = BeautifulSoup(html,'html.parser')

            #Grab article title and append to holder list
            current_title = soup.select("h1.headline")[0].text
            self.fox_titles.append(current_title)

            #find the article section <p>s
            article_text_sections = soup.select('#wrapper > div.page-content > div.row.full > main > article > div > div.article-content > div > p')

            #grab all the paragraph element texts and join them together.    
            current_article = ' '.join([p.text for p in article_text_sections])
            #append the current article to the holder list
            self.fox_text_of_articles.append(current_article)

            #find the html section with the date
            date_line = soup.select('#wrapper > div.page-content > div.row.full > main > article > header > div.article-meta.article-meta-upper > div.article-date > time')[0].text
            #create regex element to rip the date out of that line
            date_re = re.compile(r'\w{3,}\s\d{1,2},\s\d{4}')
            #find the date with the regex pattern
            date = date_re.findall(date_line)[0]
            #turn found date pattern into datetime element
            date = datetime.strptime(date, '%B %d, %Y')
            #turn date element into string in format "MM/DD/YYYY"
            current_date = f"{date.month}/{date.day}/{date.year}"
            #append date string to holder list
            self.fox_date.append(current_date)

    
    def append_csv(self,filename):
        self.filename = filename
        if 'csv' not in self.filename.lower():
            raise BadExtensionException(filename)

        fox_df = pd.DataFrame(list(zip(self.fox_titles, self.fox_date, self.fox_urls, self.fox_text_of_articles)), columns = ['title','date','url', 'article_text'])

        #create new column with the source of these articles
        fox_df['source'] = 'Fox'

        #append the dataframe the new article CSV.
        fox_df.to_csv(self.filename, index = False, header = False, mode= 'a')
    



if __name__ == '__main__':

    arg = argparse.ArgumentParser(description= "Give filename and extension to save articles")
    arg.add_argument('-filename', help = 'Provide a filename and path to save article text', default='fake.csv')
    arguments = arg.parse_args()


    cnn = CNN(topic = 'politics', driver_loc = 'D:\Projects\gun_violence\chromedriver.exe')
    cnn.article_names_and_urls()
    cnn.grab_and_parse_articles()
    cnn.append_csv(arguments.filename)

    fox = Fox(topic= 'politics')
    fox.grab_parse_html()
    fox.append_csv(arguments.filename)