import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

pwd = os.getcwd()
def open_pattern(pattern_name):
    os.chdir(pwd + "/Patterns")
    with open(pattern_name + ".txt", 'r') as pattern:
        pattern = pattern.read()
    return pattern

def make_query_to_DB(subject, pattern):
    query_pattern = re.sub("SUBJECT", subject, pattern)
    query_pattern = re.sub("PREDICATE", "dbo:country", query_pattern)
    print(query_pattern)
    sparql.setQuery(query_pattern)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    final = []
    for result in results["results"]["bindings"]:
        final.append(result["name"]["value"])
    # for f in final:
    #     print(f)
    return final[0]

x = make_query_to_DB("Moscow", open_pattern("pattern5"))
print(x)
# query_pattern = open_pattern("pattern5")
# subject = "<http://dbpedia.org/resource/" + "Buena_Park,_California" + ">"
# query_pattern = re.sub("SUBJECT", subject, query_pattern)
# query_pattern = re.sub("PREDICATE", "dbo:country", query_pattern)

# print(query_pattern)
#
# sparql.setQuery(query_pattern)
# sparql.setReturnFormat(JSON)
# results = sparql.query().convert()
# final = []
# for result in results["results"]["bindings"]:
#     final.append(result["name"]["value"])
# for f in final:
#     print(f)

