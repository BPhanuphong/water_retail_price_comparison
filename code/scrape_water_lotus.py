import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

def main_scraping():
    print('Start Scraping')
    # Lotus API
    url = "https://api-o2o.lotuss.com/lotuss-mobile-bff/product/v2/products?q=%7B%22offset%22:{0},%22limit%22:100,%22filter%22:%7B%22categoryId%22:[%2291288%22]%7D,%22websiteCode%22:%22thailand_hy%22%7D"

    # Headers is required 'Accept-Language' , Select 'en' or 'th'
    payload={}
    headers = {
    'Accept-Language': 'th'
    }
    
    # Making requests to API using Get Method
    response = requests.request("GET", url.format(0), headers=headers, data=payload)

    #Get Respong as json
    response_json = eval(response.text.replace('null','None').replace('false','False').replace('true','True'))

    # Find number of page
    no_page = response_json['meta']['total']//response_json['meta']['limit']+1
    product_name = []
    price = []

    # Loop through each page
    for page in range(0,no_page):
        print('Getting page {0}'.format(page))
        if page>0 :
            time.sleep(3)
            payload={}
            headers = {
            'Accept-Language': 'th'
            }
            
            response = requests.request("GET", url.format(page*100), headers=headers, data=payload)
            response_json = eval(response.text.replace('null','None').replace('false','False').replace('true','True'))
            
        # Extract product name
        [product_name.append(response_json['data']['products'][item]['name']) for item in range(len(response_json['data']['products']))]
        # Extract product price
        [price.append(response_json['data']['products'][item]['priceRange']['minimumPrice']['finalPrice']['value']) for item in range(len(response_json['data']['products']))]

    lotus_df = pd.DataFrame(data={'product_name':product_name,
                             'price':price})
    lotus_df.to_csv('/opt/airflow/data_output/lotus_water.csv',index=False)

    print('Finish Scraping')
    print('Got {0} Sku'.format(len(lotus_df)))

if __name__ == "__main__":
    main_scraping()
