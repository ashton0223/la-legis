import requests, re

HOUSE_URL = 'https://house.louisiana.gov/H_Reps/H_Reps_FullInfo'
HOUSE_EXT_URL = 'https://house.louisiana.gov/H_Reps/members.aspx?ID='
SENATE_URL = 'https://senate.la.gov/Senators_FullInfo'
SENATE_EXT_URL = 'https://senate.la.gov/smembers.aspx?ID='

name_regex = '<span id="body_ListView1_LASTFIRSTLabel_(\\d)+">([^<]*)<\\/span>'
district_regex = '<span id="body_ListView1_DISTRICTNUMBERLabel_(\\d)+">((\\w| |,|\\.|")*)<\\/span>'
party_regex = '<span id="body_ListView1_PARTYAFFILIATIONLabel_(\\d)+">([^<]*)<\\/span>'
last_name_regex = '[^ ]+'

class Lawmaker:
    def __init__(self, name, last_name, district, party, website):
        self.name = name
        self.last_name = last_name
        self.district = district
        self.party = party
        self.website = website

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
        name = self.house.name
        self.house.members = create_body(name, HOUSE_URL, HOUSE_EXT_URL)
        pass

    def create_senate(self):
        name = self.senate.name
        self.senate.members = create_body(name, SENATE_URL, SENATE_EXT_URL)
        pass

def get_full_names(page):
    ret = []
    res = re.findall(name_regex, page)
    for person in res:
        ret.append(person[2])
    return ret

def create_body(name, url, ext_url):
    members = []
    page = str(requests.get(url).content)

    mem_res = re.findall(name_regex, page)
    dist_res = re.findall(district_regex, page)
    party_res = re.findall(party_regex, page)

    for i in range(len(mem_res)):
        name = mem_res[i][1]
        last_name = re.match(last_name_regex, name)
        district = dist_res[i][1]
        party = party_res[i][1]
        website = ext_url + district
        members.append(Lawmaker(name, last_name, district, party, website))
    
    return members

l = Legis()
l.create_house()
l.create_senate()
print(l.house.members[4].party)