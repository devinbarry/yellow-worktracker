__author__ = 'devinbarry@users.noreply.github.com'


if __name__ == '__main__':
    venv = "source /Library/Frameworks/Python.framework/Versions/2.7/bin/virtualenvwrapper.sh"

    f = open('devinbarry_git_log_output.txt', 'r')


    count = 0
    line = f.readline()
    while line != '':
        count += 1
        line = f.readline()

    print('Count: {}'.format(count))
    f.close()


def _parse_line_into_date_and_comment(file_line):
    """Split the string into the two parts."""
    to_find = ' +1300'
    index = file_line.find(to_find) + len(to_find)
    # print("'{}'".format(l))
    return [file_line[:index].strip(), file_line[index:].strip()]


def _parse_date_string_into_date(date_string):
    return None