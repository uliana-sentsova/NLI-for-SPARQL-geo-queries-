import os
from pymystem3 import Mystem
from SPARQLWrapper import SPARQLWrapper, JSON
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
PWD = os.getcwd()

result = []


def open_pattern(pattern_name):
    os.chdir("/Users/ulyanasidorova/Documents/Course_Work/untitled/Patterns")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    os.chdir(PWD)
    return pattern


def ask_query(query_pattern, variable="concept"):
    assert not variable.startswith("?")
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result[variable]["value"])
    return final


pattern = open_pattern("country")
count = 0
with open("Russian.tsv", 'r', encoding="utf-8") as f:
    for line in f:
        line = line.split("\t")
        assert len(line) == 4
        city_name, value, region, info = [l.strip("\"") for l in line]

        normalized = ""
        lemmatized = ""
        descriptors = []

        if region:
            region = m.lemmatize(region)
            region = "".join(region).strip()
            descriptors.append(region)

        if not "(" in city_name and not "," in city_name:
            normalized = city_name
            lemmatized = m.lemmatize(city_name)
            lemmatized = "".join(lemmatized).strip()
        if "(" in city_name:
            city_name = city_name.split("(")
            normalized = city_name[0]
            lemmatized = m.lemmatize(normalized)
            lemmatized = "".join(lemmatized).strip()
            rest = city_name[1].strip(")")
            rest = m.lemmatize(rest)
            rest = "".join(rest).strip()
            if rest.startswith("район"):
                rest = rest.split(" ")
                rest = ",".join(rest)
            rest = rest.split(",")
            for r in rest:
                descriptors.append(r)
        region = m.lemmatize(region)
        region = "".join(region).strip()
        info = info.split("resource/Category:")[1]
        info = info.replace("Chuvash_Republic", "Chuvashia")
        info = info.replace("Udmurt_Republic", "Udmurtia")
        info = info.replace("Republic_of_Buryatia", "Buryatia")
        info = info.replace("Republic_of_Adygea", "Adygea")
        info = info.replace("Republic_of_Dagestan", "Dagestan")
        info = info.replace("Mari_El_Republic", "Mari_El")
        info = info.replace("Republic_of_Mordovia", "Mordovia")
        if "Districts" in info:
            info = info.split("Districts_of_")[1]
            info = info[:-2]
            if info.startswith("the"):
                info = info[4:]
            pat = pattern.replace("SUBJECT", info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
            else:
                print(info, res)
        if "Cities_and_towns_in_" in info:
            info = info[20:]
            if info.startswith("the"):
                info = info[4:]
            info = info[:-2]
            pat = pattern.replace("SUBJECT", info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
        if "Urban-type_settlements_in_" in info:
            info = info[26:-2]
            if info.startswith("the"):
                info = info[4:]
            pat = pattern.replace("SUBJECT", info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
        if "Rural_localities_in_" in info and ",_" not in info:
            info = info[20:-2]
            if info.startswith("the"):
                info = info[4:]
            pat = pattern.replace("SUBJECT", info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
        if "Populated_places_of_" in info:
            info = info[20:-2]
            info = info.replace("_Russia", "")
            pat = pattern.replace("SUBJECT", info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
        descriptors = list(set(descriptors))
        # print(normalized, lemmatized, value, descriptors)

        string = lemmatized + "," + ",".join(descriptors) + "," + normalized + "\t" + value
        result.append(string)
        print(string)

with open("ONTO_Russian.txt", "w") as r:
    for line in result:
        r.write(line + "\n")
