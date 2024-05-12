import telebot, os, dotenv
from zip_maker import do_zip_with_pdf

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def say_hello(message):
    bot.send_message(message.chat.id, "Hellow everybody!\nОтправляем полученный от сервера идентификаторов архив с QR, в ответ получаем архив с PDF и исходными QR")


@bot.message_handler(content_types=["document"])
def get_users_file(message):
    if message.document.file_name[-4:] == ".zip":
        downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
        with open(f"{message.document.file_name}", "wb") as file:
            file.write(downloaded_file)
        result = do_zip_with_pdf(f"{message.document.file_name}")
        if result == "BAD":
            say_not_understend(message)
            return None
        with open (result, "rb") as file:
            bot.send_document(message.chat.id, file)
        os.remove(result)
        bot.send_message(message.chat.id, "Nice!")
    else: say_not_understend(message)





@bot.message_handler(content_types=["text"])
def say_not_understend(message):
    bot.send_message(message.chat.id, "Что то не то.\n Давай еще разок объясню\nОтправляем полученный от сервера идентификаторов архив с QR, в ответ получаем архив с PDF и исходными QR")


if __name__ == '__main__':
    bot.infinity_polling()