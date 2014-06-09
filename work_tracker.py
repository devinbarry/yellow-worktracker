__author__ = 'devinbarry@users.noreply.github.com'

import re
import os.path
import click
from tqdm import *
from datetime import date
from datetime import datetime, timedelta
from collections import OrderedDict
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from redmine import Redmine
from pandas import DataFrame
from pyactiveresource.activeresource import ActiveResource

USERNAME = 'test'
PASSWORD = 'test'


class Issue(ActiveResource):
    _site = 'http://redmine.finda.co.nz'
    # _user = USERNAME
    # _password = PASSWORD


@click.command()
@click.option('--username', prompt='Redmine username', help='Redmine username', required=True)
@click.option('--password', prompt='Redmine password', help='Redmine password', required=True)
@click.option('--file', prompt='Git log export text file',
              help='The file which you have exported git log to', required=True)
def main(username, password, file):
    global USERNAME
    global PASSWORD
    # Set the globals for username and password from the input arguments
    USERNAME = username
    PASSWORD = password

    # Set the username and password for the Issue class
    Issue._user = USERNAME
    Issue._password = PASSWORD
    _main(file_name=file)


def _main(file_name):
    """
    Runs the two main sections of the program.
    :param file_name: The file name of the git log file to process
    :return:
    """
    if os.path.exists(file_name):
        output = _read_and_process_file(file_name)
        _process_output_dictionary(output)
    else:
        print('File does not exist!')


def _get_file_modification_date(file_name):
    """
    Get the last modification date of the file
    :param file_name: any file
    :return: datetime.date()
    """
    dttf = datetime.fromtimestamp(os.path.getmtime(file_name))
    return dttf.date()


def _parse_line_into_date_and_comment(file_line, to_find=' +1300'):
    """
    Split the string into the two parts: The date found in the comment
    and the actual comment part of the comment.
    :param file_line:
    :param to_find:
    :return:
    """
    index = file_line.find(to_find) + len(to_find)

    date = file_line[:index].strip()
    comment = file_line[index:].strip()

    # print("{}: '{}'".format(len(date), date))
    # TODO test to make sure this doesn't loop forever
    if len(date) < 29:
        return _parse_line_into_date_and_comment(file_line, to_find=' +1200')

    return [date, comment]


def _check_date_string(date_string):
    """Make sure that the date string is from 2013 or 2014
    and make sure that the day is a weekday.
    """
    # TODO improve hardcoded years here
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
    """
    Looks for strings containing four numeric characters in a row.
    :param comment: The message part of the commit message
    :return:
    """
    nums_out = re.findall(r'\d{4}', comment)
    return nums_out


def _get_refs_from_comment(comment):
    """
    Looks for strings of the format "Refs #xxxx" where x is a numeric character
    :param comment: The message part of the commit message
    :return:
    """
    list_out = re.findall(r'refs #\d{4}', comment, re.IGNORECASE)
    return list_out


def _remove_words_from_string(string, word_list):
    """
    Remove all words in the word_list from the string. Return the modified string.
    :param string: The original string
    :param word_list: The list of words to remove
    :return: The modified string
    """
    new_word_list = set(word_list)
    for word in new_word_list:
        string = string.replace(word, '')
    return string


def _get_pertinant_words(comment):
    """
    Finds the important words and phrases from the commit message.
    Important words and phrases are 'Refs #xxxx' or simply a
    substring containing 4 sequential numeric characters
    :param comment: The message part of the commit message
    :return:
    """
    refs = _get_refs_from_comment(comment)
    new_comment = _remove_words_from_string(comment, refs)
    # Probably very little will ever happen here
    nums = _get_nums_from_comment(new_comment)
    return refs + nums


def _get_number(number_string):
    """
    Retrieve an integer representation of the number
    contained in the string. Two input formats are possible:
    either Refs #xxxx
    or xxxx
    Where x is a numeric character
    :param number_string: The input string
    :return: integer representing the number found
    """
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
    """Fetch issues from Redmine and build a list of subjects."""
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
    weekday_list = _build_date_list_weeks()
    padded_c2, padded_c3 = _pad_other_lists(weekday_list, c1, c2, c3)

    dtstr = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = 'output/work_log_{}.xlsx'.format(dtstr)
    df = DataFrame({'Date': weekday_list, 'Ticket Name': padded_c2, 'Ticket Data': padded_c3})
    # print(df)
    df.to_excel(file_name, sheet_name='sheet1', index=False)


