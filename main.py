import xmltodict
import requests
import xml.dom.minidom
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('PUBMED_API_KEY')

# gets the path to reference the dataset
# ADD THE PATH TO pubmed_articles.xml
findingPath = "#"

# takes the xml document from the path and starts the parsing operation
tree = ET.parse(findingPath)

# gets the root tag for the document
findingRootTag = tree.getroot()

titlesArray = []

# loops through the document and finds the 'ArticleTitle' tag which holds
# the titles of the articles, and stores it as theTitles
for theTitles in findingRootTag.iter('ArticleTitle'):
    # if the title does not start with Re: and RE: then add it to the titlesArray
    if not theTitles.text.startswith("Re:") and not theTitles.text.startswith("RE:"):
        titlesArray.append(theTitles.text)

idsArray = []

# loops through the titlesArray
for i in range(len(titlesArray)):

    # url used to search the PubMed database using E-Utilities API each iteration, will search for a different title
    # ADD YOUR API KEY
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={titlesArray[i]}&field=title&api_key=api_key"

    # sends a POST request to the sever using the url
    idRequest = requests.post(url)

    # stores the content of the response to the request
    xmlResponse = idRequest.content

    # parse xmlResponse and stores in dataBase
    dataBase = xmltodict.parse(xmlResponse)

    # if the article does not have an ID, return a 0
    # if there are multiple IDs for an article, return the second item, index[1]
    if dataBase['eSearchResult']['IdList'] is None:
        returnID = 0
    else:
        if isinstance(dataBase['eSearchResult']['IdList']['Id'], list):
            returnID = dataBase['eSearchResult']['IdList']['Id'].pop()
        else:
            returnID = dataBase['eSearchResult']['IdList']['Id']

    # updates as the requests are being sent
    if i == 1:
        print("Sending request...")
    if i == 100:
        print("loading")
    if i == 1000:
        print("Loading.")
    if i == 2000:
        print("loading..")
    if i == 3000:
        print("loading...")
    if i == 4000:
        print("loading....")

    # adds the returned data into the idsArray
    idsArray.append(returnID)

print("All the requests are now processed")

# Setting the root element in the new Xml file that will be created.
PubmedArticleSet = ET.Element("PubmedArticleSet")

# The loop will execute once for each title in the titlesArray
for eachItem in range(len(titlesArray)):
    # PubmedArticle will be the sub element, which will hold
    # the ArticleTitle & PMID tags
    PubmedArticle = ET.SubElement(PubmedArticleSet, "PubmedArticle")

    # PMID is a sub element that will hold the ID for the article
    y = ET.SubElement(PubmedArticle, "PMID")
    y.text = str(idsArray[eachItem])

    # ArticleTitle is the sub element that will hold the titles
    y = ET.SubElement(PubmedArticle, "ArticleTitle")
    y.text = str(titlesArray[eachItem])

tree = ET.ElementTree(PubmedArticleSet)

# writes the tree in the xml file
tree.write('results.xml', encoding='utf-8', xml_declaration=True, )

# formats xml file
with open('results.xml') as xmldata:
    xml = xml.dom.minidom.parseString(xmldata.read())
    xml_format = xml.toprettyxml()

with open('results.xml', "w") as f:
    f.write(xml_format, )
