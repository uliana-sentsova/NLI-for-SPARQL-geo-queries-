import Constructor as constructor

with open("evaluation_set.txt", "r", encoding="utf-8") as evaluation_set, open("result.txt", 'a') as result:

    freq_dict = []

    for query in evaluation_set:
        query = query.strip()
        freq_dict.append(query)
    print(len(list(set(freq_dict))))

    for query in freq_dict:

        print("ЗАПРОС:", query)
        print("ПРЕОБРАЗОВАНИЕ В SPARQL:")
        try:
            res = constructor.make_query(query,)
        except Exception as err:
            print(err)

        correct = ""
        answer = ""
        reason = ""
        while True:
            answer = input("Запрос построен правильно?\t")
            if answer == "n" or answer == "y" or answer=="break":
                break

        if answer == "n":
            reason = input("В чём заключается ошибка?")
            correct = "1"
            result.write(query + "\t0\t" + reason + "\n")
        elif answer == "y":
            result.write(query + "\t1\t" + "NA" + "\n")
        else:
            break