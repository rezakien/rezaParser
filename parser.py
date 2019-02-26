from MVideoParser import *
from datetime import datetime
from multiprocessing import Pool
def main():
	start = datetime.now()
	html_ = MVideo()						#	Создает объект парсера MVideo
	print(html_.GetCategories())			# 	Возвращает список категорий
	print(html_.GetSubCategories())			#	Возвращает список подкатегорий
	end = datetime.now()
	totalTime = end-start
	print(str(totalTime.total_seconds()))	#	Потраченное время на парсинг и сохранение файлов
if __name__ == '__main__':
	main()
		