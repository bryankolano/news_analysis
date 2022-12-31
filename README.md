# Political News Stories Collection
## A script to gather political stories from CNN.com and foxnews.com
## By: Bryan Kolano, Original repo creation: December 7th, 2022
### Updated: December 31, 2023

***

#### Background
Approximately a month ago, I was trying to think of a new project that involved text and classification.  I had been watching a decent amount of news coverage leading up to the mid-term elections of 2022.  I would see vasty different coverage of the same stories online and on the t.v. depending on what the source was.  An idea occurred to me about how it might be interesting to do  analysis of political stories.  With CNN and Fox News, the language they use is very different, they focus on different topics, and their coverages of the same topics are typically very different.  Perhaps the data exists on the internet, but I didn't find any that I wanted to use for this project, so I decided to create my own dataset.    <br>

The point of this repo is to grab new headlines each day from each news sources and then combine them in a CSV.  After a couple hundred (maybe a couple thousand) stories are collected, I plan to do analysis in a different script.  I want to examine differences between the two sources, and I also plan to test various machine learning algorithms to see if they can correctly classify whether a text comes from CNN or Fox News.

#### Files in this repo
1. news_articles.ipynb: This is the first script I wrote to webdrive CNN articles and webscrape Fox New articles.  
2. get_articles.py: This script contains the two custom classes to grab the articles from CNN and Fox, called CNN and Fox, respectively.  
- Each of these classes take one argument: the new topics (politics, sports, etc.).  Even though this project focuses on political articles, I wrote the class in case I wanted to grab other types of articles. 
- When calling this script, a command line argument is required for the output CSV filename that you would like to write to.  
 -Currently, I have created a Windows batch file that runs this script every morning through the Windows Task Scheduler.  The .bat file activates the conda environment and then runs this script and outputs the results to news_articles.csv.
3. requirements.txt: Python packages required for these scripts.
4. (future) CSV of news articles with title, date, URL, article text, and article source (CNN vs Fox).
5. (future) Text analysis of articles.

#### Collection of CNN Articles

From 2019-2021, while I was part of the Army's Intelligence and Security Command Data Science Team, we used to teach a class called "Introduction to Advanced Data Analytics in R" (called OS305) to open source intelligence analysts.  These analysts were soldiers, army civilians, and government contractors who were looking to be able to do analysis on data collected from the open internet. <br>

These student had minimal experience in R; they had only taken a small coding bootcamp before OS305.  As part of each iteration of OS305, I gave a block of instruction on webscraping.  For the class, we scraped a couple of pre-determined websites to show a website's HTML and CSS and then scrape the data. <br>

During one iteration of the class, I decided to call an audible and grab a random website to scrape.  I broke a cardinal rule of teaching coding: don't live code in front of students, haha.  I chose CNN.com and tried to webscrape it using R.  No matter how many ways I tried to manipulate the HTML and CSS structure, I could not pull the information I wanted.  I told the class that I would look into a get back to them.  <br>

As it turns out, CNN among many other websites uses JavaScript to render content once it is loaded in the browser.  In other words, in webscraping, you're trying to grab information that doesn't exist yet because you are making a GET request at a point before the actual content is loaded/ rendered.  At the time, I did not know CNN did that, and alas, webscraping would not work for CNN and I shared with the class the reason.
<br>

Due to the way CNN renders content, it is necessary to use webdriving to navigate CNN and gather data.  Therefore, the CNN sections of the script use Selenium to gather the page information and then use Beautiful Soup to parse the HTML document.  <br>

After grabbing the information from each news article, I turn it into a Pandas Dataframe and then write the results to a CSV called "news_articles."


#### Collection of Fox News Articles
Fortunately, Fox news does not render its content in the same way CNN does.  Therefore, a standard webscrape with the requests package can be used to grab the HTML.  Webdriving is unnecessary to grab Fox News data, so I can simply make the GET request and then parse the HTML response with Beautiful Soup.

After grabbing all article information, I turn it into a Pandas Dataframe and then write to the same CSV I am adding all the CNN articles to. 

#### CSV Creation
After I pull the political articles for a few months, I plan to push the CSV to this repo.

#### Text Analysis
Once I have a large enough collection of articles, I plan to do text analysis on the articles.  I liked to find common themes amoung CNN vs. Fox News articles.  I will also experiment to determine which machine learning algorithms provide the best classification of CNN vs. Fox articles.