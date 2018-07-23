import requests
import json;
from bs4 import BeautifulSoup

def getGradeDetails(degreeId):
    r = requests.get('https://anabin.kmk.org/index.php?eID=user_anabin_abschluesse&conf=abschluesse&uid='+degreeId+'&_=1529927449342')

    soup = BeautifulSoup(r.text, 'html.parser')
    result = {}
    result['details'] = tableContentToArray(soup)
    instituteTable = soup.findAll("table", {"id": "abschluss-institutionen"});
    if not instituteTable :
        return []
    instituteId = instituteTable[0].findAll("tr",{"class": "detailLink-institutionen"});
    instituteId = instituteId[0].get('data')
    result['university'] = getInstituteData(instituteId)
    return result

def getInstituteData(uid):
    r = requests.get('https://anabin.kmk.org/index.php?eID=user_anabin_institutionen&conf=institutionen&uid='+uid+'&_=1529928418426')
    soup = BeautifulSoup(r.text, 'html.parser')
    accordion = soup.findAll("div", {"id": "accordion"});
    table = accordion[0].findAll("table");
    return tableContentToArray(table[0]);

def tableContentToArray(table):
    divs = table.findAll("td", {"class": "label"})
    result = {}
    for d in divs:
        td = d.parent.findAll('td');
        result[td[0].text] = td[1].text
    return result

def addToContent(key,placeholder,data):
    return (data[key] if key in data else placeholder)

def writeToCSV(data):
    file = open('wikidata_raw.csv','w')
    file.write('abschlussID;Abschluss;Abschlusstyp;Dauer Min;'+
        'Dauer Max;Klasse;Studienrichtung;Land;KomischeZahl1;KomischeZahl2;'+
        'd_Abschluss;d_Abkürzung;d_AbschlussTyp;d_StudienRichtung;d_Abschlussklasse;d_Kommentar;un_Langname;un_Abkürzung;un_Name auf Deutsch;un_Anschrift;un_Telefon;un_Fax;un_E-Mail;un_Homepage;un_Kommentar'
        +'\n')

    for rs in data:
        content = rs[1]+';'+rs[2]+';'+rs[3]+';'+rs[4]+';'+rs[5]+';'+rs[6]+';'+rs[7]+';'+rs[8]+';'+rs[9]+';'+rs[10]+';'
        if not rs[11]:
            content = content + ';;;;;;;;;;;;;\n'
        else:
            content = content + rs[11]['details']['Abschluss']+';'
            content = content + rs[11]['details']['Abkürzung']+';'
            content = content + rs[11]['details']['Abschlusstyp']+';';
            content = content + rs[11]['details']['Studienrichtung']+';'
            content = content + rs[11]['details']['Abschlussklasse']+';'
            content = content + addToContent('Kommentar','',rs[11]['details'])+';'

            content = content + rs[11]['university']['Langname']+';'
            content = content + rs[11]['university']['Abkürzung']+';'
            content = content + rs[11]['university']['Name auf Deutsch']+';'
            content = content + '\n'+rs[11]['university']['Anschrift'].replace("<br>", "").replace("\n", " ")+'\n'+';'
            content = content + rs[11]['university']['Telefon']+';'
            content = content + addToContent('Fax','',rs[11]['university'])+';'
            content = content + addToContent('E-Mail','',rs[11]['university'])+';'
            content = content + addToContent('Homepage','',rs[11]['university'])+';'
            content = content + '\n'+rs[11]['university']['Kommentar'].replace("<br>", "").replace("\n", " ").replace("\n", " ")+'\n'+''
            content = content + '\n'
            print('###START###')
            print(rs[11]['university']['Anschrift'].replace("\n", ""))
            print('###ENDE###')
        file.write(content)

    file.close()

def main():
    print('Request Page...')
    r = requests.get('https://anabin.kmk.org/index.php?eID=user_anabin_abschluesse&conf=abschlussergebnisliste&sEcho=6&iColumns=11&iDisplayStart=0&iDisplayLength=100&bRegex=false&sSearch_8=Island&iSortingCols=1&iSortCol_0=2&sSortDir_0=asc&land=18')
    j = json.loads(r.text)

    #data = j['aaData']
    for d in j['aaData']:
        d.append(getGradeDetails(d[1]))

    writeToCSV(j['aaData'])
    return

main()
