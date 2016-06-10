import Constructor as constructor


accept = 0
reject = 0

with open("evaluation_set.txt", "r", encoding="utf-8") as evaluation_set:
    for query in evaluation_set:
        query = query.strip()
        try:
            constructor.make_query(query)
            accept += 1
        except Exception as err:
            print("Запрос не выполнен.")
            print("Ошибка: ", err)
            reject += 1

print("Количество корректно обработанных запросов: ", accept, ".")
print("Количество некорректно обработанных запросов: ", reject, ".")