# ugly hack to get faster json
try:
    import cjson

    # emulate built-in json/simplejson
    class Json:
        def load(self, inp):
            return cjson.decode(inp.read())

        def loads(self, data):
            return cjson.decode(data)
        
        def dump(self, raw, outp):
            data = cjson.encode(raw)
            outp.write(data)

        def dumps(self, raw):
            return cjson.encode(raw)

    json = Json()
except:
    from warnings import warn
    warn("cjson not found, using slower json")
    import json

