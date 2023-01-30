import tkinter as tk
import PyPDF2
import json
import re
from tkinter import ttk
from tkinter import filedialog

from fuzzywuzzy import fuzz

global file_path
global save_location
global selection
global type_of_thingie
global ea_student_data
global sp_student_data
global sz_student_data
global all_student_data
all_student_data = []
ea_student_data = []
sp_student_data = []
sz_student_data = []


def choose_pdf_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes = (("PDF files", "*.pdf"), ("All files", "*.*")))

def choose_save_location():
    global save_location
    save_location = filedialog.askdirectory()

def parse_okul_pdf():
    global selection
    number_of_changes = 0
    old_changes = 0
    exam_type = None
    mostprobable_count_for_exam = 0
    mostprobable_name_for_exam = ""
    selection = None
    limittype = False
    todertype = False
    input_text = textbox.get()
    found_flag = False
    global all_student_data
    global ea_student_data
    global sp_student_data
    global sz_student_data
    global type_of_thingie
    type_of_thingie = "some"
    with open(file_path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        for page in pdf.pages:
            if 'SINAV SONUÇ BELGESİ' in page.extract_text():
                break
            for line in page.extract_text().split("\n"):
                if 'Limit' in line:
                    limittype = True
                    todertype = False
                if 'TYT' in line:
                    exam_type = "tyt"
                elif 'AYT' in line:
                    exam_type = "ayt"
                if limittype:
                    if 'Sınıf Deneme' in line:
                        number_of_changes += 1
                        selection = "limit-sınıf"
                    if 'TYT' in line and 'PuanTYT' not in line:
                        number_of_changes += 1
                        selection = "limit-tyt"
                    if 'AYT' in line and 'PuanAYT' not in line:
                        number_of_changes += 1
                        selection = "limit-ayt"
                    if 'LGS' in line:
                        number_of_changes += 1
                        selection = "limit-lgs"
                elif 'TÖDER' in line:
                    number_of_changes += 1
                    todertype = True
                    limittype = False
                    selection = "toder-" + exam_type
                #if exam_type initialized
                if not selection is None:
                    if number_of_changes > old_changes:
                        print(mostprobable_name_for_exam , " " , selection , " " , mostprobable_count_for_exam)
                        if mostprobable_name_for_exam != selection:
                            if mostprobable_count_for_exam == 0:
                                mostprobable_name_for_exam = selection
                                mostprobable_count_for_exam = 1
                            else:
                                mostprobable_count_for_exam -= 1
                        else:
                            mostprobable_count_for_exam += 1
                        old_changes = number_of_changes
    selection = mostprobable_name_for_exam
    with open(file_path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        for page in pdf.pages:
            if 'SINAV SONUÇ BELGESİ' in page.extract_text():
                break
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                if "Eşit Ağrlık Puana Göre Sınav Sonuç Listesi" in line:
                    type_of_thingie = "EA"
                if "Sayısal Puana Göre Sınav Sonuç Listesi" in line:
                    type_of_thingie = "SP"
                if "Sözel Puana Göre Sınav Sonuç Listesi" in line:
                    type_of_thingie = "Sözel"
                parse_student_data(line)
    all_student_data = sp_student_data
    for i in ea_student_data:
        for j in all_student_data:
            if fuzz.ratio(i["Name"], j["Name"]) > 99 :
                j[input_text].update(i[input_text])
                i[input_text].update(j[input_text])
                found_flag = True
        if not found_flag:
            all_student_data.append(i)
        found_flag = False
    for i in sz_student_data:
        for j in all_student_data:
            if fuzz.ratio(i["Name"], j["Name"]) > 99 :
                i[input_text].update(j[input_text])
                j[input_text].update(i[input_text])
                found_flag = True
        if not found_flag:
            all_student_data.append(i)
        found_flag = False
    '''    
    with open(save_location + '/' + input_text + 'ea_student_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(ea_student_data, outfile, indent=4, ensure_ascii=False)
    with open(save_location + '/' + input_text + 'sp_student_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(sp_student_data, outfile, indent=4, ensure_ascii=False)
    with open(save_location + '/' + input_text + 'sz_student_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(sz_student_data, outfile, indent=4, ensure_ascii=False)
    '''
    with open(save_location + '/' + input_text + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(all_student_data, outfile, indent=4, ensure_ascii=False)
    all_student_data = []
    ea_student_data = []
    sp_student_data = []
    sz_student_data = []

def more_than_two_numbers_after_comma(string):

    numbers = string.split(',')
    if len(numbers[1]) > 2 and 0 < len(numbers[0]) < 3 and (int(int(numbers[1]) / 10) == 0 or int(int(numbers[1]) / 10) == 25 or int(int(numbers[1]) / 10) == 50 or int(int(numbers[1]) / 10) == 75) and -5 < int(
            numbers[0]) < 40:
        return True

def parse_student_data(student_string):
    global all_student_data
    global type_of_thingie
    input_text = textbox.get()
    if selection == "limit-tyt":
        if "******" not in student_string:
            return
        data = student_string.split()
        for i in range(len(data)):
            if ',' in data[i]:
                if more_than_two_numbers_after_comma(data[i]):
                    if (data[i] != "0,000"):
                        print(data[i])
                        data[i] = data[i][:-1] + " " + data[i][-1:]
        student_string = " ".join(data)
        data = student_string.split()
        student_data = {
            'id-num': int(data[len(data) - 1]),
            'Name': " ".join(data[38:len(data) - 3]),
            'Class': ("12" if str(data[len(data) - 3][0]) == "1" else "Mezun"),
            input_text: {
                'Turkish-T': int(data[1]),
                'Turkish-N': float(data[2].replace(',', '.')),
                'Turkish-F': int(data[3]),
                'History-T': int(data[4]),
                'History-N': float(data[5].replace(',', '.')),
                'History-F': int(data[6]),
                'Geography-T': int(data[7]),
                'Geography-N': float(data[8].replace(',', '.')),
                'Geography-F': int(data[9]),
                'Philosophy-T': int(data[10]),
                'Philosophy-N': float(data[11].replace(',', '.')),
                'Philosophy-F': int(data[12]),
                'Religion-T': int(data[13]),
                'Religion-N': float(data[14].replace(',', '.')),
                'Religion-F': int(data[15]),
                'Selected-Philosophy-T': int(data[16]),
                'Selected-Philosophy-N': float(data[17].replace(',', '.')),
                'Selected-Philosophy-F': int(data[18]),
                'Physics-T': int(data[19]),
                'Physics-N': float(data[20].replace(',', '.')),
                'Physics-F': int(data[21]),
                'Chemistry-T': int(data[22]),
                'Chemistry-N': float(data[23].replace(',', '.')),
                'Chemistry-F': int(data[24]),
                'Biology-T': int(data[25]),
                'Biology-N': float(data[26].replace(',', '.')),
                'Biology-F': int(data[27]),
                'Math-T': int(data[28]),
                'Math-N': float(data[29].replace(',', '.')),
                'Math-F': int(data[30]),
                'Total-N': float(data[31].replace(',', '.')),
                'TYT-Puan': float(data[32].replace(',', '.')),
                #from 33 to 36 is sort
                'Sort': [int(data[33]), int(data[34]), int(data[35]),int(data[36])]
            }
        }
        sp_student_data.append(student_data)

    if selection == "limit-ayt":
        if "******" not in student_string:
            return
        data = student_string.split()
        if type_of_thingie == "EA":
            student_data = {
                'id-num': int(data[len(data) - 1]),
                'Name': " ".join(data[20:len(data) - 5]),
                'Class': ("12" if str(data[len(data) - 5][0]) == "1" else "Mezun"),
                input_text: {
                'Literature-T': int(data[0]),
                'Literature-N': float(data[1].replace(',', '.')),
                'Literature-F': int(data[2]),
                'History-T': int(data[3]),
                'History-N': float(data[4].replace(',', '.')),
                'History-F': int(data[5]),
                'Geography-T': int(data[6]),
                'Geography-N': float(data[7].replace(',', '.')),
                'Geography-F': int(data[8]),
                'Mathematics-T': int(data[9]),
                'Mathematics-N': float(data[10].replace(',', '.')),
                'Mathematics-F': int(data[11]),
                'TM-net': float(data[12].replace(',', '.')),
                'TM-points': float(data[13].replace(',', '.')),
                'sort': [int(data[14]), int(data[15]), int(data[16]), int(data[17]), int(data[18]), int(data[19])],
                'TYT-score': float(data[len(data) - 4].replace(',', '.')),
                'TYT-net': float(data[len(data) - 3].replace(',', '.'))
            }
            }
            ea_student_data.append(student_data)
        elif type_of_thingie == "SP":
            student_data = {
                'id-num': int(data[len(data) - 1]),
                'Name': " ".join(data[20:len(data) - 5]),
                'Class': ("12" if str(data[len(data) - 5][0]) == "1" else "Mezun"),
                input_text : {
                'Physics-T': int(data[0]),
                'Physics-N': float(data[1].replace(',', '.')),
                'Physics-F': int(data[2]),
                'Chemistry-T': int(data[3]),
                'Chemistry-N': float(data[4].replace(',', '.')),
                'Chemistry-F': int(data[5]),
                'Biology-T': int(data[6]),
                'Biology-N': float(data[7].replace(',', '.')),
                'Biology-F': int(data[8]),
                'Mathematics-T': int(data[9]),
                'Mathematics-N': float(data[10].replace(',', '.')),
                'Mathematics-F': int(data[11]),
                'MF-net': float(data[12].replace(',', '.')),
                'MF-points': float(data[13].replace(',', '.')),
                #'sort': [int(data[14]), int(data[15]), int(data[16]), int(data[17]), int(data[18]), int(data[19])],
                'TYT-score': float(data[len(data) - 4].replace(',', '.')),
                'TYT-net': float(data[len(data) - 3].replace(',', '.'))
                }
            }
            sp_student_data.append(student_data)
        elif type_of_thingie == "Sözel":
            for i in range(len(data)):
                if ',' in data[i]:
                    if more_than_two_numbers_after_comma(data[i]):
                        wrog_flag = True
                        data[i] = data[i][:-1] + " " + data[i][-1:]

            student_string = " ".join(data)
            data = student_string.split()
            if data[len(data) - 20] == "0,00" or "Tanımsız" in data[len(data) - 20]:
                data.pop(len(data) - 20)
                student_string = " ".join(data)
                data = student_string.split()
            student_data = {
                'id-num': int(data[len(data) - 1]),
                'Name': " ".join(data[17:len(data) - 20]),
                'Class': ("12" if str(data[len(data) - 20][0]) == "1" else "Mezun"),
                input_text :{'Literature-T': int(data[0]),
                'Literature-N': float(data[1].replace(',', '.')),
                'Literature-F': int(data[2]),
                'History-T': int(data[3]),
                'History-N': float(data[4].replace(',', '.')),
                'History-F': int(data[5]),
                'Geography-T': int(data[6]),
                'Geography-N': float(data[7].replace(',', '.')),
                'Geography-F': int(data[8]),
                'TS-net': float(data[9].replace(',', '.')),
                'TS-points': float(data[10].replace(',', '.')),
                #'sort': [int(data[11]), int(data[12]), int(data[13]), int(data[14]), int(data[15]), int(data[16])],
                'TYT-score': float(data[len(data) - 19].replace(',', '.')),
                'TYT-net': float(data[len(data) - 18].replace(',', '.')),
                'History-2-T': int(data[len(data) - 17]),
                'History-2-N': float(data[len(data) - 16].replace(',', '.')),
                'History-2-F': int(data[len(data) - 15]),
                'Geography-2-T': int(data[len(data) - 14]),
                'Geography-2-N': float(data[len(data) - 13].replace(',', '.')),
                'Geography-2-F': int(data[len(data) - 12]),
                'Philosopy-T': int(data[len(data) - 11]),
                'Philosopy-N': float(data[len(data) - 10].replace(',', '.')),
                'Philosopy-F': int(data[len(data) - 9]),
                'Religion-T': int(data[len(data) - 8]),
                'Religion-N': float(data[len(data) - 7].replace(',', '.')),
                'Religion-F': int(data[len(data) - 6]),
                'Selected-Philosophy-T': int(data[len(data) - 5]),
                'Selected-Philosophy-N': float(data[len(data) - 4].replace(',', '.')),
                'Selected-Philosophy-F': int(data[len(data) - 3])
                }
            }
            sz_student_data.append(student_data)
    elif selection == "toder-tyt":
        data = student_string.split()
        if len(data) < 15 or 'GENEL' in student_string:
            return
        student_data = {
            'id-num': 1234567890,
            'Name': " ".join(data[len(data):39:-1]),
            'Class': "12",
            input_text : {
                'Turkish-T': int(data[1]),
                'Turkish-F': int(data[2]),
                'History-T': int(data[3]),
                'History-F': int(data[4]),
                'Geography-T': int(data[5]),
                'Geography-F': int(data[6]),
                'Philosopy-T': int(data[7]),
                'Philosopy-F': int(data[8]),
                'Religion-T': int(data[9]),
                'Religion-F': int(data[10]),
                'Mathematics-T': int(data[11]),
                'Mathematics-F': int(data[12]),
                'Total-T': int(data[13]),
                'Total-F': int(data[14]),
                'Geometry-T': int(data[21]),
                'Geometry-F': int(data[22]),
                'Physics-T': int(data[23]),
                'Physics-F': int(data[24]),
                'Chemistry-T': int(data[25]),
                'Chemistry-F': int(data[26]),
                'Biology-T': int(data[27]),
                'Biology-F': int(data[28]),
                'Turkish-N': float(data[29].replace(',', '.')),
                'History-N': float(data[30].replace(',', '.')),
                'Geography-N': float(data[31].replace(',', '.')),
                'Philosopy-N': float(data[32].replace(',', '.')),
                'Religion-N': float(data[33].replace(',', '.')),
                'Mathematics-N': float(data[34].replace(',', '.')),
                'Geometry-N': float(data[35].replace(',', '.')),
                'Physics-N': float(data[36].replace(',', '.')),
                'Chemistry-N': float(data[37].replace(',', '.')),
                'Biology-N': float(data[38].replace(',', '.')),
                'Total-N': float(data[39].replace(',', '.'))
            }
        }
        sp_student_data.append(student_data)







root = tk.Tk()
root.title("Limit PDF Parser")
root.geometry('200x150')
choose_pdf_button = tk.Button(text="Choose PDF file", command=choose_pdf_file)
choose_pdf_button.pack()
choose_save_location_button = tk.Button(text="Choose save location", command=choose_save_location)
choose_save_location_button.pack()
textbox = tk.Entry(root)
textbox.pack()


# Create Combobox
n = tk.StringVar()
start = tk.Button(text="Start", command=parse_okul_pdf)
start.pack()
root.mainloop()
