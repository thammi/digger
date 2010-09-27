import json
from warnings import warn
import os.path

def save_batch(item, data, file_name):
    if os.path.exists(file_name):
        # read in old data
        try:
            inp = file(file_name)
            batch = json.load(inp)
            inp.close()
        except:
            warn("Couldn't load old data")
            batch = {}
    else:
        batch = {}

    # insert new data
    batch[item] = data

    # writing back
    out = file(file_name, 'w')
    json.dump(batch, out)
    out.close()
