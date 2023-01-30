import json
import tkinter as tk
from tkinter import ttk
from fuzzywuzzy import fuzz

path = "C:/Users/ahyil/Desktop/Coding/Limit_project/final.json"
global input_text
global selected_option
import pandas as pd

input_text = "GÖKÇE NERGİS"
def main():
    new_student = []
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
        for i in data:
            if fuzz.ratio(i["Name"], input_text) > 80:
                for attribute in i:
                    if attribute != "Name" and attribute != "ID" and attribute != "Class":
                        if 'AYT' in attribute:
                            filtered_data = [i for i in data if fuzz.ratio(i["Name"], input_text) > 80]
                            print(attribute, ":", i[attribute])
                            df = pd.DataFrame(filtered_data)
                            df.to_excel('file_name.xlsx', index=False)



if __name__ == '__main__':
    main()