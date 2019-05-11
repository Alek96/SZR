import csv


def csv_members_parse(infile):
    """
    format:
    surname   name   second_name   inactive   resignation   index
    bbbb      aaaa                 0          0             999999
    """
    result = []
    csv_reader = csv.reader(infile.splitlines(), delimiter=';')
    for row in csv_reader:
        if len(row) != 5 and len(row) != 6:
            raise ValueError('File format is incorrect')
        member = dict()
        member['surname'] = row[0]
        member['name'] = row[1]
        if len(row) == 6:
            member['second_name'] = row[2]
        member['inactive'] = row[-3]
        member['resignation'] = row[-2]
        member['index'] = row[-1]
        result.append(member)
    return result


def csv_subgroup_and_members_parse(infile):
    """
    format:
    index   name   surname   inactive   groups                 programs
    999999  bbbb   aaaa      0          CWI102, LAB102, WYK1   103B-ISP-IN (G2-IN000-ISP-I2-1030)
    """
    result = []
    csv_reader = csv.reader(infile.splitlines(), delimiter=';')
    for row in csv_reader:
        if len(row) != 6:
            raise ValueError('File format is incorrect')
        member = dict()
        member['index'] = row[0]
        member['name'] = row[1]
        member['surname'] = row[2]
        member['inactive'] = row[3]
        member['groups'] = str(row[4]).replace(", ", ",").split(",")
        member['programs'] = row[5]
        result.append(member)
    return result
