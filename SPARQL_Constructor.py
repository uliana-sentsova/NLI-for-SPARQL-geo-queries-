import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
from pymystem3 import Mystem
m = Mystem()
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

PWD = os.getcwd()


def import_dictionary(list_of_dict_names):

    os.chdir(PWD + "/PREDICATES_DICTIONARY")

    assert list_of_dict_names
    result_dictionary = dict()
    for dict_name in list_of_dict_names:
        with open(dict_name + ".txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = line.split(" = ")
                assert len(line) == 3
                pattern = line[0].strip()
                value = [l for l in line[1:]]
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
DICTIONARY_NAMES = ["subj", "obj_loc"]

PREDICATES = import_dictionary(DICTIONARY_NAMES)
# for key in PREDICATES:
#     print(key, PREDICATES[key])

ONTOLOGY = import_ontology(os.listdir(PWD + "/ONTOLOGIES"))

SYNONYMS = dict()
SYNONYMS["settlements"] = ["город", "г.", "деревня", "поселок", "село", "пгт","населенный пункт", "россия","рф",
                          "российкий федерация"]
SYNONYMS["rivers"] = ["река", "речка"]
SYNONYMS["mountains"] = ["гора", "сопка", "вулкан"]
SYNONYMS["seas"] = ["море"]
SYNONYMS["volcanos"] = ["вулкан", "гора"]
SYNONYMS["islands"] = ["архипелаг", "остров"]
SYNONYMS["lakes"] = ["озеро", "водохранилище"]
SYNONYMS["regions"] = ["край", "регион", "область"]






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
        if symbol not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя-":
            return False
    return True


def ontology_search(lemmas):
    """
    Функция для поиска локации в онтологии. Поиск жадный: сначала ищутся биграммы, затем единичные токены.
    :param lemmas: лемматизированный запрос (список)
    :return:
    """
    location = None
    location_lemmatized = ""

    # Поиск по биграммам:
    search = search_bigram(lemmas)
    if search:
        # Location - вся информация о локации, которая содержится в онтологии;
        # location_lemmatized - лемма, вход в онтологию
        location, location_lemmatized = [s for s in search]
    else:
        for word in lemmas:
            if word in ONTOLOGY:
                location = ONTOLOGY[word]
                location_lemmatized = word
    if location:
        return location_lemmatized, location
    else:
        return False, False


def find_location(input_query):
    """
    Функция для поиска локации в запросе. Максимально возможное количество найденных локаций: 2 (пока что).
    Функция ищет локации, если найдено две локации, то сравнивает дескрипторы каждой из локаций, чтобы
    можно было определить, является запрос уточнением одной локации (троицк москва) или объединением двух локаций
    (москва новосибирск).
    :param input_query: запрос, тип: строка
    :return: список словарей, каждый словарь содержит ключи: normalized (нормализованный тип локации), lemmatized
    (лемма в онтологии), context (дескрипторы), translation (URI из DBPedia) и category (тип локации - город, река,
    континент, государство и т.д.).
    """

    assert type(input_query) == str

    input_query = input_query.lower()
    input_query = remove_prepositions(input_query)
    input_query = remove_punctuation(input_query)
    lemmas = m.lemmatize(input_query.lower())
    lemmas = [l for l in lemmas if is_word(l)]
    input_query = [word.strip().lower() for word in input_query.split(" ") if is_word(word)]

    location_lemmatized, location = ontology_search(lemmas)
    if location:
        location_normalized = location["normalized"]
        translation = location["translation"]
        category = location["type"]
        context = location["context"]

        print("Location found:", location_normalized)

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
                        context, "type": category, "translation": translation}
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

                print("Location found:", location_normalized)

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
                        context, "type": category, "translation": translation}

                result.append(info)

        if len(result) == 2:
            checked = check_real_subject(result)
            print("Subjects analysis...")
            if checked:
                print("One subject: ", checked["normalized"])
                return [checked]
            else:
                print("Number of subjects: ", len(result))
                print("Subject 1: ", result[0]["normalized"])
                print("Subject 2: ", result[1]["normalized"])
                return result
        elif len(result) > 2:
            raise ValueError("Locations more than two in the query.")
        else:
            return result

    else:
        return False


