result = []
filename = "MAIN_ONTO_rivers.txt"
with open("PARSED.txt", 'r', encoding="utf-8") as f:
    for line in f:
        line = line.split("\t")
        line = [l.strip() for l in line]
        result.append(line)
print(len(result))
dictionary = {}
checked = []
rest = []
for line in result:
    try:
        if line[1] not in checked:
            checked.append(line[1])
            dictionary[line[1]] = line[0]
        else:
            rest.append(line)
    except IndexError as err:
        print(err)
        print(line)

print(len(dictionary))
print(len(rest))


for r in rest:
    string = dictionary[r[1]]
    string = string.split(",")
    normalized = string[-1]
    string = string[:-1]
    string_2 = r[0].split(",")
    string_2 = string_2[1:-1]
    for word in string_2:
        if word and word not in string:
            string.append(word)
    string.append(normalized)
    dictionary[r[1]] = ",".join(string)
print(len(dictionary))

with open(filename, "w") as f:
    for key in dictionary:
        f.write(dictionary[key] + "\t" + key + "\n")