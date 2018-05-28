import simplejson as js
import re
import time, datetime


class JsonRead(object):
    """
    Class which implements all methods to read a JSON from a file and process it.
    """

    def __init__(self, filename):
        self.json = self.load_json(filename)

    def del_coments(self, data, ch="#"):
        """
        Delete all comments that exist in the input string
        :param data: String with the text to replace
        :param ch: Comment start character
        :return: String with all the comments deleted
        """
        output = ""
        for line in data.splitlines():
            if (line.find(ch) > -1):
                line = line[0:line.find(ch)]
            output = output + line + "\n"
        return output

    def get_field(self, data, field):
        """
        Takes a dict with nested lists and dicts, and searches all dicts for a key of the field provided.

        If the field is 'date', return the current timestamp.

        :param data: Dict with all the information
        :param field:  Key to be found
        :return: Array with the key values.
        """

        fields_found = []
        if field == 'date':
            st = datetime.datetime.fromtimestamp(time.time()).strftime('%d%B%y_%H-%M-%S')
            fields_found.append(st)
            return fields_found

        for key, value in data.iteritems():
            if key == field:
                if isinstance(value, list):
                    fields_found = fields_found + value
                else:
                    fields_found.append(value)
            elif isinstance(value, dict):
                results = self.get_field(value, field)
                for result in results:
                    fields_found.append(result)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.get_field(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)
        return fields_found

    def substitute_params(self, data, prejson, reg="<.*?>"):
        """
        Replaces all the variables in a dictionary with the value indicated in the dictionary itself.
        :param data: String with the dictionary
        :param prejson: JSON with the dictionary
        :param reg: Regex with the variables pattern
        :return: Dict with the variables substituted.
        """

        while len(re.findall(reg, data)) > 0:
            for match in re.findall(reg, data):
                m = match.replace('<', '').replace('>', '')
                data = data.replace(match, self.get_field(prejson, m)[0])
        return data

    def load_json(self, filename):
        """
        Method which load a JSON from a file and process it with all the previous methods.
        :param filename: Absolute File Path
        :return: JSON processed
        """
        if filename.find(".json") < 0:
            filename = filename + ".json"
        try:
            data = open(filename).read()
            data = self.del_coments(data)
            prejson = js.loads(data)
            data = self.substitute_params(data, prejson)
        except:
            print("ERROR: loading %s" % (filename))
            raise
        return js.loads(data)


if __name__ == "__main__":
    reader = JsonRead("configuration.json")
    print reader.json