def check_real_subject(loc_list):
    """
    Функция проверяет, входит ли одна локация в другую с точки зрения онтологии.
    Пример 1: обрабатывая запрос ["никольск", "пензенская область"], функция вернет локацию Никольск,
    так как Никольск находится в Пензенской области.

    Пример 2: обрабатывая запрос ["новосибирск", "москва"]", функция вернет значение False,
    так как Новосибирск и Москва являются локациями одного уровня, согласно онтологии.
    :param loc_list: список локаций (пока можно подавать  на вход только две!)
    :return: False, если локации одного уровня. Если локации разных уровней (город и регион), вернет локацию с
    меньшим уровнем (город).
    """
    assert len(loc_list) == 2
    for i in loc_list[1]["context"]:
        if i == loc_list[0]["lemmatized"]:
            return loc_list[1]
    for i in loc_list[0]["context"]:
        if i == loc_list[1]["lemmatized"]:
            return loc_list[0]
    return False


# Функция импортирует шаблон.
def open_pattern(pattern_name):
    """
    Функция импортирует шаблон по заданному имени.
    :param pattern_name:
    :return:
    """
    os.chdir(PWD + "/PATTERNS_LIBRARY")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    os.chdir(PWD)
    return pattern



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
    if not location:
        for bigram in bigrams:
            if reordered(bigram) in ONTOLOGY:
                location = (ONTOLOGY[bigram], bigram)
    return location


# Функция проверяет потенциальный предикат на наличие в словаре предикатов.
def keyword_search(query):
    for key in PREDICATES.keys():
        try:
            x = re.compile(key)
        except Exception:
            print("______", key)
        matched = re.findall(x, query)
        if matched:
            query = query.replace(matched[0], "")
            return (PREDICATES[key], query)
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

    print("Analyzing query pattern...")
    keyword, query = keyword_search(raw_query)

    if not keyword:
        raise KeyError("Query type not found.")
    else:
        predicate, query_type = keyword[0], keyword[1]
        print("Query pattern found. Type:", query_type)
        print("Predicate:", predicate[0])

        if query_type != "no_subject":
            print("Searching for a location...")
            location = find_location(query)
            if not location:
                raise KeyError("Location not found.")
            else:
                locations = [l["translation"] for l in location]
                if len(locations) > 1:
                    query_type = query_type + "_union_" + str(len(locations))
                return [locations, predicate, query_type]
    return False


def choose_pattern(query_type):
    """
    Функция по типу предиката выбирает шаблон для запроса
    :param query_type: тип предиката, известен из словаря предикатов
    :return: строка, содержащая шаблон SPARQL
    """
    if query_type == "subj":
        return open_pattern("subject")
    elif query_type == "object":
        return open_pattern("pattern2")
    elif query_type == "no_subject":
        return open_pattern("pattern3")
    elif query_type == "obj_loc":
        return open_pattern("obj_loc")
    elif query_type == "info":
        return open_pattern("pattern4")
    elif query_type == "subj_union_2":
        return open_pattern("subj_union_2")
    elif query_type == "obj_union_2":
        return open_pattern("obj_union_2")
    else:
        return False


