import os

result = []
pwd = os.getcwd()
os.chdir(pwd + "/Города")
# for filename in os.listdir():
#     fh = open(filename, "r", encoding="utf-8")
#     for line in fh:
#         result.append(line.strip())

unmatched = []

filenames = ['абв.tsv', 'где.tsv', 'ёжзий.tsv', 'клм.tsv', 'ноп.tsv', 'рсту.tsv', 'фхц.tsv', 'чшщыэюя.tsv']
fh = open(filenames[0], "r", encoding="utf-8")
dictionary = dict()
for line in fh:
    line = line.strip()
    line = line.split("\t")
    location = line[1]
    value = line[0].split("resource/")[1]
    value = value.strip("\"")
    if "(" in location:
        if "(город)" in location:
            location = location.split("(")
            city_name = location[0].lower().strip().strip("\")")
            dictionary[city_name] = value
            dictionary[city_name + ",город"] = value
        elif "(город," in location:
            location = location.split("(город, ")
            city_name = location[0].lower().strip().strip("\")")
            dictionary[city_name] = value
            dictionary[city_name + ",город"] = value
            dictionary[city_name + "," + location[1].lower()[:-1]] = value
        else:
            city_name = location.split("(")[0].lower().strip("\") ")
            rest = location.split("(")[1].strip("\")")
            if rest[0].isupper() and len(rest.split()) == 1:
                dictionary[city_name] = value
                dictionary[city_name + "," + rest.lower()] = value
            elif rest[0].isupper() and len(rest.split()) > 1:
                if "—" not in rest:
                    dictionary[city_name] = value
                    dictionary[city_name + "," + rest.split(" ")[1].lower()] = value
                    dictionary[city_name + "," + rest.lower()] = value
                else:
                    unmatched.append(city_name + " " + rest + "\t" + value)
                    # dictionary[city_name] = value
                    # dictionary[city_name + " папуа новая гвинея"] = value
                    # dictionary[city_name + " новая гвинея"] = value
            elif "значения" in rest:
                dictionary[city_name] = value
            elif len(rest.split(" ")) == 1:
                dictionary[city_name] = value
                dictionary[rest + " " + city_name] = value
            else:
                if len(rest.split(" ")) == 2:
                    if rest.split()[0].endswith("й"):
                        unmatched.append(city_name + "," + rest + "\t" + value)
                        # dictionary[city_name] = value
                        # dictionary[city_name + " " + rest.split()[1]] = value
                        # dictionary[city_name + " " + rest] = value
                    else:
                        dictionary[city_name] = value
                        dictionary[city_name + "," + rest.split()[0].strip(",")] = value
                        dictionary[city_name + "," + rest.split()[0].strip(",") + " " + rest.split()[1].lower()] = value
                else:
                    unmatched.append(city_name + " " + rest + "\t" + value)
                    # dictionary[city_name] = value
                    # dictionary[city_name + " лондон"] = value
                    # dictionary[city_name + " район"] = value
                    # dictionary[city_name + " район лондон"] = value
    else:
        if len(location.split()) > 2:
            unmatched.append(location.lower() + "\t" + value)
        else:
            dictionary[location.lower().strip('\"')] = value

with open("Locations from DBPedia-1.txt", 'w') as fw:
    for key in dictionary:
        # print(key + "\t" + dictionary[key])
        fw.write(key + "\t" + dictionary[key] + "\n")

with open("Unmatched.txt", "w") as unm:
    for u in unmatched:
        unm.write(u + "\n")