import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
from pymystem3 import Mystem
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# ======================================

# LOCATION_DICTIONARY = dict()
# with open("RU-EN.txt", 'r', encoding="utf-8") as f:
#     for line in f:
#         LOCATION_DICTIONARY[line.split("\t")[0]] = line.strip().split("\t")[1]
#
# PROPERTIES = dict()
# with open("SUBJECT.txt", "r", encoding="utf-8") as g:
#     for line in g:
#         line = line.strip().split(",")
#         PROPERTIES[line[0]] = (line[1], "default")
#         # PROPERTIES[line[1]] = [l for l in line[0].split(",")]
#
# with open("FULL.txt", "r", encoding="utf-8") as g:
#     for line in g:
#         line = line.strip().split(",")
#         PROPERTIES[line[0]] = (line[1], "no_subject")
#
# with open("INFO.txt", "r", encoding="utf-8") as g:
#     for line in g:
#         line = line.strip().split(",")
#         PROPERTIES[line[0]] = (line[1], "info")
#
# with open("OBJECT.txt", "r", encoding="utf-8") as g:
#     for line in g:
#         line = line.strip().split(",")
#         PROPERTIES[line[0]] = (line[1], "object")

PWD = os.getcwd()


def import_dictionary(list_of_dict_names, key_index=0, value_index=1):

    os.chdir(PWD + "/DICTIONARIES")

    assert list_of_dict_names
    result_dictionary = dict()
    for name in list_of_dict_names:
        with open(name + ".txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = line.split("\t")
                assert len(line) == 2
                result_dictionary[line[key_index].strip()] = (line[value_index].strip(), name)

    os.chdir(PWD)
    return result_dictionary


def import_ontology(list_of_onto_names):

    os.chdir(PWD + "/ONTOLOGIES")

    assert list_of_onto_names
    result_dictionary = dict()
    for name in list_of_onto_names:
        with open(name + ".txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = line.split("\t")
                assert len(line) == 2

                if "," not in line[0]:
                    onto_key = line[0].strip()
                    onto_value = [line[1].strip(), name]
                else:
                    onto_key = line[0].split(",")[0]
                    onto_value = [line[1].strip(), name]
                    for word in line[0].split(",")[1:]:
                        word = word.split(" ")
                        for w in word:
                            onto_value.append(w)

                result_dictionary[onto_key] = onto_value
    os.chdir(PWD)
    return result_dictionary

DICTIONARY_NAMES = ["OBJECT", "SUBJECT", "FULL", "INFO"]

PROPERTIES = import_dictionary(DICTIONARY_NAMES)


ONTOLOGY = import_ontology(["CITY"])
# for key, value in ONTOLOGY.items():
#     print(key, value)

SYNONYMS = dict()
SYNONYMS["CITY"] = ['город', 'г.', 'деревня', "поселок", "село"]


def remove_prepositions(raw_query):
    assert type(raw_query) == str
    raw_query = re.sub("^во?\s", "", raw_query)
    raw_query = re.sub("\sво?$", "", raw_query)
    raw_query = re.sub("\sво?\s", " ", raw_query)
    return raw_query


def remove_punctuation(raw_query):
    assert type(raw_query) == str
    raw_query = re.sub("[\.,!?]", "", raw_query)
    return raw_query


def is_word(word):
    assert type(word) == str
    for symbol in word.lower():
        if symbol not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
            return False
    return True


def find_location(input_query):

    assert type(input_query) == str

    input_query = input_query.lower()
    input_query = remove_prepositions(input_query)
    input_query = remove_punctuation(input_query)
    lemmas = m.lemmatize(input_query.lower())
    lemmas = [l for l in lemmas if is_word(l)]
    input_query = [word.strip().lower() for word in input_query.split(" ") if is_word(word)]

    translation = None
    location = None
    category = None
    context = None

    for word in lemmas:
        if word in ONTOLOGY:
            location = ONTOLOGY[word][-1]
            translation = ONTOLOGY[word][0]
            category = ONTOLOGY[word][1]
            context = ONTOLOGY[word][2:-1]
    # if not location:
    #     location = search_bigram(lemmas)
    #     print(location)
    #     print("!!----!!----!!")

    if translation:

        print("translation:",translation)
        print("type:",category)
        print("context:",context)

        removing = []

        if context:
            for word in context:
                if word in lemmas:
                    removing.append(lemmas.index(word))

        for synonym in SYNONYMS[category]:
            if synonym in lemmas:
                ind = lemmas.index(synonym)
                removing.append(ind)

        removing.append(lemmas.index(location))
        for i in removing:
            input_query[i] = ""

        input_query = " ".join(input_query).strip()

        info = {"translation": translation, "type": category, "normalized": location}
        return {"info": info, "query": input_query}

    else:
        return False

print("=======")



# ======================================
# Функция импортирует шаблон.
def open_pattern(pattern_name):
    os.chdir(PWD + "/Patterns")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    return pattern


# Вспомогательная функция для проверки, является ли токен словом,
# а не знаком пунктуации или цифрами.
# def is_word(word):
#     assert type(word) == str
#     for symbol in word:
#         if symbol not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
#             return False
#     return True


# Вспомогательная функция
def reordered(bigram):
    bigram = bigram.split(" ")
    bigram = bigram[1] + " " + bigram[0]
    return bigram


# Вспомогательная функция для поиска биграммов в словаре локаций
# (чтобы находить такие локации как "новосибирская область").
def search_bigram(words_list):
    locations = []
    bigrams = []
    for i in range(0, len(words_list)):
        try:
            bigrams.append(words_list[i] + " " + words_list [i + 1])
        except IndexError:
            break
    for bigram in bigrams:
        if bigram in ONTOLOGY:
            locations.append(ONTOLOGY[bigram])
    if not locations:
        for bigram in bigrams:
            if reordered(bigram) in ONTOLOGY:
                locations.append(ONTOLOGY[bigram])
    return locations


# Функция проверяет потенциальный предикат на наличие в словаре предикатов.
def keyword_search(query):
    for key in PROPERTIES.keys():
        if key in query:
            return PROPERTIES[key]
    return False


# TODO: что делать, если найдено больше одного ключевого слова?

# Функция лемматизирует запрос, находит в нем локацию, находит потенциальный предикат,
# проверяет его в словаре предикатов (функция is_in_properties).
def analyze_input(raw_query):

    assert type(raw_query) == str

    result = find_location(raw_query)
    print(result)
# TODO: ----------->>>>>>>>>>>>>>>
    keyword = keyword_search(lemmas)
    if keyword:
        predicate, query_type = keyword[0], keyword[1]
        if query_type == "no_subject":
            location = ""
        else:
            rest = re.sub(predicate, "", lemmas)
            location = find_location(lemmas)

            if not location:
                raise KeyError("Location is not in the dictionary")
        return (translate_location(location), predicate, query_type)
    else:
        print("В ЗАПРОСЕ НЕ ОБНАРУЖЕНО КЛЮЧЕВЫХ СЛОВ")
        raise KeyError


    #
    # location = find_location(lemmas)
    # print("Локация: ", location)
    # if location:
    #     rest = re.sub(location[0], "", " ".join(lemmas)).strip()
    #     search = keyword_search(rest)
    #     if search:
    #         predicate, query_type = search[0], search[1]
    #         print("Предикат:", predicate)
    #     else:
    #         raise KeyError("В ЗАПРОСЕ НЕ ОБНАРУЖЕНО КЛЮЧЕВЫХ СЛОВ")
    #     return (translate_location(location), predicate, query_type)
    # else:
    #     raise KeyError("Location is not in the dictionary")



def define_pattern(query_type):
    if query_type == "default":
        return "pattern1"
    elif query_type == "no_subject":
        return "pattern3"
    elif query_type == "info":
        return "pattern4"
    else:
        return False


# Функция создает запрос. На вход подаётся субъект (локация),
# переменная (неизвестная информация), предикат и шаблон запроса.
def construct_query(subject, variable, predicate, query_type):
    print("TYPE:    ", query_type)
    query_pattern = define_pattern(query_type)
    print("PATTERN:    ", query_pattern)
    if query_pattern == "pattern1" or query_pattern == "pattern2":
        query_pattern = open_pattern(query_pattern)
        query_pattern = query_pattern.replace("SUBJECT", subject)
        query_pattern = query_pattern.replace("PREDICATE", predicate)

    elif query_pattern == "pattern3":
        query_pattern = open_pattern(query_pattern)
        query_pattern = query_pattern.replace("PREDICATE", predicate)

    elif query_pattern == "pattern4":
        query_pattern = open_pattern(query_pattern)
        query_pattern = query_pattern.replace("SUBJECT", subject)

    else:
        print("ТИП ЗАПРОСА НЕ НАЙДЕН.")

    query_pattern = query_pattern.replace("VARIABLE", variable)
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result[variable]["value"])
    return query_pattern, final



# TODO: написать функцию, подобную pattern-handler'у из бутстреппинга, чтобы одинаково мэтчились фразы "в берлине",
# TODO: "берлина", "берлин"

# TODO: подумать, как сделать функцию выбора шаблона sparql

# TODO: написать грамматику, которая делает из простой локации разные варианты (новосибирск, город новосибирск)

# TODO: сделать так, чтобы сначала поиск шел по полным шаблонам, где уже известен и объект и предикат



# Делаем запрос
def make_query(query):
    # Открываем шаблоны

    # pattern2 = open_pattern("pattern2.txt")
    print("\n")
    print("ЗАПРОС:")
    print(query)
    print("------------------------------------------------------------")
    (subject, predicate, query_type) = analyze_input(query)
    print(subject, predicate)
    sparql_query, result = construct_query(subject=subject, variable="variable",
                                           predicate=predicate, query_type=query_type)
    # if not result:
    #     sparql_query, result = construct_query(subject=subject, variable="variable",
    #                                            predicate=predicate, query_type="pattern2")
    # if not result:
    #     sparql_query, result = construct_query(subject=subject, variable="variable",
    #                                            predicate=predicate, query_type="pattern4")

    print("РЕЗУЛЬТАТ ЗАПРОСА: ")
    for r in result:
        print(r)
    print("\n" + "ТЕЛО ЗАПРОСА: ")
    print("------------------------------------------------------------")
    print(sparql_query)
    print("------------------------------------------------------------")



# query1 = "описание камышлинского района"
query2 = "В каком экономическом регионе находится Москва?"
query3 = "Какое население в Берлине?"
query4 = "какие страны в африке?"
query5 = "острова австралии"

# make_query(query1)
make_query(query2)
make_query(query3)
make_query(query4)
# # make_query(query5)