import json
from warnings import warn
import os.path

def change_batch(change, file_name):
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

    # apply changes
    change(batch)

    # writing back
    out = file(file_name, 'w')
    json.dump(batch, out)
    out.close()

def update_batch(update, file_name):
    change_batch(lambda batch: batch.update(update), file_name)

def save_batch(item, data, file_name):
    def save(batch):
        batch[item] = data

    change_batch(save, file_name)

