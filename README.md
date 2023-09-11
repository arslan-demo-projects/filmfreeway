##The scraper scripts have been developed using python 3 

##Scrape auctions from [Surplex Website](https://www.surplex.com/es/a.html) and store the scraped auction results into a MYSQL database.

```
*** Step-1 ***

Script has developed using python3 or latest version. You can 
download and install IDE Pycharm Community Edition  (used for 
managing python projects and scripts).
```

### Download Pycharm from [Jetbrains](https://www.jetbrains.com/pycharm/download/) Official Website

###You can also get help from [Here](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/?ref=lbp) to know how to create virtual environment at linux or windows


```
*** Step-2 ***

Install latest pip version.

Now the below-mentioned modules need to install using terminal or 
command line interface using pip:-
```
`pip install scrapy==2.5.1`

`pip install gspread`

`pip install usaddress`

`pip install pyOpenSSL==22.0.0`

`pip install oauth2client==4.1.3`

`pip install cryptography==38.0.4`

##OR 

You can install all requirements using requirements.txt.
Please write this command in terminal:
````
pip install -r requirements.txt
````

```
*** Step-3 ***

Note: Now Set your project interpreter in which you have installed the
above modules / dependencies.
```

### *** Step-4 ***
### [Google SpreadSheet Link](https://docs.google.com/spreadsheets/u/1/d/1wYaCvdN9xb4GS04IeMjC_rwSfCkuUKxoUTWBFWiGTYY/edit#gid=0)

```
*** Step-5 ***

Open the command prompt and navigate into the project folder like:
cd filmfreeway
cd filmfreeway
cd spiders

```
### To run the spider script at command prompt please write command :-
`python filmfreeway_spider.py`

or

`python3 -m filmfreeway_spider.py`

####Note: Before run script Please make sure you are in project directory: 
####`~/filmfreeway/filmfreeway/spiders/`
 
If you have questions regarding script, please inbox me I will be happy
to help you!

````

*** Step-6 ***

Python Web Scraper integrated with Google Spreadsheet and Scrape Film 
Festivals Information from https://filmfreeway.com/festivals/. Firstly, 
the web scraper read film festivals names from google spreadsheet and 
then search names on website. Then it match the festival name from 
available results. If festival name matched, then scrape the details 
and update the records back in google spreadsheet.
````

```
*** Step-7 ***

For any query please send me message.
```
###best regards,
###Arslan Shakar
