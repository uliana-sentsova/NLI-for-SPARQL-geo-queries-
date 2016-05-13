import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
from pymystem3 import Mystem
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

PWD = os.getcwd()

def import_dictionary(list_of_dict_names, key_index=0, value_index=1):

    os.chdir(PWD + "/DICTIONARIES")

    assert list_of_dict_names
    result_dictionary = dict()
    for dict_name in list_of_dict_names:
        with open(dict_name + ".txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = line.split(" = ")
                assert len(line) == 2
                pattern = line[key_index].strip()
                value = line[value_index].strip()
                result_dictionary[pattern] = (value, dict_name)

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

                normalized = ""
                context = []

                if "," not in line[0]:
                    onto_key = line[0].strip()
                    onto_value = [line[1].strip(), name]
                else:
                    onto_value = line[1]

                    lino = line[0].split(",")
                    onto_key = lino[0]
                    context = lino[1:-1]
                    normalized = lino[-1]
                    # for word in line[0].split(",")[1:]:
                    #     word = word.split(" ")
                    #     for w in word:
                    #         onto_value.append(w)

                result_dictionary[onto_key] = {"translation": onto_value, "normalized":
                    normalized, "context": context, "type": name}
    os.chdir(PWD)
    return result_dictionary

# DICTIONARY_NAMES = ["OBJECT", "SUBJECT", "FULL", "INFO"]
DICTIONARY_NAMES = ["subj"]

PROPERTIES = import_dictionary(DICTIONARY_NAMES)


ONTOLOGY = import_ontology(["russian_settlement"])

SYNONYMS = dict()
SYNONYMS["russian_settlement"] = ['город', 'г.', 'деревня', "поселок", "село", "пгт","населенный пункт", "россия","рф",
                          "российкий федерация"]


def remove_prepositions(raw_query):
    assert type(raw_query) == str
    raw_query = re.sub("^во?\s", "", raw_query)
    raw_query = re.sub("\sво?$", "", raw_query)
    raw_query = re.sub("\sво?\s", " ", raw_query)
    raw_query = re.sub("^на\s", "", raw_query)
    raw_query = re.sub("\sна$", "", raw_query)
    raw_query = re.sub("\sна\s", " ", raw_query)
    return raw_query


def remove_punctuation(raw_query):
    assert type(raw_query) == str
    raw_query = re.sub("[\.,!?]", "", raw_query)
    return raw_query

def remove_modifiers(raw_query):
    assert type(raw_query) == str
    modifiers = ["официально", "онлайн", "он лайн"]
    for m in modifiers:
        raw_query = raw_query.replace(m, "")
    return raw_query


def is_word(word):
    assert type(word) == str
    for symbol in word.lower():
        if symbol not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
            return False
    return True


def ontology_search(lemmas):
    location = None
    location_lemmatized = ""
    search = search_bigram(lemmas)
    if search:
        location, location_lemmatized = [s for s in search]
    else:
        for word in lemmas:
            if word in ONTOLOGY:
                location = ONTOLOGY[word]
                location_lemmatized = word
    if location:
        return (location_lemmatized, location)
    else:
        return False, False


def find_location(input_query):
    print("INPUT:", input_query)

    assert type(input_query) == str

    input_query = input_query.lower()
    input_query = remove_prepositions(input_query)
    input_query = remove_punctuation(input_query)
    lemmas = m.lemmatize(input_query.lower())
    lemmas = [l for l in lemmas if is_word(l)]
    input_query = [word.strip().lower() for word in input_query.split(" ") if is_word(word)]


    print("LEMMAS:", lemmas)

    location_lemmatized, location = ontology_search(lemmas)
    if location:
        location_normalized = location["normalized"]
        translation = location["translation"]
        category = location["type"]
        context = location["context"]

        # print("LOCATION_norm:", location_normalized)
        # print("LOCATION_lemm:", location_lemmatized)
        # print("TRANSLATION:", translation)
        # print("CATEGORY:", category)
        # print("CONTEXT:", context)

        removing = []

        if context:
            for word in context:
                if word in lemmas:
                    removing.append(lemmas.index(word))

        # for synonym in SYNONYMS[category]:
        #     if synonym in lemmas:
        #         ind = lemmas.index(synonym)
        #         removing.append(ind)

        location_lemmatized = location_lemmatized.split()
        for l in location_lemmatized:
            removing.append(lemmas.index(l))
        for i in removing:
            input_query[i] = ""
            lemmas[i] = ""
        lemmas = [l for l in lemmas if l]
        input_query = [q for q in input_query if q]

        info = {"lemmatized": " ".join(location_lemmatized), "normalized": location_normalized, "context":
                        context, "type": category}
        result = []
        result.append(info)

        # Повторный поиск в оставшемся запросе:
        if lemmas:
            location_lemmatized, location = ontology_search(lemmas)
            if location:
                location_normalized = location["normalized"]
                translation = location["translation"]
                category = location["type"]
                context = location["context"]
                # print("----------")
                # print("LOCATION_norm:", location_normalized)
                # print("LOCATION_lemm:", location_lemmatized)
                # print("TRANSLATION:", translation)
                # print("CATEGORY:", category)
                # print("CONTEXT:", context)

                removing = []
                if context:
                    for word in context:
                        if word in lemmas:
                            removing.append(lemmas.index(word))
                location_lemmatized = location_lemmatized.split()
                for l in location_lemmatized:
                    removing.append(lemmas.index(l))
                for i in removing:
                    input_query[i] = ""
                    lemmas[i] = ""
                lemmas = [l for l in lemmas if l]
                input_query = [q for q in input_query if q]

                info = {"lemmatized": " ".join(location_lemmatized), "normalized": location_normalized, "context":
                        context, "type": category}

                result.append(info)

        if len(result) == 2:
            result = check_real_subject(result)
            return result
        elif len(result) > 2:
            raise ValueError("Locations more than two in the query.")
        else:
            return result

    else:
        return False

print("=======")


def check_real_subject(loc_list):
    assert len(loc_list) == 2
    for i in loc_list[1]["context"]:
        if i == loc_list[0]["lemmatized"]:
            return loc_list[1]
    for i in loc_list[0]["context"]:
        if i == loc_list[1]["lemmatized"]:
            return loc_list[0]
    return False



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
    bigrams = []
    location = None
    for i in range(0, len(words_list)):
        try:
            bigrams.append(words_list[i] + " " + words_list [i + 1])
        except IndexError:
            break
    for bigram in bigrams:
        if bigram in ONTOLOGY:
            location = (ONTOLOGY[bigram], bigram)
    for bigram in bigrams:
        if reordered(bigram) in ONTOLOGY:
            location = (ONTOLOGY[bigram], bigram)
    return location


# Функция проверяет потенциальный предикат на наличие в словаре предикатов.
def keyword_search(query):
    for key in PROPERTIES.keys():
        x = re.compile(key)
        matched = re.findall(x, query)
        if matched:
            query = query.replace(matched[0], "")
            return (PROPERTIES[key], query)
    return False


# TODO: что делать, если найдено больше одного ключевого слова?

# Функция лемматизирует запрос, находит в нем локацию, находит потенциальный предикат,
# проверяет его в словаре предикатов (функция is_in_properties).
def analyze_input(raw_query):

    assert type(raw_query) == str

    raw_query = raw_query.lower()
    raw_query = remove_prepositions(raw_query)
    raw_query = remove_punctuation(raw_query)
    raw_query = remove_modifiers(raw_query)

    keyword, query = keyword_search(raw_query)
    if not keyword:
        raise KeyError("Query type not found.")

    location = find_location(query)
    print(location)
    if not location:
        raise KeyError("Location not found.")

    raise ValueError


    predicate, query_type = keyword[0], keyword[1]

    return location["location"]["translation"], predicate, query_type


def choose_pattern(query_type):
    if query_type == "subj":
        return open_pattern("pattern1")
    elif query_type == "object":
        return open_pattern("pattern2")
    elif query_type == "no_subject":
        return open_pattern("pattern3")
    elif query_type == "info":
        return open_pattern("pattern4")
    else:
        return False


def construct_query(subject, predicate, query_type, variable="concept"):
    print(query_type)
    query_pattern = choose_pattern(query_type)
    if not query_pattern:
        raise KeyError("Pattern not found.")

    query_pattern = query_pattern.replace("SUBJECT", subject)
    query_pattern = query_pattern.replace("PREDICATE", predicate)
    query_pattern = query_pattern.replace("VARIABLE", variable)

    return query_pattern


def ask_query(query_pattern, variable="concept"):
    assert not variable.startswith("?")
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result[variable]["value"])
    return final


