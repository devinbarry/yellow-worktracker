__author__ = 'devinbarry@users.noreply.github.com'

import re
import click
from datetime import datetime, timedelta
from collections import OrderedDict
from dateutil.parser import parse
from redmine import Redmine
from pandas import DataFrame
from pyactiveresource.activeresource import ActiveResource

USERNAME = 'test'
PASSWORD = 'test'


@click.command()
@click.option('--username', prompt='Redmine username', help='Redmine username', required=True)
@click.option('--password', prompt='Redmine password', help='Redmine password', required=True)
@click.option('--file', prompt='Git log export text file',
              help='The file which you have exported git log to', required=True)
def main(username, password, file):
    USERNAME = username
    PASSWORD = password
    _main(file_name=file)


class Issue(ActiveResource):
    _site = 'http://redmine.finda.co.nz'
    _user = USERNAME
    _password = PASSWORD


def _parse_line_into_date_and_comment(file_line, to_find=' +1300'):
    """Split the string into the two parts."""
    index = file_line.find(to_find) + len(to_find)

    date = file_line[:index].strip()
    comment = file_line[index:].strip()

    # print("{}: '{}'".format(len(date), date))
    if len(date) < 29:
        return _parse_line_into_date_and_comment(file_line, to_find=' +1200')

    return [date, comment]


def _check_date_string(date_string):
    year_2014 = '2014' in date_string
    year_2013 = '2013' in date_string
    assert year_2013 or year_2014
    mon = 'Mon' in date_string
    tue = 'Tue' in date_string
    wed = 'Wed' in date_string
    thu = 'Thu' in date_string
    fri = 'Fri' in date_string
    assert mon or tue or wed or thu or fri


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


def _get_number(number_string):
    if len(number_string) == 4:
        return int(number_string)
    else:
        return int(number_string[-4:])


def _build_list_of_numbers(output_values):
    pure_num = []
    for number in output_values:
        pure_num.append(_get_number(number))
    return list(set(pure_num))


def _build_list_of_subjects(dev_issues, num_list):
    subjects = []
    for number in num_list:
        issue = dev_issues.get(resource_id=number)
        if issue is not None:
            subjects.append(issue.subject)
        else:
            issue = Issue.find(number)
            if issue is not None:
                subjects.append(issue.subject)
    return subjects


def _write_columns_to_excel(c1, c2, c3):
    weekday_list = _build_list_of_weekdays()
    padded_c2, padded_c3 = _pad_other_lists(weekday_list, c1, c2, c3)

    dtstr = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = 'work_log_{}.xlsx'.format(dtstr)
    df = DataFrame({'Date': weekday_list, 'Ticket Name': padded_c2, 'Ticket Data': padded_c3})
    # print(df)
    df.to_excel(file_name, sheet_name='sheet1', index=False)


def _build_list_of_weekdays():
    weekday_list = list()
    start_date = datetime(2013, 10, 7)  # Monday 7th Oct 2013
    date = start_date
    count = 0
    while date < datetime(2014, 5, 31):
        weekday_list.append(date.date())
        count += 1
        date += timedelta(days=1)
        if count == 7:
            count = 0
            weekday_list.append('')
    return weekday_list


def _pad_other_lists(weekday_list, date, c1, c2):
    padded_c1 = list()
    padded_c2 = list()
    counter_max = len(date)
    counter = 0
    for weekday_value in weekday_list:
        if weekday_value != '':
            # We have a date
            # Test if we have reached the end of the data
            if counter == counter_max:
                # Pad because there is no more data
                padded_c1.append('')
                padded_c2.append('')
                continue

            if weekday_value == date[counter]:
                padded_c1.append(c1[counter])
                padded_c2.append(c2[counter])
                counter += 1
            else:
                # Pad if we cant find a value for that date
                padded_c1.append('')
                padded_c2.append('')
        else:
            # Pad if we skip a line for the week splits
            padded_c1.append('')
            padded_c2.append('')

    return padded_c1, padded_c2


def _main(file_name):
    f = open(file_name, 'r')

    output = OrderedDict()

    server = Redmine('http://redmine.finda.co.nz', username=USERNAME, password=PASSWORD)
    project = server.project.get('sem')
    devin = server.user.get('current')
    dev_issues = server.issue.filter(project_id=project.id)

    # for issue in dev_issues:
    #     print('{} - {}'.format(issue.id, issue.subject))

    count = 0
    line = f.readline()
    while line != '':
        count += 1
        line = f.readline()
        line = line.strip()

        # Skip blank lines
        if not line:
            continue

        date_string, comment = _parse_line_into_date_and_comment(line)
        _check_date_string(date_string)
        # print("{}: '{}'".format(len(date_string), date_string))

        actual_date = parse(date_string).date()
        words = _get_pertinant_words(comment)

        if actual_date > datetime(2014, 4, 14).date():
            print('WTFWTFWTFWTFWTFTWTFETFTETF')
            print(date_string)
            print(line)

        try:
            output[actual_date].extend(words)
        except KeyError:
            output[actual_date] = list()
            output[actual_date].extend(words)

    print('Processed {} lines'.format(count))
    f.close()

    for k in output.keys():
        # remove dupes
        output[k] = list(set(output[k]))

    # for k in output.keys():
    #     print('{}: {}'.format(k, output[k]))

    column1 = list()
    column2 = list()
    column3 = list()

    # Start with oldest at the top of spreadsheet
    for k in reversed(output.keys()):
        num_list = _build_list_of_numbers(output[k])
        subject_list = _build_list_of_subjects(dev_issues, num_list)
        # print('{}: {}'.format(k, subject_list))
        column1.append(k)
        column2.append('; '.join(subject_list))  # Convert list to string
        column3.append('; '.join(output[k]))  # Convert list to string

    _write_columns_to_excel(column1, column2, column3)


if __name__ == '__main__':
    venv = "source /Library/Frameworks/Python.framework/Versions/2.7/bin/virtualenvwrapper.sh"
    main()
