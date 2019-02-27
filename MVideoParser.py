from bs4 import BeautifulSoup
import requests
import csv
import os
import json
class MVideo(object):
	# Поля класса парсера МВидео
	Categories = {}
	Products = {}
	CategoriesColumnNames = ['Категория','Url']
	ProductsColumnNames = ['Продукт','Цена(руб.)','Категория']
	url = 'https://www.mvideo.ru/catalog'
	CategoriesFileName = 'files/categories.csv'
	SubCategoriesFileName = 'files/subcategories.csv'
	ProductsFileName = 'files/products.csv'
	def __init__(self):
		self.url = self.url
	
	def get_url(self):
		return self.url

	def get_html(self):
		response = requests.get(self.get_url())
		return response.text
	
	def GetCategories(self):
		if(os.path.isfile(self.CategoriesFileName)):
			print("Считываем с файл '"+self.CategoriesFileName+"'")
			with open(self.CategoriesFileName, 'r',encoding='utf-8', newline='') as openedCsv:
				reader = csv.reader(openedCsv, delimiter='|')
				for item in reader:
					if(not item[0]=='Категория'):
						CategoryName = item[0]
						CategoryUrl = item[1]
						AbsoluteUrl =  CategoryUrl
						self.Categories[CategoryName] = AbsoluteUrl
			if 'Акции' in self.Categories.keys():
				del self.Categories['Акции']
		else:
			soup = BeautifulSoup(self.get_html(),'lxml')
			Categoriessoup = soup.find("div",{"class":"js-catalog-container"}).find_all("div",{"class":"c-catalog-item"})
		
			self.CategoriesColumnNames.append('Категория')
			self.CategoriesColumnNames.append('Url')
			for item in Categoriessoup:
				CategoryName = item.find('h3').find('a').getText().strip()
				CategoryUrl = item.find('h3').find('a').get('href').strip()
				AbsoluteUrl = self.url + CategoryUrl
				self.Categories[CategoryName] = AbsoluteUrl
			del self.Categories['Акции']
			filename = self.CategoriesFileName
			columnsName = ['Категория','Url']
			dictionary = self.Categories
			self.writeCSV(filename,columnsName,dictionary)
		return self.Categories
	
	def GetSubCategories(self):
		SubCategory = {}
		if(os.path.isfile(self.SubCategoriesFileName)):
			print("Считываем с файл '"+self.SubCategoriesFileName+"'")
			with open(self.SubCategoriesFileName, 'r',encoding='utf-8', newline='') as openedCsv:
				reader = csv.reader(openedCsv, delimiter='|')
				for item in reader:
					if(not item[0]=='Подкатегория'):
						SubCategoryName = item[0]
						SubCategoryURL = item[1]
						SubCategory[SubCategoryName] = SubCategoryURL
		else:
			SubCategoryName = ''
			SubCategoryURL = ''
			self.Categories = self.GetCategories()
			for i,item in self.Categories.items():
				self.url = item
				soup = BeautifulSoup(self.get_html(),'lxml')
				try:
					objSubCategory = soup.find('ul',{'class':'sidebar-categories-list'}).find_all('li')
					for i in objSubCategory:
						SubCategoryName = i.find('a').getText()
						SubCategoryURL = self.url + i.find('a').get('href')
						SubCategory[SubCategoryName] = SubCategoryURL
				except Exception:
					print('Что-то пошло не так')
				finally:
					print("Подкатегория '" + SubCategoryName + "' готова к парсингу")
			columnsName = ['Подкатегория','Url']
			dictionary = SubCategory
			filename = self.SubCategoriesFileName
			self.writeCSV(filename,columnsName,dictionary)
		return SubCategory
	def GetProducts(self):
		if(os.path.isfile(self.SubCategoriesFileName)):
			with open(self.SubCategoriesFileName, 'r', encoding='utf-8', newline='') as CsvReader:
				reader = csv.reader(CsvReader, delimiter='|')
				for row in reader:
					if(not row[0]=='Подкатегория'):
						try:
							totalPages = self.GetPages(row[1])
							if(not totalPages==None):
								for i in range(0,totalPages+1):
									if(not totalPages==0):
										pagePart = '/page=' if 'f' in row[1].split('/') else '/f/page='
										if(i<=totalPages):
											i += 1
										self.url = row[1] + pagePart + str(i)
									else:
										self.url = row[1]

									print(self.url,'total pages =',totalPages)
									soup = BeautifulSoup(self.get_html(),'lxml')
									try:
										productsDict = dict.fromkeys(['ProductName','ProductLocalPrice','ProductCategoru'], 'None')
										productsSoup = soup.find('div',{'class':'o-plp-container__product-listing'}).find_all('div',{'class':'product-tiles-list-wrapper'})
										for products in productsSoup:
											productsList = products.find_all('div',{'class':'c-product-tile__description'})
											productsDict = {}
											for index,productObject in enumerate(productsList):
												#! Блок, отвечающий за, непостредственно, парсинг 
												ProductDictObject = json.loads(productObject.find('h4').find('a').get('data-product-info'))
												ProductName = ProductDictObject['productName']
												ProductPrice = ProductDictObject['productPriceLocal']
												ProductCategory = ProductDictObject['productCategoryName']
												ProductUrl = productObject.find('h4').find('a').get('href').strip()
												productsDict[index] = {'ProductName':ProductName,'ProductPrice':ProductPrice,'ProductCategory':ProductCategory,'ProductUrl':ProductUrl}
											self.writeCSVProducts(self.ProductsFileName,self.ProductsColumnNames,productsDict)
									except Exception:
										print('Error on parsing the certain product!')
						except Exception:
							print('Error on scraping the subcategories!')
		else:
			self.GetSubCategories()
			self.GetProducts()
	def GetPages(self,html):
		self.url = html
		html = self.get_html()
		soup = BeautifulSoup(html,'lxml')
		optionsPagination = {'class':'c-pagination'}
		lastPageOption = {'class':'c-pagination__num c-btn c-btn_white'}
		try:
			pages = 0
			if(self.isPaginatinable(soup)==True):
				try:
					pages = soup.find('div',attrs=optionsPagination).find('a',attrs=lastPageOption).getText()
				except Exception:
					pages = 0
			else:
				print('Структура страницы отличается от алгоритма для парсинга.')
				return None
		finally:
			return int(pages)
	def isPaginatinable(self,soup):
		optionsCheck = {'class':'product-tiles-list-wrapper'}
		try:
			check = soup.find('div',attrs=optionsCheck)
		except Exception:
			check = None
			print('error on accessing to pagination.')
		if(not check==None):
			return True
		else:
			return False
	def writeCSV(self,filename=CategoriesFileName,columnsNames=CategoriesColumnNames,dictionary=Categories):
		if(os.path.isfile(filename)):
			print('Файл уже существует, откройте его')
		else:
			with open(filename, 'w',newline='',encoding='utf-8') as file:
				writer = csv.writer(file,delimiter="|")
				writer.writerow(columnsNames)
				for key,item in dictionary.items():
					if('promo' not in str(item)):
						writer.writerow([str(key).strip().replace('\"','') ,str(item).strip().split('?')[0]])
			res = "Файл '" + filename.split('/')[1] + "'записан. Путь: '" + filename.split('/')[0] + "/'"
			print(res)
	def writeCSVProducts(self,filename,columnsNames,dictionary):
		with open(filename, 'a',newline='',encoding='utf-8') as file:
			writer = csv.writer(file,delimiter="|")
			writer.writerow(columnsNames)
			for key,item in dictionary.items():
				for key, item in item.items():
					writer.writerow([str(key).strip() ,str(item)])
		res = "Файл '" + filename.split('/')[1] + "'записан. Путь: '" + filename.split('/')[0] + "/'"
		print(res)