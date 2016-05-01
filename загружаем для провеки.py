import os

pwd = os.getcwd()
os.chdir(pwd + "/Города")

filenames = ['абв.tsv', 'где.tsv', 'ёжзий.tsv', 'клм.tsv', 'ноп.tsv', 'рсту.tsv', 'фхц.tsv', 'чшщыэюя.tsv']
fh = open(filenames[0], "r", encoding="utf-8")

result = []
ambiguos = []
for line in fh:
    line = line.strip()
    line = line.split("\t")
    location = line[1]
    location = location.split("(")[0].strip()
    result.append(location.lower())

def check_ambiguity(city_name):
    if result.count(city_name) > 1:
        return True
    else:
        return False


print(check_ambiguity("агра"))
print(check_ambiguity("вашингтон"))
print(check_ambiguity("агно"))