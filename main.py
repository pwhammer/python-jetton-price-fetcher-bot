import telebot
import constants
import asyncio
import requests
import json
import configparser
from loguru import logger
from gql import gql
from redoubt_agent import RedoubtEventsStream
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bs4 import BeautifulSoup

API = constants.API_KEY
token_API = constants.TOKEN #telebot.TeleBot(constants.token)
bot = Bot(token_API)
dp = Dispatcher(bot)
Sending_prices = 0
RedoubtEventsStream.api_key = API
keyboard = ReplyKeyboardMarkup() #!
keyboard.add()
HEPL_COMMAND = """
<b>/star</b> - Начать работу с ботом
<b>/help</b> - Список комманд
<b>/settings</b> - Описание бота
"""

async def run_query():
    logger.info("Running GraphQL query")
    stream = RedoubtEventsStream()
    res = await stream.execute("""
    query nft {
        redoubt_nft_deals(order_by: {deal_time: desc}, limit: 1) {
            sale_address
            address
            deal_time
            seller
            buyer
            price
        }
    }
    """)
    logger.info(f"Got last NFT deals: {res}")

@dp.message_handler(commands=['start'])
async def start_command(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать в телеграм бот AreYouRichEnough! Для того, чтобы узнать возможности бота - введите комманду /settings. Хорошего дня!",
                           parse_mode="HTML",
                           reply_markup=keyboard)
    await message.delete()

@dp.message_handler(commands=['help'])
async def help_command(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text=HEPL_COMMAND, parse_mode="HTML")
    await message.delete()

@dp.message_handler(commands=['settings'])
async def settings_command(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text='Здесь раз в минуту будет появлятся актуальная цена токена Scale. Для запуска бота, напиши в чат - /run',
                           parse_mode="HTML")
    await message.delete()

@dp.message_handler(commands=['run'])
async def run_command(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text='<b>Напиши любую цифру, букву или слово, чтобы остановить ежеминутную отправку курса TON</b>',
                           parse_mode="HTML")
    await message.delete()
    while True:
        logger.info("Running GraphQL query")
        stream = RedoubtEventsStream()
        res = await stream.execute("""
            query nft {
                redoubt_nft_deals(order_by: {deal_time: desc}, limit: 1) {
                    sale_address
                    address
                    deal_time
                    seller
                    buyer
                    price
                }
            }
            """)
        logger.info(f"Got last NFT deals: {res}")
        await bot.send_message(chat_id=message.from_user.id, text='Цена на <b>TON</b> в $ составляет: ', parse_mode="HTML")
        await bot.send_message(chat_id=message.from_user.id, text=res)
        await asyncio.sleep(60)
        # Sending_prices = bot.send_message(chat_id=message.from_user.id, text=Sending_prices)
        # if Sending_prices != 0:
            #break

if __name__ == '__main__': # если данный модуль будет открываться сам, то он будет открыватся не посредством импорта в другой модуль, а будет запускаться самостоятельно
    executor.start_polling(dp, skip_updates=True)
