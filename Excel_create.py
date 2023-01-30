import os
import json
import pandas as pd
from fuzzywuzzy import fuzz

path = "C:/Users/ahyil/Desktop/Coding/Limit_project"
global every_student
every_student = []

def convert_to_excel(database):
    data = []
    for item in database:
        for exam in item:
            row = {}
            if 'TYT' in exam :
                for value in item[exam]:
                    row[value] = item[value]
                data.append(row)
    df = pd.DataFrame(data)
    df.to_excel("exam_results.xlsx", index=False)


def main():
    newcount = 0
    dupecount = 0
    highest_ratio = 0
    found_flag = False
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(path + "/" + filename, encoding="utf-8") as file:
                data = json.load(file)
                for i in data:
                    highest_ratio = 0
                    for j in every_student:
                        highest_ratio = max(highest_ratio, fuzz.ratio(i["Name"], j["Name"]))
                        if fuzz.ratio(i["Name"], j["Name"]) > 80 and found_flag == False:
                            print("This student is already in the list " , j["Name"] , "in file " , filename, "and" , i["Name"] , "with ratio " , highest_ratio)
                            dupecount += 1
                            i["Name"] = j["Name"]
                            if i["id-num"] != "123456789":
                                j["id-num"] = i["id-num"]
                            found_flag = True
                    if found_flag == False:
                        print("New " , i["Name"] , "in file " , filename, "with ratio " , highest_ratio)
                        newcount += 1
                        every_student.append(i)
                    found_flag = False
    print("New count: " , newcount)
    print("Duplicate count: " , dupecount)
    convert_to_excel(every_student)

if __name__ == '__main__':
    main()
    with open("final.json", "w", encoding="utf-8") as outfile:
        json.dump(every_student, outfile, indent=4, ensure_ascii=False)
