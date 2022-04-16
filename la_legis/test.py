import requests, re

get_votes_r = r'href="([^"]+)" target="_blank">Votes</a>'
regex_test = r''

root = 'http://legis.la.gov/legis/'
URL = 'http://legis.la.gov/legis/BillInfo.aspx?s=221ES&b=HB1&sbi=y'

ct = str(requests.get(URL).content)
a = re.search(get_votes_r, ct)
url = f'{root}{a.group(1)}'
print(requests.get(url).content)