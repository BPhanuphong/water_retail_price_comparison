import pandas as pd
import time
import editdistance
import re

# Use for extract size from product name
def get_size(name):
    name = name.replace(' ','').replace('มิลลิลิตร','มล.').replace('ลิตร','ล.').replace(',','')     # Change to same format of mesure

    # Find number in front of ล,มล,ล.,มล.
    pattern = r'\d+(\.\d+)?ล\.|\d+(\.\d+)?ล|\d+(\.\d+)?มล\.|\d+(\.\d+)?มล'
    if re.search(pattern, name):
        name_match = re.search(pattern, name)[0]
        if 'มล' not in name_match:
            return int(float(name_match.split('ล')[0])*1000) # Convert to milliliter
        else:
            return int(name_match.split('มล')[0])
    else: 
        return None

# Use for extract quantity from product name
def get_quantity (name):

    name = name.replace(' ','')
    
    # Find number in after of แพ็ค,X or in front of ขวด
    pattern = r'แพ็ค\s*(\d+)|(\d+\s*ขวด)|x\s*(\d+)|X\s*(\d+)'
    if re.search(pattern, name):
        name_match = re.search(pattern, name)
        return int(name_match[0].replace('แพ็ค','').replace('ขวด','').replace('x','').replace('X',''))  #Remove all unit to extract only number
    else:
        return 1


def clean_name(name):
    #Remove Size and Quantity from product name
    name = name.replace(' ','').replace('มิลลิลิตร','มล.').replace('ลิตร','ล.').replace(',','').replace('ชิ้น','')
    size_pattern = r'\d+(\.\d+)?ล\.|\d+(\.\d+)?ล|\d+(\.\d+)?มล\.|\d+(\.\d+)?มล'
    quantity_pattern = r'แพ็ค\s*(\d+)|(\d+\s*ขวด)|x\s*(\d+)|X\s*(\d+)'
    
    if re.search(size_pattern, name):
        size_match = re.search(size_pattern, name)[0]
        name = name.replace(size_match,'')
    if re.search(quantity_pattern, name):
        quantity_match = re.search(quantity_pattern, name)[0]
        name = name.replace(quantity_match,'')
    return name



def main():
    bigC_df = pd.read_csv('/opt/airflow/data_output/bigc_water.csv')
    lotus_df = pd.read_csv('/opt/airflow/data_output/lotus_water.csv')

    bigC_df['size'] = bigC_df['product_name'].apply(lambda x : get_size(x))
    bigC_df['quantity'] = bigC_df['product_name'].apply(lambda x : get_quantity(x))
    lotus_df['size'] = lotus_df['product_name'].apply(lambda x : get_size(x))
    lotus_df['quantity'] = lotus_df['product_name'].apply(lambda x : get_quantity(x))
    bigC_df['clean_name'] = bigC_df['product_name'].apply(lambda x : clean_name(x))
    lotus_df['clean_name'] = lotus_df['product_name'].apply(lambda x : clean_name(x))
    lotus_df = lotus_df.reset_index().rename(columns={'index': 'lotus_id'})
    bigC_df = bigC_df.reset_index().rename(columns={'index': 'bigc_id'})
    bigC_df['lotus_id'] = None

    # Check for matching
    for index in range(len(bigC_df)):
        bigc_name = bigC_df['clean_name'].loc[index]
        print(index)
        print('big c:' ,bigc_name)

        # Filter for same size and quantity
        match_size_df = lotus_df[(lotus_df['size']==bigC_df['size'].loc[index])&(lotus_df['quantity']==bigC_df['quantity'].loc[index])]
        name_list = match_size_df['clean_name'].values.tolist()
        id_list =  match_size_df['lotus_id'].values.tolist()
        score = []
        if len(name_list)>0:

            #Loop to check name similarity in name_list
            for name in name_list:
                distance = editdistance.eval(bigc_name, name)
                max_length = max(len(bigc_name), len(name))
                similarity = 1 - (distance / max_length)
                score.append(similarity)
                
            # Set score to be above 0.8
            if max(score)>0.8:
                print('Matching')
                print(id_list[score.index(max(score))])
                print(lotus_df['product_name'].loc[id_list[score.index(max(score))]])
                bigC_df['lotus_id'].loc[index] = id_list[score.index(max(score))]
            else:
                print('Low Score')
        else:
            print('Not Found')



    bigC_df = bigC_df.merge(lotus_df[['lotus_id','product_name','price','size','quantity']].rename(columns={'product_name': 'lotus_product_name','price':'lotus_price','size':'lotus_size','quantity':'lotus_quantity'}), 
                on='lotus_id', how='left')

    print('match found:{0}'.format(len(bigC_df['lotus_id'].dropna())))
    print(bigC_df[bigC_df['lotus_id'].notna()])

    bigC_df.to_csv('/opt/airflow/data_output/matching.csv')


if __name__ == "__main__":
    main()
