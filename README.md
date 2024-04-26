Auther : Phanuphong Siriphongwatana

## Overview
This project contains a web scraping pipeline designed to extract data specifically related to water products from two major retail websites in Thailand: BigC and Lotus. The pipeline automates the process of fetching ,storing SKU data and matching providing a structured output that can be used for price comparison and market analysis.

## Agenda
- Data collection
- Data Preprocessing
- Run pipeline


## Data collection

Our target is to get all water products related name and price by `scraping` on bigc and lotus website using  `python` language.

### BigC
For Big C web site we use normal approach using reqeusts and beautifulsoup

url : https://www.bigc.co.th/category/water?limit=100&page={0}

return format : html

Parameter :
- limit : 100
- page : (Check number of page from next page button)

Sample Data Output
| product_name | price | 
|------------|------------|
| คริสตัล น้ำดื่ม 600มล. | 6.00 | 
| มิเนเร่ น้ำแร่ธรรมชาติ 330 มล. แพ็ค 12 | 85.00 | 
| คริสตัล น้ำดื่ม 1500 มล. แพ็ค 6 | 54.00 | 


### Lotus
For lotus website we using api that we found on the website (Found using google chrome network inspect Fetch/XHR ) pull with requests.

api url : https://api-o2o.lotuss.com/lotuss-mobile-bff/product/v2/products?q=%7B%22offset%22:{0},%22limit%22:100,%22filter%22:%7B%22categoryId%22:[%2291288%22]%7D,%22websiteCode%22:%22thailand_hy%22%7D

return format : json

Parameter :
- limit : this is a limit number of product that api will return 
- offset : which product to start return with

Sample Data Output
| product_name | price | 
|------------|------------|
| สิงห์น้ำดื่ม1500มล. แพ็ค 6 | 55.0 | 
| โลตัส น้ำแร่ธรรมชาติ 100% 1500 มล.แพ็ค6 | 85.0 | 
| น้ำทิพย์น้ำดื่ม1500มล. แพ็ค 6 | 49.0 | 

## Data Preprocessing
### Extract size of product

We define water volume in มล.(milliliters) and ล.(liters).

- Convert to same scale by replacing 'มิลลิลิตร' with 'มล.' and 'ลิตร' with 'ล.'
- Use Regular Expression to find the nunmber in front of 'มล.' and 'ล.'
  - pattern = r'\d+(\.\d+)?ล\.|\d+(\.\d+)?ล|\d+(\.\d+)?มล\.|\d+(\.\d+)?มล'
- Convert all to milliliters scale.

| product_name  | size|
|------------|-----------|
| คริสตัล น้ำดื่ม 600มล. | 600.0 |
| มิเนเร่ น้ำแร่ธรรมชาติ 330 มล. แพ็ค 12 | 330.0 |
| คริสตัล น้ำดื่ม 1500 มล. แพ็ค 6  | 1500.0|

### Extract quantity of product

Quantity will be in product name in 3 format
- แพ็ค 6
- 12  ขวด
- x6

Use Regular Expression to find the number of quantity
  - pattern = r'แพ็ค\s*(\d+)|(\d+\s*ขวด)|x\s*(\d+)|X\s*(\d+)'

If can't find quantity keyword will be assign with 1.

| product_name  | quantity |
|------------|-----------|
| คริสตัล น้ำดื่ม 600มล. |1 |
| มิเนเร่ น้ำแร่ธรรมชาติ 330 มล. แพ็ค 12 | 12 |
| คริสตัล น้ำดื่ม 1500 มล. แพ็ค 6 | 6|

### Clean Product Name
In this process we remove size and quantity from previous step

| product_name  |size| quantity | clean_name |
|------------|-----------|-----------|-----------|
| คริสตัล น้ำดื่ม 600มล. | 600.0 | 1 | คริสตัลน้ำดื่ม|
| มิเนเร่ น้ำแร่ธรรมชาติ 330 มล. แพ็ค 12 | 330.0 | 12 | มิเนเร่น้ำแร่ธรรมชาติ|
| คริสตัล น้ำดื่ม 1500 มล. แพ็ค 6 | 1500.0| 6| คริสตัลน้ำดื่ม|

### Matching
2 Step
1. Match with equal size and quantity
2. Match with clean product name
    - Using `Levenshtein distance` to find the difference between two product name. This will output as score of similarity
    - Select Max score that above 0.8 score
  
|product_name|	price|	size	|quantity	|clean_name	|lotus_id	|lotus_product_name	|lotus_price|	lotus_size|	lotus_quantity|
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
|มิเนเร่ น้ำแร่ธรรมชาติ 330 มล.แพ็ค 12	|85.0	|330.0	|12	|มิเนเร่น้ำแร่ธรรมชาติ	|74.0	|มิเนเร่น้ำเเร่ธรรมชาติ330มล. แพ็ค 12|	85.0	|330.0	|12.0|
|เปอริเอ้ น้ำแร่อัดลม รสสตรอเบอร์รี่ 250 มล.	|44.0	|250.0|	1|	เปอริเอ้น้ำแร่อัดลมรสสตรอเบอร์รี่|	125.0|	เปอริเอ้ น้ำแร่อัดก๊าซ สตรอเบอร์รี่ 250 มล.	|42.0	|250.0	|1.0|
|วอลวิก น้ำแร่ธรรมชาติ 1.5 ล.	|82.0	|1500.0	|1	|วอลวิกน้ำแร่ธรรมชาติ|	103.0	|วอลวิกน้ำแร่ธรรมชาติ 1500มล.|	82.0|	1500.0	|1.0|


## Steps running pipeline 

In this datapipeline will use airflow for scraping and matching to compare the price from each website. All of the service will be on docker container using docker-compose.

### Prerequisites
Ensure you have the following installed on your system:
- Docker
- Docker Compose


### 1. Set up the Docker Environment
- Clone this repository to your local machine.
- Navigate to the project directory.

### 2. Airflow DAG
- Inside this project there already contain DAG file in `dags` folder (datapipeline_dags.py).
- DAG containing three tasks:
  1. `scraping_lotus`: This task will scrape water sku from lotus website.
  2. `scraping_bigc`: This task will scrape water sku from bigc website.
  3. `matching_sku`: This task will match each sku from bigc with lotus.

### 3.Run Docker Containers
- You can start the containers by using 
```
docker-compose up -d
```
Docker will start Airflow

### 4. Login into Airflow console.
- Use web browser and go to localhost:8080 
- Login using :
    - **Username** : airflow
    - **Password** : airflow

### 5. Running pipeline
- In the DAG details page, you will see an DAG call scraping_water_comparision.
- Click on the DAG name to view its details.
- Turn on DAG by click the `Pause/Unpause` near DAG name.
- Trigger the DAG by click on the `trigger button` (play button).
- Monitor for DAG run process to be green mean success.

### 6. Check data in data_output
- File :
    1. bigc_water.csv
    2. lotus_water.csv
    3. matching.csv

## Future work
This project just collecting process only 1 cetegory of item in retail store. 
- collect more product on another category
- making visulization on price comparison
- make price strategy base on this data.
