import os
from pymystem3 import Mystem
m = Mystem()
import re


queries = []
count = 0



# Фукнция для обработки исходного файла и поиска конкретной локации
def queries_location(city_names, filename="queries.txt"):
    try:
        count = 0
        for city_name in city_names:
            target_file = open(city_name.capitalize() + ".txt", 'w', )
            source_file = open(filename, 'r', encoding='utf-8')
            p = re.compile(city_name+"\w{0,2}", re.IGNORECASE)
            for line in source_file:
                if p.search(line) is not None:
                    target_file.write(line)
                count += 1
                if count % 1000000 == 0:
                    print("Обработано ", count, " строк (локация: ", city_name, ").")
            source_file.close()
            count = 0
        return True
    except Exception as err:
        print(err)
        print(count)
        return False


def make_freq_dict(my_array):
    d = dict()
    for m in my_array:
        d[m] = d.get(m, 0) + 1
    return d

# Функция ищет общие запросы между разными городами ( "./Locations")
def all_patterns(lemmatize=False):
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

    with open("All_patterns.txt", 'w', encoding='utf-8') as target:
        for line in all_queries:
            target.write(line + '\n')

    # Составляем частотный словарь
    freq = dict()
    for query in all_queries:
        freq[query] = freq.get(query, 0) + 1

    print("Количество запросов: ", len(all_queries), "\n", "Количество уникальных запросов: ", len(freq))

    # Возвращаем частотный словарь
    return freq


def frequent_patterns(freq_dict, threshold=10):
    frequent = []
    for key in freq_dict:
        if freq_dict[key] > threshold:
            frequent.append(key)
    f = open("Frequent_patterns.txt", 'w')
    for pattern in frequent:
        f.write(pattern + '\n')
    f.close()
    print("Создан файл с шаблонами.")
    return frequent


def same_structure(pattern, query, missed_word="_"):
    if pattern != missed_word:
        if pattern.endswith(missed_word):
            pattern = pattern[:-len(missed_word)]
            if (query.startswith(pattern) and len(query.split(pattern)[1].split(" ")) == 1):
                return query.split(pattern)[1]
            else:
                return False
        elif pattern.startswith(missed_word):
            pattern = pattern[len(missed_word):]
            if (query.endswith(pattern) and len(query.split(pattern)[0].split(" ")) == 1):
                return query.split(pattern)[0]
            else:
                return False
        elif not pattern.endswith(missed_word) and not pattern.startswith(missed_word):
            pattern = pattern.split(missed_word)
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


def most_popular(freq_dictionary, n=10):
    value_key_pairs = [(key, value) for value, key in freq_dictionary.items()]
    value_key_pairs.sort()
    return value_key_pairs[-n:]

def bigrams(queries_list, keyword):
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

def queries_from_file(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            yield line


def new_locations(patterns, sourcefile = "queries.txt"):
    locations = []
    f = open(sourcefile, 'r', encoding="utf-8")
    for line in f:
        line = line.strip()
        for pattern in patterns:
            if same_structure(pattern, line):
                locations.append(same_structure(pattern, line))
    f.close()
    return locations

city_names = []
with open("New LOCATIONS_DICTIONARY.txt", 'r') as h:
    for line in h:
        line = line.strip()
        city_names.append(line)

queries_location(city_names, filename="queries.txt")

used_patterns = []
with open("Used_patterns.txt", "r", encoding="utf-8") as h:
    for line in h:
        used_patterns.append(line.strip())

freq = all_patterns()
freq = frequent_patterns(freq, threshold=200)

patterns_to_use = [key for key in freq if len(key.split()) > 2 and key not in used_patterns]

with open("Used_patterns.txt", "a", encoding="utf-8") as f:
    f.write("\n")
    for p in patterns_to_use:
        f.write(p + "\n")
print("Использованные паттерны записаны в файл Used_patterns.txt.")

locs = new_locations(patterns_to_use)
freq_locs = make_freq_dict(locs)

f = open("New LOCATIONS_DICTIONARY.txt", 'w')
for popular in most_popular(freq_locs, 150):
    print(m.lemmatize(popular[1])[0])
    f.write(popular[1] + '\n')
f.close()