__author__ = 'devinbarry@users.noreply.github.com'

import re
from collections import OrderedDict
from dateutil.parser import parse


def _parse_line_into_date_and_comment(file_line):
    """Split the string into the two parts."""
    to_find = ' +1300'
    index = file_line.find(to_find) + len(to_find)
    # print("'{}'".format(l))
    return [file_line[:index].strip(), file_line[index:].strip()]


def _parse_date_string_into_date(date_string):
    return parse(date_string).date()


def _get_nums_from_comment(comment):
    nums_out = re.findall(r'\d{4}', comment)
    return nums_out


def _get_refs_from_comment(comment):
    list_out = re.findall(r'refs #\d{4}', comment, re.IGNORECASE)
    return list_out


def _remove_words_from_string(string, word_list):
    new_word_list = set(word_list)
    for word in new_word_list:
        string = string.replace(word, '')
    return string


def _get_pertinant_words(comment):
    refs = _get_refs_from_comment(comment)
    new_comment = _remove_words_from_string(comment, refs)
    # Probably very little will ever happen here
    nums = _get_nums_from_comment(new_comment)
    return refs + nums


if __name__ == '__main__':
    venv = "source /Library/Frameworks/Python.framework/Versions/2.7/bin/virtualenvwrapper.sh"

    f = open('devinbarry_git_log_output.txt', 'r')

    output = OrderedDict()


    count = 0
    line = f.readline()
    while line != '':
        count += 1
        line = f.readline()

        date_string, comment = _parse_line_into_date_and_comment(line)
        date = _parse_date_string_into_date(date_string)
        words = _get_pertinant_words(comment)
        try:
            output[date].extend(words)
        except KeyError:
            output[date] = list()
            output[date].extend(words)

    print('Processed {} lines'.format(count))
    f.close()

    for k in output.keys():
        # remove dupes
        output[k] = list(set(output[k]))

    for k in output.keys():
        print('{}: {}'.format(k, output[k]))