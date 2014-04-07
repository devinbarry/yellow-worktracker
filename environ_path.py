__author__ = 'devinbarry@users.noreply.github.com'


def _check_duplicates_in_path():
    """Check the $PATH environmental variable for duplicates."""
    import os

    path = os.environ['PATH']
    path_list = [piece for piece in path.split(":")]

    print('duplicates: {} items'.format(len(path_list)-len(set(path_list))))

    path_count = {part: 0 for part in set(path_list)}

    # Build new path with only unique path parts
    new_path = ''

    for i in range(len(path_list)):
        if not path_count[path_list[i]]:
            new_path += ':{}'.format(path_list[i])
            path_count[path_list[i]] += 1

    for v in path_count.values():
        assert v == 1

    print(new_path)

    # This is the current (07/04/14) default path
    "/Library/Frameworks/Python.framework/Versions/2.7/bin:/Library/Frameworks/Python.framework/Versions/3.4/bin:/opt/local/bin:/opt/local/sbin:/usr/local/bin:/usr/local/sbin:/Library/Frameworks/Python.framework/Versions/2.7/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/git/bin"



if __name__ == '__main__':
    _check_duplicates_in_path()