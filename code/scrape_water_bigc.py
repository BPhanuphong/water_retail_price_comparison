import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

def main_scraping():
    print('Start Scraping')
    url = 'https://www.bigc.co.th/category/water?limit=100&page={0}'
    response = requests.get(url.format(1))
    soup = BeautifulSoup(response.content, 'html.parser')   
    no_page = len(soup.find('div','pagination_pagination__wJ_sG').find_all('a'))
    product_name = []
    price = []
    for page in range(1,no_page+1):
        print('Page :',page)
        if page>1 :
            time.sleep(3)
            response = requests.get(url.format(page))
            soup = BeautifulSoup(response.content, 'html.parser')
            
        for element in soup.find_all('div','category_result_col__LmuH8'):
            product_name.append(element.find('div','productCard_title__f1ohZ').text)
            price.append(element.find('div','productCard_price__9T3J8').text.split('/')[0].replace('฿',''))

    bigC_df = pd.DataFrame(data={'product_name':product_name,
                                'price':price})

    bigC_df.to_csv('/opt/airflow/data_output/bigc_water.csv',index=False)
    print('Finish Scraping')
    print('Got {0} Sku'.format(len(bigC_df)))

if __name__ == "__main__":
    main_scraping()

