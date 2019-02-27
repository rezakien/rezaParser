from MVideoParser import *
from datetime import datetime
# from multiprocessing import Pool
def main():
	start = datetime.now()
	#	Создает объект парсера MVideo
	html_ = MVideo()						
	
	# 	Возвращает список категорий
	print(html_.GetCategories())			
	
	#	Возвращает список подкатегорий
	print(html_.GetSubCategories())			
	
	#	Сохраняет товары в CSV-файл и возвращает список товаров. 
	#	Но так как товаров может быть очень много, функции сохранения и возвращение списка выключены.
	print(html_.GetProducts())				
	
	end = datetime.now()					
	totalTime = end-start
	print(str(totalTime.total_seconds()))	#	Потраченное время на парсинг и сохранение файлов
if __name__ == '__main__':
	main()
		