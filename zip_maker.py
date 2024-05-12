import os
from zipfile import ZipFile
from fpdf import FPDF


# Обработка QR кодов
def hex8b(qr_name: str) -> str:
    return qr_name[:-4].upper()


def dec3b(qr_name: str) -> str:
    return str(int(qr_name[-10:-4], 16))


def fac_code(qr_name: str) -> str:
    fc = str(int(hex8b(qr_name)[-6:-4], 16))
    code = str(int(hex8b(qr_name)[-4:], 16))
    return f"{fc},{code}"


def generate_qr_list(qrs: list, path: str) -> list:
    data = list()
    for qr in qrs:
        data.append([f"{path}/{qr}",
                     f"HEX 8b: {hex8b(qr).upper()}",
                     f"DEC 3b: {dec3b(qr)}",
                     f"FC 3b: {fac_code(qr)}"])
    return data


# Генерация PDF
# Подготовка новой страницы к заполнению
def newpage(pdf: FPDF):
    pdf.add_page()
    pdf.set_x(20)
    pdf.image("https://proxway-ble.ru/images/logo.svg", w=50)
    pdf.set_xy(140, 10)
    pdf.set_font("Helvetica", size=16)
    pdf.multi_cell(w=60, text="https://proxway-ble.ru\n8 800 700-19-57\ninfo@proxway-ble.ru")
    pdf.set_font("Helvetica", size=6.3)


# Отрисовка ячейки с QR кодом и расшифровкой
def draw_cell(pdf: FPDF, x: int, y: int, qr: list):
    pdf.set_xy(x, y)
    pdf.image(qr[0], w=30)
    pdf.multi_cell(w=31, text=f"{qr[1]}\n{qr[2]}\n{qr[3]}")


def generate_table(pdf: FPDF, data: list):
    step_y = 30  # стартовый отступ от верхнего края
    step_x = 20  # стартовый отступ от бокового края
    step = 1  # считаем до 5х - кол-во столбцов
    for elem in data:
        draw_cell(pdf, step_x, step_y, elem)
        if step != 5:
            step_x += 37
            step += 1
        else:
            if (data.index(elem) + 1) % 30 == 0 and (data.index(elem) + 1) != len(data):
                newpage(pdf)
                step_y = 30  # стартовый отступ от верхнего края
                step_x = 20  # стартовый отступ от бокового края

            else:
                step_x = 20
                step_y += 42
            step = 1  # начинаем счет до 5х заново


def do_pdf(data: list, path_save: str) -> str:
    pdf = FPDF("P", "mm", "A4")
    newpage(pdf)
    generate_table(pdf, data)
    name_pdf = f"{path_save}/_PW-ID_{data[0][0][-10:-4].upper()}-{data[-1][0][-10:-4].upper()}.pdf"
    pdf.output(name_pdf)
    print(f"PDF файл PW-ID_{data[0][0][-10:-4].upper()}-{data[-1][0][-10:-4].upper()}.pdf сгенерирован")
    return f"PW-ID_{data[0][0][-10:-4].upper()}-{data[-1][0][-10:-4].upper()}"


def zip_unpuck(zip_file_name):
    with ZipFile(zip_file_name, "r") as zip:
        zip.extractall()
    return zip_file_name[:-4]


def zip_puck(name, path) -> str:
    files = os.listdir(path)
    with ZipFile(f"{name}.zip", "w") as zip:
        for file in files:
            zip.write(filename=f"{path}/{file}", arcname=file)
    return f"{name}.zip"


def do_zip_with_pdf(zip_file_name: str) -> str:
    '''
    Функция принимающая имя входного zip файла, формирующая из него новый с pdf и возвращающая имя нового архива
    :param zip_file_name: имя входного архива
    :return: имя выходного архива
    '''
    # Распакуем полученный архив
    TEMP_FOLDER = zip_unpuck(zip_file_name)

    # Создадим список файлов в папке, проверим что они все изображения
    files = sorted(os.listdir(TEMP_FOLDER))
    for item in files:
        if item[-4:] != ".png": return "BAD"

    # Создаем список с данными для генерации PDF
    data = generate_qr_list(files, TEMP_FOLDER)

    new_zip_name = do_pdf(data, TEMP_FOLDER)
    res = zip_puck(new_zip_name, TEMP_FOLDER)

    # Подчистим хвосты
    os.remove(zip_file_name)
    for item in os.listdir(TEMP_FOLDER):
        os.remove(f"{TEMP_FOLDER}/{item}")
    os.rmdir(TEMP_FOLDER)

    return res
