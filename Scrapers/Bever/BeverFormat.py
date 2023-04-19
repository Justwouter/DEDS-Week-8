import json
import os
outfile = os.path.dirname(__file__)+"/output/data"


def read_json_file(filename):
    with open(filename) as file:
        data = json.load(file)
    return data

print(read_json_file(outfile+".json"))