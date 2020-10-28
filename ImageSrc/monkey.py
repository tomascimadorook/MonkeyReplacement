from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
from time import sleep
import random
import re
sns.set()

def scrap_houses(url):
	headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})


	meli_ids = []
	links = []
	imgs_main = []
	addresses = []
	full_addresses = []
	symbols = []
	prices = []
	mtrs = []
	rooms = []

	houses_readed = 0
	scrap = True
	pages = 0

	while scrap:

		web = url+str(houses_readed+1)
		pages += 1
		
		print("Requesting: " + web)
		print('Page: ' + str(pages))

		response = get(web, headers=headers)
		html_soup = BeautifulSoup(response.text, 'html.parser')
		
		if len(html_soup.body.findAll(text='Escribe en el buscador lo que quieres encontrar.')) >= 1:
			print("I reached the bottom of the list")
			scrap = False
		else:
			
			house_containers = html_soup.find_all('li', class_="ui-search-layout__item")
			just_readed = len(house_containers)
			houses_readed += just_readed
			duplicated = 0

			print("Items in page: " + str(just_readed))
			
			for house in house_containers:

				link = house.find_all('a', class_="ui-search-link")[0]["href"]
				meli_id = "MLU-" + link.split('com.uy/')[1].split('-')[1]

				if meli_id in meli_ids:
					duplicated += 1
					print("found a duplicated")
				else:
					meli_ids.append(meli_id)
					links.append(link)
				
					img_main = house.find_all('img', class_="ui-search-result-image__element")[0]["data-src"]
					imgs_main.append(img_main)

					address = house.find_all('h2', class_="ui-search-item__title")[0].text
					addresses.append(address)

					full_address = house.find_all('span', class_="ui-search-item__location")[0].text
					full_addresses.append(full_address)

					symbol = house.find_all('span', class_="price-tag-symbol")[0].text
					symbols.append(symbol)

					price = int(house.find_all('span', class_="price-tag-fraction")[0].text.replace('.',''))
					prices.append(price)

					mtrs_rooms = house.find_all('li', class_="ui-search-card-attributes__attribute")
					if len(mtrs_rooms) == 0:
						mtrs.append(0)
						rooms.append(0)			
					else:
						mtr = mtrs_rooms[0].text.split(' m²')[0]
						mtrs.append(int(''.join(filter(str.isdigit, mtr))))
						if len(mtrs_rooms) > 1:
							room = mtrs_rooms[1].text.split(' dorm')[0]
							rooms.append(int(room))
						else:
							rooms.append(0)
					
			if duplicated == just_readed:
				print("I reached the bottom of the list (by duplicates)")
				scrap = False
			else:
				generator = random.Random()
				sleep(generator.uniform(1,2))

	print("Finish!")
	print("Houses readed: " + str(houses_readed))

	print(len(links))
	cols = ['MELI_Id', 'URL', 'Image', 'Address', 'Full address', 'Currency', 'Price', 'Mtrs', 'Rooms']

	df_houses = pd.DataFrame({'MELI_Id': meli_ids,
							   'URL': links,
	                           'Image': imgs_main,
	                           'Address': addresses,
	                           'Full address': full_addresses,
	                           'Currency': symbols,
	                           'Price': prices,
	                           'Mtrs': mtrs,
	                           'Rooms': rooms})[cols]
	df_houses.to_excel('meli_raw_perquerodo.xls')

#scrap_houses("https://listado.mercadolibre.com.uy/inmuebles/apartamentos/venta/montevideo/pocitos/_Desde_")
scrap_houses("https://listado.mercadolibre.com.uy/inmuebles/apartamentos/venta/montevideo/parque-rodo/_Desde_")

df_houses = pd.read_excel('meli_raw_perquerodo.xls',header=0)
df_houses["Description"] = ''
df_houses["Latitude"] = 0
df_houses["Longitude"] = 0
df_houses["Seller_name"] = ''
df_houses["Monkey"] = False

headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

images_id = []
images = []

specs_id = []
specs_descr = []
specs_value = []

attrs_id = []
attrs = []

i = 0

for i in range(df_houses.index.size):

	row = df_houses.iloc[i]
	print(f"Processing: {row.MELI_Id}")
	
	response = get(row.URL, headers=headers)
	html_soup = BeautifulSoup(response.text, 'html.parser')

	################################################################################

	div_desc = html_soup.find_all('div', class_="item-description__text")
	if(len(div_desc) > 0):
		description = div_desc[0].get_text(separator=" ").strip()
	else:
		description = ''

	################################################################################

	e = re.findall("longitude:(.*?),", response.text)
	if len(e) > 0:
		gps_longitude = e[0].replace(' ','')
	else:
		gps_longitude = 0
	
	e = re.findall("latitude:(.*?),", response.text)
	if len(e) > 0:
		gps_latitude = e[0].replace(' ','')
	else:
		gps_latitude = 0

	################################################################################

	for image in html_soup.find_all('img'):
		if "-F.webp" in image['src']:
			img_src = image['src'].replace('webp','jpg')
			images.append(img_src)
			images_id.append(row.MELI_Id)

	
	################################################################################

	for sp in html_soup.find_all('li', class_="specs-item"):
		spec_descr = sp.find_all('strong')[0].text
		specs_descr.append(spec_descr)

		spec_value = sp.find_all('span')[0].text
		specs_value.append(spec_value)
		specs_id.append(row.MELI_Id)


	################################################################################

	
	for attr_container in html_soup.find_all('ul', class_="attribute-list"):
		for attr in attr_container.find_all('li'):
			attr_value = attr.text.strip()
			attrs.append(attr_value)
			attrs_id.append(row.MELI_Id)

	################################################################################

	seller_name = ""
	monkey = False

	seller_info = html_soup.find_all('section', class_="vip-section-seller-info")

	agency = seller_info[0].find_all('p', class_="disclaimer")
	if len(agency) > 0:
		seller_name = agency[0].text
		monkey = True
	else:
		seller_name = seller_info[0].find_all('p', class_="card-description")[0].text.strip()
		monkey = False

	################################################################################

	row["Description"] = description
	row["Latitude"] = gps_longitude
	row["Longitude"] = gps_latitude
	row["Seller_name"] = seller_name
	row["Monkey"] = monkey

	df_houses.iloc[i] = row

	generator = random.Random()
	sleep(generator.uniform(1,2))



cols = ['MELI_Id', 'URL']

df_images = pd.DataFrame({'MELI_Id': images_id,
							   'URL': images,
	                           })[cols]


cols = ['MELI_Id', 'Spec', 'Value']

df_spec = pd.DataFrame({'MELI_Id': specs_id,
							   'Spec': specs_descr,
							   'Value': specs_value,
	                           })[cols]

cols = ['MELI_Id', 'Attr']

df_attr = pd.DataFrame({'MELI_Id': attrs_id,
							   'Attr': attrs,
							   })[cols]


with pd.ExcelWriter('processed_data_parquerodo.xls') as writer:  
	df_houses.to_excel(writer, sheet_name='df_houses', merge_cells=False)
	df_images.to_excel(writer, sheet_name='df_images', merge_cells=False)
	df_spec.to_excel(writer, sheet_name='df_spec', merge_cells=False)
	df_attr.to_excel(writer, sheet_name='df_attr', merge_cells=False)
	

	# print(description)
	# print(gps_longitude)
	# print(gps_latitude)

	# for img in images:
	# 	print(img)

	# for i in range(len(specs_descr)):
	# 	print(f"{specs_descr[i]}: {specs_value[i]}")

	# for attr in attrs:
	# 	print(attr)

	# print(seller_name)
	# print(monkey)