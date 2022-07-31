from bs4 import BeautifulSoup
import requests

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import os


def find_articles(category, keyword, count):
	if count < 1:
		return -1

	page = 1
	url = ""
	parsed_articles = []

	match category:
		case "1":
			url = "https://habr.com/ru/hub/lib/"
		case _:
			pass

	# if page > 1:
	# 	url = url + f"/page{page}"


	def get_html(page):
		if page > 1:
			r = requests.get(url + f"page{page}")
		else:
			r = requests.get(url)
		
		return BeautifulSoup(r.content, "html.parser")


	while len(parsed_articles) < count:
		html = get_html(page)
		articles = html.select(".tm-article-snippet")

		if len(articles) <= 0:
			break

		for el in articles:
			title = el.select(".tm-article-snippet__title-link")[0].text

			if keyword in title:
				parsed_articles.append(title)

			if len(parsed_articles) == count:
					break

		page += 1
		# if page < 5:
		# 	page += 1
		# else:
		# 	return parsed_articles

	return parsed_articles


bot = Bot(token="1640410478:AAHhj1neqzlnPhrSjMYcKH4qmWeeO9PYG4M")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start(message : types.message):
	await message.answer("Укажите данные для поиска в виде КАТЕГОРИЯ:КЛЮЧЕВОЕ СЛОВО:КОЛИЧЕСТВО")
	await message.answer("""1. Профессиональная литература
2. Python
3. Rust

		""")


@dp.message_handler()
async def inputs(message : types.message):
	category, keyword, count = message.text.split(":")
	articles = find_articles(category, keyword, int(count))

	await message.answer("\n".join(articles))

# @dp.message_handler(regexp="^[a-z]")
# async def choose_keyword(message : types.message):
# 	keyword = message.text
# 	await message.answer("Укажите количество статей")


# @dp.message_handler(regexp="^[0-9]")
# async def choose_count(message : types.message):
# 	count = int(message.text)
# 	articles = find_articles(category, keyword, count)

# 	await message.answer("\n".join(articles))


if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)

# # find_articles("1", "Rust", 3)
