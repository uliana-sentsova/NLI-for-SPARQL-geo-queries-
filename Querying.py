import Constructor as constructor

total_count = 0
accept = 0
reject = 0
location_not_found = 0
keyword_not_found = 0
multiple_locations = 0
unknown_error = 0

with open("evaluation_set.txt", "r", encoding="utf-8") as evaluation_set, open("result.txt", 'w') as result:
    for query in evaluation_set:
        query = query.strip()

        try:
            res = constructor.make_query(query)
            result.write(query + "\n")
            result.write(res + "\n")
            result.write("====================================================================" + "\n")
            accept += 1
        except constructor.LocationNotFoundError as err:
            location_not_found += 1
            reject += 1
            print("Запрос не выполнен: не найдена локация. Запрос: ", query)
        except constructor.KeywordNotFoundError as err:
            keyword_not_found += 1
            reject += 1
            print("Запрос не выполнен: не найден предикат. Запрос: ", query)
        except constructor.MultipleLocationError:
            print("Запрос не выполнен: больше двух локаций в запросе. Запрос: ", query)
            multiple_locations += 1
            reject += 1
        except Exception as err:
            print("Неизвестная ошибка. Запрос: ", query)
            print("Ошибка: ", err)
            unknown_error += 1
            reject += 1
        finally:
            total_count += 1


print("Количество корректно обработанных запросов: {0}.".format(accept))
print("Количество некорректно обработанных запросов: {0}.".format(reject))
print("Количество запросов с ненайденными локациями: {0}.".format(location_not_found))
print("Количество запросов с ненайденными ключевыми словами: {0}.".format(keyword_not_found))
print("Количество запросов с неизвестной ошибкой: {0}.".format(unknown_error))