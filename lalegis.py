import requests, re, PyPDF2
from io import BytesIO

HOUSE_URL = 'https://house.louisiana.gov/H_Reps/H_Reps_FullInfo'
HOUSE_EXT_URL = 'https://house.louisiana.gov/H_Reps/members.aspx?ID='
HOUSE_SPRK_URL = 'https://house.louisiana.gov/H_Staff/H_Staff_Speaker'
SENATE_URL = 'https://senate.la.gov/Senators_FullInfo'
SENATE_EXT_URL = 'https://senate.la.gov/smembers.aspx?ID='
SENATE_PR_URL = 'https://senate.la.gov/Officers'

# Sample Senate bill
TEST_VOTE_URL = 'https://www.legis.la.gov/Legis/ViewDocument.aspx?d=1263950'

name_regex = r'<span id="body_ListView1_LASTFIRSTLabel_(\d)+">([^<]*)<\/span>'
district_regex = r'<span id="body_ListView1_DISTRICTNUMBERLabel_(\d)+">((\w| |,|\.|")*)<\/span>'
party_regex = r'<span id="body_ListView1_PARTYAFFILIATIONLabel_(\d)+">([^<]*)<\/span>'
last_name_regex = '[^,]+'
vote_regex = r'YEAS([^\d]*)\d{1,2}NAYS([^\d]*)\d{1,2}ABSENT([^\d]*)\d{1,2}'
speaker_regex = r'span>([^,]+), Speaker<'
pr_regex = r'Senator ([^<]+)<\/span'


class Bill:
    def __init__(self, url):
        self.url = url
        self.yeas = []
        self.nays = []
        self.absents = []
    
    def get_votes(self, lawmakers):
        (yeas, nays, absents) = get_vote_data(self.url)
        for lawmaker in lawmakers:
            bill_name = lawmaker.bill_name
            if re.search(f'{bill_name}[A-Z ]', yeas):
                self.yeas.append(bill_name)
                continue
            elif re.search(f'{bill_name}[A-Z ]', nays):
                self.nays.append(bill_name)
                continue
            elif re.search(f'{bill_name}[A-Z ]', absents):
                self.absents.append(bill_name)

class Lawmaker:
    def __init__(self, name, bill_name, district, party, website):
        self.name = name
        self.bill_name = bill_name
        self.district = district
        self.party = party
        self.website = website
        self.votes = []

class Body:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.bills = []
        self.speaker = None

    def add_lawmaker(self, lawmaker):
        self.members.append(lawmaker)
    
    # specific to the House
    def add_speaker(self, url):
        res = str(requests.get(url).content)
        match = re.search(speaker_regex, res)
        name = match.group(1)
        split = name.split(' ')
        bill_name = split[len(split) - 1]
        print(bill_name)

        for member in self.members:
            if member.bill_name == bill_name:
                self.speaker = member
                break
    
    # specific to the Senate
    def add_president(self, url):
        res = str(requests.get(url).content)
        match = re.search(pr_regex, res)
        name = match.group(1)
        split = name.split(' ')
        bill_name = split[len(split) - 1]
        print(bill_name)

        for member in self.members:
            if member.bill_name == bill_name:
                self.speaker = member # Named speaker for all bodies
                break

    def add_bill(self, url):
        new_bill = Bill(url)
        new_bill.get_votes(self.members)
        self.bills.append(new_bill)

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
    double_bill_names = []
    page = str(requests.get(url).content)

    mem_res = re.findall(name_regex, page)
    dist_res = re.findall(district_regex, page)
    party_res = re.findall(party_regex, page)

    for i in range(len(mem_res)):
        name = mem_res[i][1]
        bill_name = re.search(last_name_regex, name).group(0)

        # Check for multiple people having the same last name
        for i in range(len(members)):
            if members[i].bill_name == bill_name:
                print('double!',bill_name)
                double_bill_names.append(bill_name)
                offset = len(members[i].bill_name) + 2
                o_name = members[i].name # doesn't go off screen
                members[i].bill_name = f'{bill_name}, {o_name[offset]}.'
                bill_name = f'{bill_name}, {name[offset]}.'
                continue
        if bill_name in double_bill_names:
            offset = len(bill_name) + 2
            bill_name = f'{bill_name}, {name[offset]}.'

        district = dist_res[i][1]
        party = party_res[i][1]
        website = f'{ext_url}{district}'
        members.append(Lawmaker(name, bill_name, district, party, website))
    
    return members

def get_vote_content(vote_url):
    ret = ''

    res = requests.get(vote_url).content
    with BytesIO(res) as data:
        read_pdf = PyPDF2.PdfFileReader(data)

        for page in range(read_pdf.getNumPages()):
            txt = read_pdf.getPage(page).extractText()
            ret += txt
    return ret

def get_vote_data(vote_url):
    content = get_vote_content(vote_url)
    split_content = re.search(vote_regex, content)
    yeas = split_content.group(1)
    nays = split_content.group(2)
    absents = split_content.group(3)
    return (yeas, nays, absents)

def main():
    l = Legis()
    l.create_house()
    l.create_senate()

    print(l.house.members[4].party)
    for member in l.senate.members:
        print(member.bill_name)
    l.senate.add_bill(TEST_VOTE_URL)
    print(len(l.senate.bills[0].yeas),len(l.senate.bills[0].nays))
    l.house.add_speaker(HOUSE_SPRK_URL)
    print(l.house.speaker.name)
    l.senate.add_president(SENATE_PR_URL)
    print(l.senate.speaker.name)

if __name__ == '__main__':
    main()