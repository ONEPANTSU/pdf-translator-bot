import math
import os

import fitz
from fitz import Point, Rect
from googletrans import Translator


def translate_text(text):
    translator = Translator()
    max_length = 12500
    translated_text = ""
    iter_count = len(text) // max_length
    if len(text) % max_length != 0:
        iter_count += 1
    for i in range(iter_count):
        begin = i * max_length
        if i != iter_count - 1:
            end = i * max_length + max_length
        else:
            end = len(text)
        translated_text += translator.translate(
            text=text[begin:end], src="en", dest="ru"
        ).text
    return translated_text


def translate_pdf(original_path, translated_path, font_size=12, max_line_length=50):
    pdf = fitz.open(original_path)
    new_pdf = fitz.open()
    new_pdf.new_page()
    pno = 0
    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        image_list = page.get_images()
        text = page.get_text()
        if len(text) > 0:
            new_pdf.insert_page(pno)
            new_page = new_pdf.load_page(pno)
            translated = translate_text(text)
            new_translated = translated
            bias = 0
            line_len = 0
            for char_index in range(len(translated)):
                line_len += 1
                if line_len == max_line_length:
                    new_translated = (
                        new_translated[: char_index + bias]
                        + "\n"
                        + new_translated[char_index + bias :]
                    )
                    bias += 1
                    line_len = 0
                if translated[char_index] == "\n":
                    line_len = 0
            new_page.insert_font(fontname="tnr", fontfile="fonts/Times New Roman.ttf")
            new_page.insert_text(
                Point(20, 20), new_translated, fontname="tnr", fontsize=font_size
            )
            pno += 1
        for image in image_list:
            new_pdf.insert_page(pno)
            new_page = new_pdf.load_page(pno)
            xref = image[0]
            filename = f"images/{xref}.png"
            pix = fitz.Pixmap(pdf, xref)
            if pix.n >= 5:
                pix = fitz.open(fitz.csRGB, pix)
            pix.save(filename)
            new_page.insert_image(
                rect=Rect(Point(0, 0), Point(618, 957)), filename=filename
            )
            os.remove(filename)
            pno += 1
        new_pdf.save(translated_path)

def get_documentc_count(original_path):
    file_size = os.path.getsize(original_path)
    documents_count = math.ceil(file_size / 50000000)
    return documents_count
def split(original_path, documents_count, font_size=12):
    file_names = []
    pdf = fitz.open(original_path)
    new_pdf = fitz.open()
    new_pdf.new_page()
    pno = 0
    pages_count = pdf.page_count / documents_count
    num = 1
    for page_num in range(pdf.page_count):
        if pno >= pages_count:
            pno = 0
            file_name = original_path[:-4] + "_" + str(num) + ".pdf"
            file_names.append(file_name)
            new_pdf.save(file_name)
            num += 1
            new_pdf = fitz.open()
        page = pdf.load_page(page_num)
        image_list = page.get_images()
        text = page.get_text()
        if len(text) > 0:
            new_pdf.insert_page(pno)
            new_page = new_pdf.load_page(pno)
            new_page.insert_font(fontname="tnr", fontfile="fonts/Times New Roman.ttf")
            new_page.insert_text(
                Point(20, 20), text, fontname="tnr", fontsize=font_size
            )
            pno += 1
        for image in image_list:
            new_pdf.insert_page(pno)
            new_page = new_pdf.load_page(pno)
            xref = image[0]
            filename = f"images/{xref}.png"
            pix = fitz.Pixmap(pdf, xref)
            if pix.n >= 5:
                pix = fitz.open(fitz.csRGB, pix)
            pix.save(filename)
            new_page.insert_image(
                rect=Rect(Point(0, 0), Point(618, 957)), filename=filename
            )
            os.remove(filename)
            pno += 1
    file_name = original_path[:-4] + "_" + str(num) + ".pdf"
    file_names.append(file_name)
    new_pdf.save(file_name)
    return file_names