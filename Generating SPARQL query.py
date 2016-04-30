import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
from pymystem3 import Mystem
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# ======================================

pwd = os.getcwd()
os.chdir(pwd + "/DICTIONARIES")
LOCATION_DICTIONARY = dict()
with open("RU-EN.txt", 'r', encoding="utf-8") as f:
    for line in f:
        LOCATION_DICTIONARY[line.split("\t")[0]] = line.strip().split("\t")[1]

PROPERTIES = dict()
with open("PROP.txt", "r", encoding="utf-8") as g:
    for line in g:
        line = line.strip().split(",")
        PROPERTIES[line[0]] = (line[1], "default")
        # PROPERTIES[line[1]] = [l for l in line[0].split(",")]

with open("FULL.txt", "r", encoding="utf-8") as g:
    for line in g:
        line = line.strip().split(",")
        PROPERTIES[line[0]] = (line[1], "full")

with open("ABOUT.txt", "r", encoding="utf-8") as g:
    for line in g:
        line = line.strip().split(",")
        PROPERTIES[line[0]] = (line[1], "about")



os.chdir(pwd)
pwd = os.getcwd()


# ======================================
# Функция импортирует шаблон.
def open_pattern(pattern_name):
    os.chdir(pwd + "/Patterns")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    return pattern


# Вспомогательная функция для проверки, является ли токен словом,
# а не знаком пунктуации или цифрами.
def is_word(word):
    assert type(word) == str
    for symbol in word:
        if symbol not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
            return False
    return True


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
        if bigram in LOCATION_DICTIONARY:
            locations.append(bigram)
    if not locations:
        for bigram in bigrams:
            if reordered(bigram) in LOCATION_DICTIONARY:
                locations.append(bigram)
    return locations


# Функция ищет локацию в запросе: сначала отдельные слова, затем биграммы.
# На вход нужно подавать лемматизированный array.
def find_location(words_list):
    words_list = words_list.split(" ")
    locations = []
    for word in words_list:
        if word in LOCATION_DICTIONARY:
            locations.append(word)
    if not locations:
        return search_bigram(words_list)
    else:
        return locations


# Функция переводит запрос на язык DPBedia: Липецк -> Lipetsk
def translate_location(location):
    if location == "":
        return ""
    else:
        return LOCATION_DICTIONARY[location[0]]


# Функция проверяет потенциальный предикат на наличие в словаре предикатов.
def keyword_search(query):
    for key in PROPERTIES.keys():
        if key in query:
            return PROPERTIES[key]
    return False


# TODO: что делать, если найдено больше одного ключевого слова?

# Функция лемматизирует запрос, находит в нем локацию, находит потенциальный предикат,
# проверяет его в словаре предикатов (функция is_in_properties).
def analyze_input(input_query):
    assert type(input_query) == str
    lemmas = m.lemmatize(input_query.lower())
    lemmas = [l for l in lemmas if is_word(l)]
    lemmas = " ".join(lemmas).strip()

    keyword = keyword_search(lemmas)
    if keyword:
        predicate, query_type = keyword[0], keyword[1]
        print("Предикат:", predicate)

        if query_type == "full":
            location = ""
        else:
            rest = re.sub(predicate, "", lemmas)
            location = find_location(lemmas)

            if not location:
                print("Location is not in the dictionary")
                raise KeyError

            print("Локация: ", location)

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
    elif query_type == "full":
        return "pattern3"
    elif query_type == "about":
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
    print(query_type)
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



query1 = "описание камышлинского района"
query2 = "В каком экономическом регионе находится Москва?"
query3 = "Какое население в Берлине?"
query4 = "какие страны в африке?"

make_query(query1)
make_query(query2)
make_query(query3)
make_query(query4)