def _build_date_list_weeks(start_date=datetime(2013, 10, 7)):
    """
    Build a list of all dates from start_date through to two weeks
    from now.
    :param start_date: The earliest date in the date list
    :return:
    """
    weekday_list = list()
    end_date = datetime.now() + relativedelta(weeks=2)  # End date is two weeks from now
    date_ = start_date  # Default is Monday 7th Oct 2013
    count = 0
    while date_ < end_date:

        # Add the next date to the list
        weekday_list.append(date_.date())
        count += 1
        date_ += timedelta(days=1)

        # Each week create a seperation line
        if count == 7:
            count = 0
            weekday_list.append('')
    return weekday_list


def _pad_other_lists(weekday_list, date_, c1, c2):
    """
    Pad the other lists in the same way as the date list is padded.
    :param weekday_list:
    :param date_:
    :param c1:
    :param c2:
    :return:
    """
    padded_c1 = list()
    padded_c2 = list()
    counter_max = len(date_)
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

            if weekday_value == date_[counter]:
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


def _get_words_and_date(line, file_modification_date):
    """
    Fetch the important words and the date from the line string.
    :param line:
    :return:
    """
    date_string, comment = _parse_line_into_date_and_comment(line)
    _check_date_string(date_string)
    # print("{}: '{}'".format(len(date_string), date_string))

    actual_date = parse(date_string).date()
    words = _get_pertinant_words(comment)

    # This checks that no dates are after the generation time of the file
    if actual_date > file_modification_date:
        print('WTFWTFWTFWTFWTFTWTFETFTETF')
        print(date_string)
        print(line)

    return actual_date, words


def _read_and_process_file(file_name):
    """
    Read the input file and process it into a dictionary
    where the date associated with each line is the the dictionary key
    and the text associated with each line is the dictionary value.
    :param file_name:
    :return: the output dictionary
    """
    modified = _get_file_modification_date(file_name)

    f = open(file_name, 'r')
    output = OrderedDict()

    # Process file line by line
    count = 0
    line = ' '
    while line != '':
        # Strip whitespace from lines we read
        line = f.readline().strip()
        count += 1  # Increment the line count

        # Skip blank lines
        if not line:
            continue

        # Process line into a date and "important words"
        actual_date, words = _get_words_and_date(line, modified)

        # Build the dictionary
        try:
            output[actual_date].extend(words)
        except KeyError:
            output[actual_date] = list()
            output[actual_date].extend(words)

    print('Processed {} lines'.format(count))
    f.close()

    return output


def _process_output_dictionary(output):
    """
    Output is the processed dictionary of lines that comes from the
    git output file.
    :param output:
    :return:
    """
    server = Redmine('http://redmine.finda.co.nz', username=USERNAME, password=PASSWORD)
    project = server.project.get('sem')
    devin = server.user.get('current')
    dev_issues = server.issue.filter(project_id=project.id)

    # for issue in dev_issues:
    #     print('{} - {}'.format(issue.id, issue.subject))

    for k in output.keys():
        # remove dupes
        output[k] = list(set(output[k]))

    # for k in output.keys():
    #     print('{}: {}'.format(k, output[k]))

    column1 = list()
    column2 = list()
    column3 = list()

    # Start with oldest at the top of spreadsheet
    reverse_keys = reversed(output.keys())
    length = len(output.keys())
    print('Fetching data from Redmine. [{0} keys]'.format(length))

    for k in tqdm(reverse_keys, total=length):
        num_list = _build_list_of_numbers(output[k])
        subject_list = _build_list_of_subjects(dev_issues, num_list)
        # print('{}: {}'.format(k, subject_list))
        column1.append(k)
        column2.append('; '.join(subject_list))  # Convert list to string
        column3.append('; '.join(output[k]))  # Convert list to string

    print('Created spreadsheet data. Writing to spreadsheet....')
    _write_columns_to_excel(column1, column2, column3)


if __name__ == '__main__':
    venv = "source /Library/Frameworks/Python.framework/Versions/2.7/bin/virtualenvwrapper.sh"
    main()
