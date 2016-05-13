import re
from pymystem3 import Mystem
m = Mystem()
import os
PWD = os.getcwd()
os.chdir(PWD + "/Cities")
print(os.getcwd())
dictionary = dict()

count = 0
result = []
with open("А.tsv", 'r', encoding="utf-8") as f:
    for line in f:
        line = line.split("\t")

        line = [l.strip("\"") for l in line]
        normalized = ""
        lemmatized = ""

        if len(line) > 4:
            line = line[:4]
        if len(line) < 4:
            print("Значение меньше 4", line)
            continue

        city_name, value, country, abstract = [l for l in line]

        country = m.lemmatize(country)
        country = "".join(country).strip()

        try:
            value = value.split("resource/")[1]
        except IndexError:
            print(line)
            pass

        x = re.findall("\s—\s(остров|архиепархия|архипелаг|город|муниципалитет|округ|графство|эмират|община|регион|штат|насел[её]нный\sпункт|"
                       "станица|коммуна|район|община|село|деревня|столица|пос[её]лок|провинция)\s.+?[,\.]",
                       abstract, re.IGNORECASE)
        descriptors = []
        try:
            descriptors.append(x[0])
        except IndexError:
            pass
        if " — остров" in line:
            continue
        else:
            if "(" in city_name:
                city_name = city_name.split("(")
                normalized = city_name[0]
                lemmatized = m.lemmatize(normalized)
                lemmatized = "".join(lemmatized).strip()
                rest = city_name[1].strip(")")
                if "," in rest:
                    x = rest.split(",")
                    for x in rest.split(","):
                        x = "".join(m.lemmatize(x)).strip()
                        descriptors.append(x)
                else:
                    if len(rest.split()) == 1:
                        x = m.lemmatize(rest)
                        x = "".join(x)
                        descriptors.append(x.strip())
                    else:
                        rest = m.lemmatize(rest)
                        rest = [r for r in rest if r != "в" and r != "и"]
                        rest = "".join(rest).strip()
                        descriptors.append(rest)
            elif (",") in city_name:
                city_name = city_name.split(",")
                normalized = city_name[0]
                city_name = m.lemmatize("".join(city_name))
                lemmatized = "".join(city_name)
                for x in city_name[1:]:
                    descriptors.append(x)

            else:
                normalized = city_name
                city_name = m.lemmatize(city_name)
                lemmatized = "".join(city_name).strip()
        # print("NORM: ", normalized, ", LEMM: ", lemmatized, ", COUNTRY: ", country, ", DESCR: ", set(descriptors), ", VALUE: ", value)
        descriptors = list(set(descriptors))
        descriptors = ",".join(descriptors)
        if descriptors:
            string = lemmatized.lower() + "," + country + "," + descriptors + "," + normalized
        else:
            string = lemmatized.lower() + "," + country + "," + normalized
        result.append(string + "\t" + value)

result = list(set(result))


with open("RESULT1.txt", "w") as target_file:
    for line in result:
        target_file.write(line + "\n")