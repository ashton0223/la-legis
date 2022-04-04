import requests, re

HOUSE_URL = 'https://house.louisiana.gov/H_Reps/H_Reps_FullInfo'
HOUSE_PARTY = 'https://house.louisiana.gov/H_Reps/H_Reps_ByParty'
HOUSE_DISTRICT = 'https://house.louisiana.gov/H_Reps/H_Reps_ByDistrict'
SENATE_URL = 'https://senate.la.gov/Senators_FullInfo'
SENATE_DISTRICT = 'https://senate.la.gov/Senators_ByDistrict'

regex_string = '<span id="body_ListView1_LASTFIRSTLabel_(\\d)+">((\\w| |,|\\.|")*)<\\/span>'

class Lawmaker:
    def __init__(self):
        self.name = ''
        self.last_name = ''
        self.district = ''
        self.party = ''
        self.website = ''

class Body:
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_lawmaker(self, lawmaker):
        self.members.append(lawmaker)

class Legis:
    def __init__(self):
        self.house = Body('House')
        self.senate = Body('Senate')
    
    def create_house(self):
        pass

    def create_senate(self):
        sen_page = str(requests.get(SENATE_URL).content)
        full_names = ""
        pass

def get_full_names(page):
    ret = []
    res = re.findall(regex_string, page)
    for person in res:
        ret.append(person[2])
    return ret


rep_page = str(requests.get(HOUSE_URL).content)

#sen_regex = re.findall(regex_string, sen_page)
rep_regex = re.findall(regex_string, rep_page)

for rep in rep_regex:
    print('a')
    print(rep[1])
