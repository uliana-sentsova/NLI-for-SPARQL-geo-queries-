import os
from pymystem3 import Mystem
import Constructor as constructor
m = Mystem()
import re
import random

# Функция для поиска заданной подстроки во всех поисковых запросах.
def queries_location(locations_list, queries = "queries.txt", break_by=162000000):
    """
    Функция берет на вход массив строк (географических названий) и делает поиск по файлу запросов. Запросы для каждого
    географического названия функция записывает в текстовый файл с названием, соответствующим названию геолокации.
    Файлы с запросами по конкретной геолокации находятся в директории "./Locations"

    :param locations_list: массив, содержащий географические названия
    :return: Функция возвращает значение True, если обработка завершена удачно. Если произошла ошибка, функция
    возвращает False, сообщение об ошибке и номер последней обработанной строки в файле запросов.
    """
    count = 0
    try:
        for location in locations_list:
            with open("Bootstrap_results/" + location.capitalize() + ".txt", 'w') as target_file, open(queries, 'r', encoding='utf-8') as source_file:
                p = re.compile("(?:^|\s)" + location + "(?:$|\s)", re.IGNORECASE)
                for line in source_file:
                    if p.search(line) is not None:
                        target_file.write(line)
                    count += 1
                    if count % 1000000 == 0:
                        print("Обработано ", count, " строк (ключевое слово: ", location, ").")
                    if count >= break_by:
                        print("Достигнуто количество строк: ", break_by)
                        print("Переход к следующему ключевому слову...")
                        break
                count = 0
        return True
    except Exception as err:
        print(err)
        print("Последняя обработанная строка: {0}".format(count))
        return False


# Вспомоагательная функция для создания частотного словаря
def make_freq_dict(my_array):
    """
    Функция создает из массива строк частотный словарь.
    :param my_array: на вход подаётся массив строк
    :return: функция возвращает частотный словарь
    """
    d = dict()
    for m in my_array:
        d[m] = d.get(m, 0) + 1
    return d


# Функция ищет общие запросы между разными городами ( "./Locations")
def all_patterns(lemmatize=False):
    """
    Для всех файлов в директории "/Locations/queries" функция заменяет в каждом запросе название геолокации
    на нижнее подчеркивание, затем составляет общий список из получившихся шаблонов и возвращает частотный словарь.
    Пример преобразования запроса в шаблон: "какая погода в москве завтра" -> "какая погода в _ завтра".
    Общий список шаблонов (без повторений) функция записывает в файл "Unique patterns".
    :param lemmatize: при необходимости, запросы можно лемматизировать. По умолчанию False.
    :return:
    """
    all_queries = []
    pwd = os.getcwd()
    path = pwd + "/Locations/queries"
    os.chdir(path)
    for filename in os.listdir():
        with open(filename, 'r', encoding="utf-8") as f:
            city = filename.lower().split(".")[0]
            for line in f:
                line = line.strip()
                if lemmatize == True:
                    line = m.lemmatize(line)
                    line = "".join(line)
                line = re.sub(city+'.*', "_", line)
                all_queries.append(line)
    # Записываем все паттерны в файл
    os.chdir(pwd)
    with open("Unique_patterns.txt", 'w', encoding='utf-8') as target:
        for line in list(set(all_queries)):
            target.write(line + '\n')

    # with open("All_patterns.txt", 'w', encoding='utf-8') as target:
    #     for line in all_queries:
    #         target.write(line + '\n')

    # Составляем частотный словарь
    freq = dict()
    for query in all_queries:
        freq[query] = freq.get(query, 0) + 1

    print("Количество запросов: ", len(all_queries), "\n", "Количество уникальных запросов: ", len(freq))

    # Возвращаем частотный словарь
    return freq


# Функция отбирающая шаблоны с заданной частотностью.
def frequent_patterns(freq_dict, threshold=200):
    """
    Функция возвращает все шаблоны, частотность которых выше заданной. Отобранные шаблоны записываются в файл
    "Frequent_patterns.txt" в директории проекта.
    :param freq_dict: частотный словарь
    :param threshold: пороговое значение частотности
    :return:
    """
    frequent = []
    for key in freq_dict:
        if freq_dict[key] > threshold:
            frequent.append(key)
    with open("Frequent_patterns.txt", 'w') as f:
        for pattern in frequent:
            f.write(pattern + '\n')
    print("Создан файл с шаблонами.")
    return frequent


