import requests
from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


def find_articles(categories, category, keyword, count):
	if int(count) < 1:
		return -1

	page = 1
	url = ""
	parsed_articles = {}
	viewed_articles = []

	with open("viewed.txt", "r", encoding="utf8") as file:
		for line in file:
			line = line.replace("\n", "")
			viewed_articles.append(line)

	url = categories[category].split("|")[1]

	while len(parsed_articles) < count:
		try:
			if page > 1:
				r = requests.get(url + f"page{page}")
			else:
				r = requests.get(url)
		except MissingSchema:
			return -1

		html = BeautifulSoup(r.content, "html.parser")
		articles = html.select(".tm-article-snippet")

		if len(articles) <= 0:
			break

		for el in articles:
			title_el = el.select(".tm-article-snippet__title-link")[0]
			title = title_el.text.lower()
			title_link = title_el['href']

			keyword = keyword.lower()
			if (f" {keyword} " in title
					or f"-{keyword}-" in title 
					or f" {keyword}-" in title 
					or f"-{keyword} " in title ) \
						and title not in viewed_articles:
				parsed_articles[title] = title_link

			if len(parsed_articles) == count:
					break

		page += 1

	with open("viewed.txt", "a", encoding="utf-8") as file:
		for article_name in parsed_articles:
			file.write(article_name + "\n")

	return parsed_articles


bot = Bot(token="1640410478:AAHhj1neqzlnPhrSjMYcKH4qmWeeO9PYG4M")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start(message : types.message):
	await message.answer("Для очистки списка просмотренных статей введите /clear")

	categories = "Категории:\n"
	with open("categories.txt", "r", encoding="utf-8") as file:
		i = 1
		for line in file:
			line = line.split("|")[0]
			categories += f"{str(i)}. {line}\n"
			i += 1

	await message.answer(categories)
	await message.answer("Укажите данные для поиска в виде КАТЕГОРИЯ:КЛЮЧЕВОЕ СЛОВО:КОЛИЧЕСТВО")


@dp.message_handler(commands="clear")
async def clear(message : types.message):
	with open("viewed.txt", "w") as f:
		pass
	await message.answer("Список просмотренных статей очищен")


@dp.message_handler()
async def inputs(message : types.message):
	categories = []

	with open("categories.txt", "r", encoding="utf-8") as file:
		for line in file:
			line = line.replace("\n", "")
			categories.append(line)

	try:
		category, keyword, count = message.text.split(":")
	except ValueError:
		pass
	
	# "category - 1" is for indexing categories array
	articles = find_articles(categories, int(category) - 1, keyword, int(count))

	if articles != -1:
		for title, link in articles.items():
			# link looks like /ru/post/id
			link = "https://habr.com" + link
			await message.answer(f"<a href=\"{link}\">{title}</a>\n\n", parse_mode="HTML")
	else:
		await message.answer("Запрос некорректен")
	

if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)
