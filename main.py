import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile

from config import *
from translator import *

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def file_handler(message: types.Document):
    sent_message = await message.reply(
        text="_Идёт перевод файла..._🧐", parse_mode="Markdown"
    )
    file_name = str(message.document.file_name)[:-4] + "_" + str(message.from_id) + ".pdf"
    original_path = "saved/{}".format(file_name)
    translated_path = "to_send/{}".format(file_name)
    await message.document.download(destination_file=original_path)
    translate_pdf(
        original_path=original_path,
        translated_path=translated_path,
        font_size=FONT_SIZE,
        max_line_length=MAX_LINE_LENGTH,
    )

    doc_count = get_documentc_count(translated_path)
    if doc_count > 1:
        await message.reply(
            text="Файл слишком большой! Он будет разбит на *"
                 + str(doc_count)
                 + "* части 😊",
            parse_mode="Markdown",
        )
        file_names = split(translated_path, doc_count)
        doc_num = 1
        for file in file_names:
            await message.reply_document(
                document=InputFile(file),
                caption="Переведённый файл: "
                        + str(doc_num)
                        + " / "
                        + str(len(file_names))
                        + " ✅",
            )
            doc_num += 1
            os.remove(file)
    else:
        await message.reply_document(
            document=InputFile(translated_path), caption="Переведённый файл ✅"
        )
    os.remove(original_path)
    os.remove(translated_path)
    await sent_message.delete()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        text="*PDF Translator* - бот для перевода PDF-книг на русский язык 📖\n"
             "Просто отправьте файл, который хотите перевести! 🥸 \n\n_© @onepantsu_",
        parse_mode="Markdown",
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
