import os
from pymystem3 import Mystem
from SPARQLWrapper import SPARQLWrapper, JSON
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
PWD = os.getcwd()

result = []


def open_pattern(pattern_name):
    os.chdir("/Users/ulyanasidorova/Learning/Course_Work/untitled/PATTERNS_LIBRARY")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    os.chdir(PWD)
    return pattern

print(PWD)


def ask_query(query_pattern, variable="concept"):
    assert not variable.startswith("?")
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result[variable]["value"])
    return final

synonyms = ["гора", "горный ряд", "сопка", "вулкан"]


pattern = open_pattern("country")
count = 0
with open("Регионы России.tsv", 'r', encoding="utf-8") as f:
    for line in f:
        line = line.split("\t")
        assert len(line) == 3
        line = [l.strip("\"") for l in line]
        # print(line)

        value, location_name, info = [l.strip() for l in line]

        normalized = ""
        lemmatized = ""
        descriptors = []
        #
        # if region:
        #     # print(region)
        #     region = m.lemmatize(region)
        #     region = "".join(region).strip()
        #     if not region.startswith("http"):
        #         region = region.replace(" ", "_")
        #         region = "http://dbpedia.org/resource/" + region
        #     pat = pattern.replace("SUBJECT", region)
        #     try:
        #         res = ask_query(pat, variable="name")
        #     except Exception as err:
        #         print(err)
        #         print(pat)
        #     if res:
        #         descriptors.append(res[0])
        #     print(location_name, res)
        #
        if not "(" in location_name:
            normalized = location_name
            lemmatized = m.lemmatize(location_name)
            lemmatized = "".join(lemmatized).strip()
            # print(lemmatized)
        if "(" in location_name:
            # print(location_name)
            location_name = location_name.split("(")
            normalized = location_name[0]
            lemmatized = m.lemmatize(normalized)
            lemmatized = "".join(lemmatized).strip()

            rest = location_name[1].strip(")")
            rest = m.lemmatize(rest)
            rest = "".join(rest).strip()
            # print(normalized, rest)
            for s in synonyms:
                if s in rest:
                    descriptors.append(s)
            for s in synonyms:
                rest = rest.replace(s, "").strip()

            if "," in rest:
                rest = rest.split(",")

                for r in rest:
                    if r:
                        descriptors.append(r)
            else:
                if rest:
                    descriptors.append(rest)
        if "гора" not in descriptors:
            descriptors.append("гора")

            print(normalized, descriptors)

        #
        print(info)
        if "_of_" in info:
            info = info.split("_of_")[1].strip("\"")
            # print(info)
            info = info.lstrip("the_")

            info = info.replace("Chuvash_Republic", "Chuvashia")
            info = info.replace("Udmurt_Republic", "Udmurtia")
            info = info.replace("Republic_of_Buryatia", "Buryatia")
            info = info.replace("Republic_of_Adygea", "Adygea")
            info = info.replace("Republic_of_Dagestan", "Dagestan")
            info = info.replace("Mari_El_Republic", "Mari_El")
            info = info.replace("Republic_of_Mordovia", "Mordovia")

            pat = pattern.replace("SUBJECT", "http://dbpedia.org/resource/" + info)
            res = ask_query(pat, variable = "name")
            if res:
                res = m.lemmatize(res[0])
                res = "".join(res).strip()
                descriptors.append(res)
                # print(normalized, res)
        else:
            if info.endswith("_basin\""):
                info = info.split("Category:")[1].strip("\"")
                info = info[:-6]
                pat = pattern.replace("SUBJECT", "http://dbpedia.org/resource/" + info + "_River")
                res = ask_query(pat, variable="name")
                if res:
                    res = res[0].split("(")[0]
                    res = m.lemmatize(res)
                    res = "".join(res).strip()
                    descriptors.append(res)

            else:
                info = info.split("Category:")[1]
                info = info.split("_")
                if len(info) == 1:
                    pat = pattern.replace("SUBJECT", "http://dbpedia.org/resource/" + info[0].strip("\""))
                    res = ask_query(pat, variable="name")
                    if res:
                        res = m.lemmatize(res[0])
                        res = "".join(res).strip()
                        descriptors.append(res)
        #
        print(normalized, descriptors)
        string = lemmatized + "," + ",".join(descriptors) + "," + normalized + "\t" + value
        result.append(string)
        print(string)
#
#             if rest.startswith("район"):
#                 rest = rest.split(" ")
#                 rest = ",".join(rest)
#             rest = rest.split(",")
#             for r in rest:
#                 descriptors.append(r)
#         region = m.lemmatize(region)
#         region = "".join(region).strip()
#         info = info.split("resource/Category:")[1]

#         if "Districts" in info:
#             info = info.split("Districts_of_")[1]
#             info = info[:-2]
#             if info.startswith("the"):
#                 info = info[4:]
#             pat = pattern.replace("SUBJECT", info)
#             res = ask_query(pat, variable = "name")
#             if res:
#                 res = m.lemmatize(res[0])
#                 res = "".join(res).strip()
#                 descriptors.append(res)
#             else:
#                 print(info, res)
#         if "Cities_and_towns_in_" in info:
#             info = info[20:]
#             if info.startswith("the"):
#                 info = info[4:]
#             info = info[:-2]
#             pat = pattern.replace("SUBJECT", info)
#             res = ask_query(pat, variable = "name")
#             if res:
#                 res = m.lemmatize(res[0])
#                 res = "".join(res).strip()
#                 descriptors.append(res)
#         if "Urban-type_settlements_in_" in info:
#             info = info[26:-2]
#             if info.startswith("the"):
#                 info = info[4:]
#             pat = pattern.replace("SUBJECT", info)
#             res = ask_query(pat, variable = "name")
#             if res:
#                 res = m.lemmatize(res[0])
#                 res = "".join(res).strip()
#                 descriptors.append(res)
#         if "Rural_localities_in_" in info and ",_" not in info:
#             info = info[20:-2]
#             if info.startswith("the"):
#                 info = info[4:]
#             pat = pattern.replace("SUBJECT", info)
#             res = ask_query(pat, variable = "name")
#             if res:
#                 res = m.lemmatize(res[0])
#                 res = "".join(res).strip()
#                 descriptors.append(res)
#         if "Populated_places_of_" in info:
#             info = info[20:-2]
#             info = info.replace("_Russia", "")
#             pat = pattern.replace("SUBJECT", info)
#             res = ask_query(pat, variable = "name")
#             if res:
#                 res = m.lemmatize(res[0])
#                 res = "".join(res).strip()
#                 descriptors.append(res)
#         descriptors = list(set(descriptors))
#         # print(normalized, lemmatized, value, descriptors)


with open("PARSED.txt", "w") as r:
    for line in result:
        r.write(line + "\n")