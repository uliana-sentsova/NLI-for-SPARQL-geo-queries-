import os

result = []
pwd = os.getcwd()
os.chdir(pwd + "/Города")
# for filename in os.listdir():
#     fh = open(filename, "r", encoding="utf-8")
#     for line in fh:
#         result.append(line.strip())

filenames = ['абв.tsv', 'где.tsv', 'ёжзий.tsv', 'клм.tsv', 'ноп.tsv', 'рсту.tsv', 'фхц.tsv', 'чшщыэюя.tsv']
fh = open(filenames[0], "r", encoding="utf-8")
dictionary = dict()
for line in fh:
    line = line.strip()
    line = line.split("\t")
    location = line[1]
    value = line[0].split("resource/")[1]
    if "(город)" in location:
        location = location.split("(")
        city_name = location[0].lower().strip()
        dictionary[city_name] = value
        dictionary["город " + city_name] = value
        dictionary["г " + city_name] = value
    elif "(город," in location:
        location = location.split("(город, ")
        city_name = location[0].lower().strip()
        dictionary[city_name] = value
        dictionary["город " + city_name] = value
        dictionary[city_name + location[1].lower()[:-1]] = value
        dictionary["город " + city_name + location[1].lower()[:-1]] = value
    else:
        pass

for key in dictionary:
    print(key + ": " + dictionary[key])