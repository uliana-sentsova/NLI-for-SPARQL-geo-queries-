
from Bootstrap import most_popular



# counter = 0
# freq = dict()
# for line in f:
#     line = line.split()
#     for word in line:
#         freq[word] = freq.get(word, 0) + 1
#     counter +=1
#     if counter % 1000000 == 0:
#         print("Обработано ", counter, " строк.")
# print(counter)
# f.close()
# f = open("Counting.csv", 'w')
# for key in freq:
#     if freq[key] > 2:
#         f.write(key + ', ' + str(freq[key]) + '\n')
# f.close()


freq = dict()
f = open("Counting.csv", 'r', encoding="utf-8")
for line in f:
    line = line.split(", ")
    if int(line[1]) > 100 and len(line[0]) > 2:
        freq[line[0]] = int(line[1])
f.close()
print(len(freq))
for word in most_popular(freq, n = 4000):
    print(word)