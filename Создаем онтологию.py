import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# Данный файл 1) обрабатывает уникальные локации, 2) добавляет в итоговый файл строку
# "локация, дескриптор1, дескриптор2, ...". В отличие от файла "Обработка словарей локацией", данный файл
# не записывает одну и ту же локацию в различные строки. Результат записывается в файл "ONTOLOGY.txt",
# который можно будет использовать в качестве онтологии и для анализа запроса.

# TODO: запустить с начала

result = []
pwd = os.getcwd()
os.chdir(pwd + "/Ontology")
# for filename in os.listdir():
#     fh = open(filename, "r", encoding="utf-8")
#     for line in fh:
#         result.append(line.strip())


def check_ambiguity(city_name):
    if checking.count(city_name) > 1:
        return True
    else:
        return False

pwd = os.getcwd()

def open_pattern(pattern_name):
    pwd = os.getcwd()
    os.chdir("/Users/ulyanasidorova/Documents/Course_Work/untitled/Patterns")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    os.chdir(pwd)
    return pattern

def make_query_to_DB(subject, pattern, predicate):
    query_pattern = re.sub("SUBJECT", subject, pattern)
    query_pattern = re.sub("PREDICATE", predicate, query_pattern)
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result["name"]["value"])
    # for f in final:
    #     print(f)
    if final:
        return final
    else:
        query_pattern = re.sub('\ \"ru\"\ ', "\"en\"", query_pattern)
        sparql.setQuery(query_pattern)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        final = []
        for result in results["results"]["bindings"]:
            final.append(result["name"]["value"])
        if final:
            return final
        else:
            return ""

unmatched = []

filenames = ['Реки.tsv', 'где.tsv', 'ёжзий.tsv', 'клм.tsv', 'ноп.tsv', 'рсту.tsv', 'фхц.tsv', 'чшщыэюя.tsv']
filename = filenames[0]


pattern5 = open_pattern("pattern5")


checking = []
fh = open(filename, "r", encoding="utf-8")
for line in fh:
    line = line.strip()
    line = line.split("\t")
    location = line[0]
    # location = location.split("(")[1].strip()
    checking.append(location.lower())


fh = open(filename, "r", encoding="utf-8")
dictionary = dict()
for l in fh:
    line = l.strip()
    line = line.split("\t")
    location = line[0]
    value = line[1].split("resource/")[1]
    value = value.strip("\"")
    country = ""
    district = ""
    country = make_query_to_DB(value, pattern5, "dbo:country")
    if not country:
        unmatched.append(l + "\n")
    if not country:
        country = make_query_to_DB(value, pattern5, "dbo:sourceRegion")
    if country:
        country = country[0].lower()
    else:
        country = ""
    print(country, location)
    district = make_query_to_DB(value, pattern5, "dbp:city")
    if not district:
        district = ""
    else:
        district = ",".join(district).lower()
    print(district, location)
    if check_ambiguity(location.split("(")[0].strip().lower()):
        # print(location.split("(")[0].strip().lower())
        with open("Ambiguos_Countries.txt", 'a') as k:
            k.write(l)
        continue
    if "(" in location:
        if "(река)" in location:
            location = location.split("(")
            city_name = location[0].lower().strip().strip("\")")
            # dictionary[city_name] = value
            dictionary[city_name + ",река," + country + "," + district] = value
        elif("(приток") in location:
            city_name = location[0].lower().strip().strip("\")")
            dictionary[city_name + ",река," + country + "," + district] = value
        elif "(река," in location:
            location = location.split("(река, ")
            city_name = location[0].lower().strip().strip("\")")
            # dictionary[city_name] = value
            dictionary[city_name + ",река" + "," + location[1].lower()[:-1] + "," + country + "," + district] = value
        else:
            city_name = location.split("(")[0].lower().strip("\") ")
            rest = location.split("(")[1].strip("\")")
            if rest[0].isupper() and len(rest.split()) == 1:
                # dictionary[city_name] = value
                dictionary[city_name + "," + rest.lower() + ","+ country + "," + district] = value
            elif rest[0].isupper() and len(rest.split()) > 1:
                if "—" not in rest:
                    # dictionary[city_name] = value
                    dictionary[city_name + "," + rest.split(" ")[1].lower()+ "," + rest.lower()+ ","
                               + country  + "," + district] = value
                    # dictionary[city_name + "," + rest.lower()] = value
                else:
                    unmatched.append(city_name + " " + rest + "," + country  + "," + district + "\t" + value)
                    # dictionary[city_name] = value
                    # dictionary[city_name + " папуа новая гвинея"] = value
                    # dictionary[city_name + " новая гвинея"] = value
            elif "значения" in rest:
                dictionary[city_name] = value
            elif len(rest.split(" ")) == 1:
                # dictionary[city_name] = value
                dictionary[city_name + "," + rest + "," + country] = value
            else:
                if len(rest.split(" ")) == 2:
                    if rest.split()[0].endswith("й"):
                        unmatched.append(city_name + ",река," + rest + "," + country + "," + district + "\t" + value)
                        # dictionary[city_name] = value
                        # dictionary[city_name + " " + rest.split()[1]] = value
                        # dictionary[city_name + " " + rest] = value
                    else:
                        # dictionary[city_name] = value
                        # dictionary[city_name + "," + rest.split()[0].strip(",")] = value
                        dictionary[city_name + ",река," + rest.split()[0].strip(",") + "," + rest.split()[1].lower() + ","
                                   + country + "," + district] = value
                else:
                    unmatched.append(city_name + " " + rest + "," + country + "," + district + "\t" + value)
                    # dictionary[city_name] = value
                    # dictionary[city_name + " лондон"] = value
                    # dictionary[city_name + " район"] = value
                    # dictionary[city_name + " район лондон"] = value
    else:
        if len(location.split()) > 2:
            unmatched.append(location.lower() + "," + country + "," + district + "\t" + value)
        else:
            dictionary[location.lower().strip('\"') + "," + country + "," + district] = value


with open("ONTOLOGY_Rivers.txt", 'w') as fw:
    for key in dictionary:
        # print(key + "\t" + dictionary[key])
        fw.write(key + "\t" + dictionary[key] + "\n")

for u in unmatched:
    print(u)
with open("Unmatched_Countries.txt", "a") as unm:
    for u in unmatched:
        unm.write(u + "\n")