# TODO: написать функцию, подобную pattern-handler'у из бутстреппинга, чтобы одинаково мэтчились фразы "в берлине",
# TODO: "берлина", "берлин"

# TODO: подумать, как сделать функцию выбора шаблона sparql

# TODO: написать грамматику, которая делает из простой локации разные варианты (новосибирск, город новосибирск)

# TODO: сделать так, чтобы сначала поиск шел по полным шаблонам, где уже известен и объект и предикат

# Делаем запрос
def make_query(query):

    print("ЗАПРОС:", query)
    print("------------------------------------------------------------")
    (subject, predicate, query_type) = analyze_input(query)
    print("SUBJECT:", subject, "PREDICATE:", predicate)
    query_pattern = construct_query(subject=subject,
                                           predicate=predicate, query_type=query_type)
    print("\n" + "ТЕЛО ЗАПРОСА: ")
    print("------------------------------------------------------------")
    print(query_pattern)
    print("------------------------------------------------------------")

    result = ask_query(query_pattern)

    # if not result:
    #     sparql_query, result = construct_query(subject=subject, variable="variable",
    #                                            predicate=predicate, query_type="pattern2")
    # if not result:
    #     sparql_query, result = construct_query(subject=subject, variable="variable",
    #                                            predicate=predicate, query_type="pattern4")

    print("РЕЗУЛЬТАТ ЗАПРОСА: ")
    for r in result:
        print(r)


query1 = "новошахтинск ростовский область экономический регион?"
query2 = "В каком экономическом регионе находится московская область?"
query3 = "Какое население в Липецке?"
query4 = "На какой реке расположена Пензенская область?"
# query4 = "какие страны в африке?"
# query5 = "острова австралии"

make_query(query1)
make_query(query2)
make_query(query3)
make_query(query4)
# # make_query(query5)