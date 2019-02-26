from bs4 import BeautifulSoup
import requests
import csv
import os

class MVideo(object):
	# Поля класса парсера МВидео
	#
	#
	Categories = {}
	CategoriesColumnNames = []
	url = 'https://www.mvideo.ru/catalog'
	CategoriesFileName = 'files/categories.csv'
	SubCategoriesFileName = 'files/subcategories.csv'
	#
	#
	#
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
			self.CategoriesColumnNames.append('Категория')
			self.CategoriesColumnNames.append('Url')
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

	def writeCSV(self,filename=CategoriesFileName,columnsNames=CategoriesColumnNames,dictionary=Categories):
		if(os.path.isfile(filename)):
			print('Файл уже существует, откройте его')
		else:
			with open(filename, 'w',newline='',encoding='utf-8') as file:
				writer = csv.writer(file,delimiter="|")
				writer.writerow(columnsNames)
				for key,item in dictionary.items():
					writer.writerow([str(key).strip().replace('\"','') ,str(item).strip()])
			res = "Файл '" + filename.split('/')[1] + "'записан. Путь: '" + filename.split('/')[0] + "/'"
			print(res)