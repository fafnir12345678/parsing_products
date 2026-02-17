from bs4 import BeautifulSoup
import requests
import time
import os

# Определяем путь к директории, где лежит этот .py файл
parsing_dir = os.path.dirname(os.path.abspath(__file__))

url = "https://calorizator.ru/product"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")
tables_product = soup.find_all(class_="product") #все таблицы с продуктами на главной странице


prod_link_list=[]
#заполняем prod_link_list
for table in tables_product:
    products = table.find_all("li")
    for prod in products:
        name_prod = prod.a.get_text().replace('\n', '').replace('             ', '').replace('            ', '')
        link_prod = prod.a.get("href")
        
        #по итогу for-а создастся массив со всеми главными продуктами и их ссылками
        prod_link_list.append([name_prod,link_prod]) 
prod_link_list = prod_link_list[:-5:] #там есть таблица с личным кабинетом ее я убираю



products_sub_list = []
#работает с заполненным prod_link_list и заполняем products_sub_list
for prod in prod_link_list: 
    name_prod = prod[0]
    mail_linl = f"https://calorizator.ru/{prod[1]}" 
    res_sub = requests.get(mail_linl, headers=headers)
    soup_sub = BeautifulSoup(res_sub.text, "lxml")
    #заходим в каждую ссылку главного продукта
    products_sub = soup_sub.find("tbody").find_all("tr")


    while True:
        for prod_sub in products_sub:

            #все составные части продукта (имя, белки, жеры, угливоды, каллории)
            prod_sub_el = prod_sub.find_all("td")
            name_sub = prod_sub_el[1].get_text().replace('\n', '').replace('              ', '').replace('             ', '') #на [0] картинка она мне не нужна
            protein =prod_sub_el[2].get_text().replace('\n', '').replace('              ', '').replace('            ', '')
            fat = prod_sub_el[3].get_text().replace('\n', '').replace('              ', '').replace('            ', '')
            carb = prod_sub_el[4].get_text().replace('\n', '').replace('              ', '').replace('            ', '')
            kcal = prod_sub_el[5].get_text().replace('\n', '').replace('              ', '').replace('            ', '')
            products_sub_list.append([name_prod, name_sub, protein, fat, carb, kcal])


        #парсим туже категорию но след страницу
        next_page = soup_sub.find(class_="pager-next last")
        if next_page != None:
            next_page = next_page.a.get("href") #получаем след страницу или None если ее нету
            mail_linl = f"https://calorizator.ru/{next_page}"  
            res_sub = requests.get(mail_linl, headers=headers)
            soup_sub = BeautifulSoup(res_sub.text, "lxml")
            products_sub = soup_sub.find("tbody").find_all("tr")
            time.sleep(1)
        else:
            break


# Формируем путь к файлу внутри parsing6 рядом с .py
output_file = os.path.join(parsing_dir, "products.txt")

with open(output_file, "w", encoding='utf-8') as f:
    f.write("ПРОДУКТЫ С САЙТА CALORIZATOR.RU\n")
    f.write("=" * 80 + "\n\n")
    
    for item in products_sub_list:
        # Распаковываем элементы
        name_prod, name_sub, protein, fat, carb, kcal = item
        
        # Запись в файл
        f.write(f"📌 {name_prod} - {name_sub}\n")
        f.write(f"   Белки: {protein} | Жиры: {fat} | Углеводы: {carb} | Калории: {kcal}\n")
        f.write("-" * 80 + "\n")