def construct_query(subject, predicate, query_type, variable="VARIABLE"):
    """
    Функция берет на вход субъект, предикат и тип запроса и формирует шаблон SPARQL. Функция проверяет, относительно
    какого количества локаций необходимо сделать запрос. Если локаций больше 1, функция заменяет обе локации в шаблоне
    :param subject:
    :param predicate:
    :param query_type:
    :param variable:
    :return:
    """
    query_pattern = choose_pattern(query_type)
    if not query_pattern:
        raise KeyError("Pattern not found.")
    if "union" not in query_type:
        subject = subject[0]
        if "obj" in query_type:

            obj_type = predicate[1]
            predicate = predicate[0]

            query_pattern = query_pattern.replace("SUBJECT", subject)
            query_pattern = query_pattern.replace("TYPE", obj_type)
            query_pattern = query_pattern.replace("PREDICATE", predicate)
        else:
            predicate = predicate[0]
            query_pattern = query_pattern.replace("SUBJECT", subject)
            query_pattern = query_pattern.replace("PREDICATE", predicate)
            query_pattern = query_pattern.replace("VARIABLE", variable)

    else:
        predicate = predicate[0]
        query_pattern = query_pattern.replace("PREDICATE", predicate)
        for i in range(0, len(subject)):
            query_pattern = query_pattern.replace("SUBJECT" + str(i + 1), subject[i])
            query_pattern = query_pattern.replace("VARIABLE" + str(i + 1), variable + str(i+1))

    return query_pattern


def ask_query(query_pattern, variable="VARIABLE", num_vars=1):
    """
    Функция отправляет сформированный запрос SPAQRL в DBPedia. Предварительно функция проверяет правильность имени
    переменной, а также количество переменных, которых не может быть больше двух и меньше единицы (пока что).
    :param query_pattern: готовый шаблон SPARQL
    :param variable: название переменной, лучше не менять
    :param num_vars: количество переменных в запросе
    :return:
    """
    assert not variable.startswith("?")
    assert "_" not in variable
    assert num_vars > 0
    assert num_vars < 3
    if num_vars == 1:
        sparql.setQuery(query_pattern)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        final = []
        for result in results["results"]["bindings"]:
            final.append(result[variable]["value"])
        return final

    elif num_vars == 2:
        sparql.setQuery(query_pattern)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        final = []
        for result in results["results"]["bindings"]:
            variable1 = variable + "1"
            variable2 = variable + "2"
            final.append(result[variable1]["value"])
            final.append(result[variable2]["value"])
        return final

    else:
        return False


# Делаем запрос
def make_query(query):
    print("------------------------------------------------------------")
    print("ЗАПРОС:", query)
    print("------------------------------------------------------------")
    subject, predicate, query_type = analyze_input(query)
    # print("SUBJECT:", subject, "PREDICATE:", predicate)
    query_pattern = construct_query(subject=subject,
                                           predicate=predicate, query_type=query_type)
    print("\n" + "ТЕЛО ЗАПРОСА: ")
    print("------------------------------------------------------------")
    print(query_pattern)
    print("------------------------------------------------------------")

    result = ask_query(query_pattern, variable="VARIABLE", num_vars = len(subject))

    print("РЕЗУЛЬТАТ ЗАПРОСА: ")
    if result:
        for r in result:
            print(r)

    print("\n\n\n")


query1 = "где находиться г. липецк?"
query2 = "мэр города новосибирска и москвы"
query3 = "На какой реке расположен Красноярск?"
query4 = "Ульяновск кто родился из знаменитостей"
query5 = "Новосибирск какая река рядом?"
query6 = "Москва столица какого государства?"
query7 = "экономический регион москвы?"
query8 = "тюмень где располагается"
query9 = "про екатеринбург"
query10 = "кемерово описание"
query11 = "омск томск координаты"
query12 = "Москва столица какого государства?"

queries = ["где находиться г. липецк?", "численность москвы и московской области", "про екатеринбург",
           "грязи липецкая область какая численность", "мэр воронежа", "мэр города новосибирска и москвы",
           "На какой реке расположен Красноярск?", "Новосибирск какая река рядом?", "экономический регион москвы?",
           "Москва столица какого государства?", "тюмень где располагается", "кемерово описание", "омск томск координаты"
           "где расположен владивосток", "петербург координаты", "широта санкт-петербург в градусах", "реки россии",
           "липецк экономический регион", "омск в каком округе находиться", "магадан какой край"]

for query in queries:
    try:
        make_query(query)
    except KeyError:
        print("ЗАПРОС НЕ ОБРАБОТАН", query)



# TODO распар
