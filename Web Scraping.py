
import  pymongo
import requests 
from bs4 import BeautifulSoup
from datetime import date



def customizer_the_heading(lst):
    return lst[0].replace("\n","")


def customizer_the_elements(lst):
    string = lst[0].replace("\n","")
    string = string.encode("ascii","ignore")
    return string.decode()
    

def customizer_the_productprice(price):
    price = str(price)
    price = price.split("-")
    if len(price) == 1:
        if "₹" in price[0]:
            price = price[0].replace("₹","").replace(",","")
            return float(price)
        elif "$" in price[0]:
            price = price[0].replace("$","")
            return 74.19*float(price)
    elif len(price)==2:
        if "₹" in price[0] and "₹" in price[1]:
            price0 = price[0].replace("₹","").replace(",","")
            price1 = price[1].replace("₹","").replace(",","")
            return (float(price0)+float(price1))/2
        elif "$" in price[0]:
            price0 = price[0].replace("$","")
            price1 = price[0].replace("$","")
            return ((float(price0)+float(price1))/2)*74.19


def series_or_model(data):
    lst = ["Model","Series"]

    for l in lst:
        if l in data.keys():
            return data[l]

def product_price_ids(soup):
    ids = ["priceblock_ourprice","priceblock_dealprice"]
    for ID in ids:
        NoneType = type(None)
        price = soup.find(id=ID)

        if isinstance(price, NoneType) is not True:
            return price.get_text()



def data_entry(my_database,product_type,id,data,product_price):
    my_collection = my_database[f"{product_type} Details"]
    if my_collection.find({"_id":id}).count() != 1:
        my_collection.insert_one(data)
    else:
        my_collection.update_one(
            {"_id":id},
            { "$push" :{"Price Tracker":{"Date":f"{date.today()}","Price":product_price}}}
        )




my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = my_client["product_data-vise-price_details"]
url_data = open("C:\\Users\\evil1\\Desktop\\amazon electronic type data\\Product URLs.txt","r")
lines = url_data.readlines()


for URL in lines:

    #URL = "https://www.amazon.in/ASUS-i7-10750H-ScreenPad-Celestial-UX581LV-XS74T/dp/B08D941WH6/ref=pd_sbs_7/258-1968671-9530502?pd_rd_w=zTJNT&pf_rd_p=18688541-e961-44b9-b86a-bd9b8fa83027&pf_rd_r=8S1D8FT6AVF007ZE0M4W&pd_rd_r=d138c222-d7ff-47b7-ae3c-df5f12848aa8&pd_rd_wg=GpR5H&pd_rd_i=B08D941WH6&psc=1"
    Headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
    page = requests.get(URL,headers= Headers)
    soup = BeautifulSoup(page.content , "lxml")


    table_1 = soup.find("table" ,attrs={"id":"productDetails_techSpec_section_1"})
    table_2 = soup.find("table" ,attrs={"id":"productDetails_detailBullets_sections1"})


    table_1_data = table_1.find_all("tr")
    table_2_data = table_2.find_all("tr")


    data = {}


    for tr in table_1_data:
        th = tr.find_all("th")
        td = tr.find_all("td")
        heading = customizer_the_heading([th.text for th in th])
        elements = customizer_the_elements([td.text for td in td])
        data.__setitem__(heading,elements)


    for tr in table_2_data:
        th = tr.find_all("th")
        td = tr.find_all("td")
        heading = customizer_the_heading([th.text for th in th])
        elements = customizer_the_elements([td.text for td in td])
        data.__setitem__(heading,elements)


    product_price = customizer_the_productprice(product_price_ids(soup))
    data.__setitem__("Price Tracker",[])
    data.__setitem__("_id",data["ASIN"])
    product_type = data["Generic Name"]
    id = data["ASIN"]
    data_entry(my_database,product_type,id,data,product_price)