def same_structure(pattern, query, replaced="_"):
    """
    Функция сравнивает структуру запроса с заданным шаблоном, и если структура совпадает, то функция
    возвращает True и токен из запроса, занимающий место пропуска в структуре шаблоне, иначе – False. Например,
    запрос "какая погода в _" и запрос "какая погода в тюмени" имеют одинаковую структуру, и функция вернет
    токен "тюмени".

    :param pattern: шаблон, с которым сранивается запрос
    :param query: запрос
    :param replaced: символ, которым в шаблоне была заменена геолокация, по умолчанию нижнее подчеркивание.
    :return:
    """
    if pattern != replaced:
        if pattern.endswith(replaced):
            pattern = pattern[:-len(replaced)]
            if query.startswith(pattern) and len(query.split(pattern)[1].split(" ")) == 1:
                return query.split(pattern)[1]
            else:
                return False
        elif pattern.startswith(replaced):
            pattern = pattern[len(replaced):]
            if query.endswith(pattern) and len(query.split(pattern)[0].split(" ")) == 1:
                return query.split(pattern)[0]
            else:
                return False
        elif not pattern.endswith(replaced) and not pattern.startswith(replaced):
            pattern = pattern.split(replaced)
            if query.startswith(pattern[0]) and query.endswith(pattern[1]):
                word_in_the_middle = query[len(pattern[0]):-len(pattern[1])]
                if word_in_the_middle and len(word_in_the_middle.split(" ")) == 1:
                    return word_in_the_middle
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

# Функция возвращает N наиболее популярных запросов в заданном частотном словаре.
def most_popular(freq_dictionary, n=10):
    value_key_pairs = [(key, value) for value, key in freq_dictionary.items()]
    value_key_pairs.sort()
    return value_key_pairs[-n:]


# Функция для составления словаря биграммов
def bigrams(queries_list, keyword):
    """
    Функция составляет из списка запросов частотный словарь биграмм относительно заданного слова. Например,
    относительно ключевого слова "новосибирск" будет возвращен словарь, содержащий биграммы "новосибирская область",
    "погода новосибирск" и т.п.
    :param queries_list:
    :param keyword:
    :return:
    """
    bigrams_dict = dict()
    for query in queries_list:
        query = query.split()
        for i in range(0, len(query)-1):
            try:
                bigram = query[i] + " " + query[i+1]
                if keyword in bigram:
                    bigrams_dict[bigram] = bigrams_dict.get(bigram, 0) + 1
            except IndexError:
                break

    return bigrams_dict


# Вспомогательная функция
def queries_from_file(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            yield line


def new_locations(patterns, sourcefile = "queries.txt"):
    """
    Функция для выполнения последнего цикла бутстреппинга: на вход подаются шаблоны, функция возвращает геолокации,
    которые встречаются в данных шаблонах.
    :param patterns: шаблоны
    :param sourcefile: название файла с запросами, по умолчанию "queries.txt"
    :return:
    """
    locations = []
    with open(sourcefile, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            for pattern in patterns:
                if same_structure(pattern, line):
                    locations.append(same_structure(pattern, line))
    return locations

def lemmatize_query(query):
    query = m.lemmatize(query)
    lemmas = [l for l in query if constructor.is_word(l)]
    return lemmas


def check_location(query):
    location = constructor.ontology_search(query)
    if location != (False, False):
        return True
    else:
        return False



# city_names = ["река", "часовой пояс", "река рядом", "основание", "основан", "почтовый код",
# "географическое положение", "притоки", "куда впадает", "кто основал"]
# queries_location(city_names, queries="queries.txt", break_by=50000000)


evaluation_set = []
for filename in os.listdir(constructor.PWD + "/Bootstrap_results"):
    query_array = []

    print("Создание коллекции случайно выбранных запросов для ключевого слова: ", filename.split(".")[0].lower())
    with open("Bootstrap_results/" + filename, "r", encoding="utf-8") as keyword_file:
        for line in keyword_file:
            line = line.strip()
            query = lemmatize_query(line)
            if check_location(query) and len(query) < 6:
                query_array.append(line)
        for i in range(0, 20):
            try:
                random_index = random.randint(0, len(query_array) - 1)
                random_query = query_array[random_index]
                evaluation_set.append(random_query)
            except ValueError:
                continue

for entry in evaluation_set:
    print(entry)




# # Файл для хранения использованных шаблонов, чтобы избежать повторений.
# used_patterns = []
# with open("Used_patterns.txt", "r", encoding="utf-8") as h:
#     for line in h:
#         used_patterns.append(line.strip())
#
# freq = all_patterns()
# freq = frequent_patterns(freq, threshold=300)
#
# patterns_to_use = [key for key in freq if len(key.split()) > 2]
# print(patterns_to_use)
#
# with open("Used_patterns.txt", "a", encoding="utf-8") as f:
#     f.write("\n")
#     for p in patterns_to_use:
#         f.write(p + "\n")
# print("Использованные паттерны записаны в файл Used_patterns.txt.")
#
# # Ищем новые географические локации и составляем из полученных частотный словарь
# locations = new_locations(patterns_to_use)
# freq_locations = make_freq_dict(locations)
#
# # Записываем самые часто встречающиеся новые географические названия в файл:
# f = open("New locations.txt", 'w')
# for popular in most_popular(freq_locations, 150):
#     print(m.lemmatize(popular[1])[0])
#     f.write(popular[1] + '\n')
# f.close()