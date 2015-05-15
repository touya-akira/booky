import xmltodict
import urllib.request
import urllib.parse
import re
from bs4 import BeautifulSoup

apiURL = 'https://www.goodreads.com/search/index.xml?'
apiKey = 'gGvZrXQXfxLpXVduCkvoMQ'
bookurl = 'https://www.goodreads.com/book/show/'
getBookUrl = ('https://www.goodreads.com/book/show/', '?format=xml&key=' + apiKey)

groupUrl = ('https://www.goodreads.com/group/show/', '.xml?key=' + apiKey)
groupId = '153235'
groupShelf = ('https://www.goodreads.com/group/bookshelf/' + groupId + '-books?order=d&per_page=30&shelf=', '&sort=date_finished&view=main')

userDict = {
    'amaan': '31053607',
    'agau': '37568089',
    'klonk': '1431428',
    'gridcube': '30092396',
    'heddle': '12181320',
    'lif': '6176359',
    'bld1': '4640099',
    'touya': '41315361',
    'gigahurt': '1777204',
    'd4lek': '39512463',
    'nalkri': '7019867',
    'elench': '7019867',
    'ai-terminal': '42802442',
    'goomba_': '1244196',
    'lorax': '43065268'
}

userShelf = ('https://www.goodreads.com/review/list/', '?shelf=currently-reading')
# Searches for a book using either the Goodreads ID or some search text
def search(arg):
    if not arg:
        return 'Enter a search term, doofus'
    elif arg.isdigit():
        url = getBookUrl[0] + arg + getBookUrl[1]
        xml = urllib.request.urlopen(url)
        doc = xmltodict.parse(xml)
        if 'GoodreadsResponse' in doc:
            book = doc['GoodreadsResponse']['book']
            title = book['title']
            author = book['authors']['author']['name']
            rating = book['average_rating']
            return '{0} ({1}/5) by {2} - {3}'.format(title, rating, author, bookurl + arg)
        else:
            return 'No book found with that ID'
    else:
        q = urllib.parse.urlencode({'key': apiKey, 'q': arg})
        xml = urllib.request.urlopen(apiURL + q)
        doc = xmltodict.parse(xml)
        if doc['GoodreadsResponse']['search']['results-end'] != '0':
            results = doc['GoodreadsResponse']['search']['results']['work']

            # If there are many results, pick the first
            if isinstance(results, list):
                result = results[0]
            else:
                result = results
            book = result['best_book']
            title = book['title']
            author = book['author']['name']
            rating = result['average_rating']
            uid = book['id']['#text']
            return '{0} ({1}/5) by {2} - {3}'.format(title, rating, author, bookurl + uid)
        else:
            return 'No results found'

# num:
# 0 for current book
# 1 for next book
# -1 for previous
def groupBook(num):
    if num == 0:
        url = groupUrl[0] + groupId + groupUrl[1]
        xml = urllib.request.urlopen(url)
        doc = xmltodict.parse(xml)
        book = doc['GoodreadsResponse']['group']['currently_reading']['group_book']['book']
        
        title = book['title']
        author = book['author']['name']
        uid = book['id']['#text']
        
        return 'Currently reading {0} by {1} - {2}'.format(title, author, bookurl + uid)
    elif num < 0:
        url = groupShelf[0] + 'read' + groupShelf[1]
        html = urllib.request.urlopen(url)
        try:
            soup = BeautifulSoup(html)
            table = soup.find_all(id='groupBooks')[0]
            bookElem = table.contents[3]
            bookName = bookElem.contents[3].contents[1].string
            return 'Previously, we read: ' + search(bookName)
        except:
            return 'No books found.'
            raise
    else:
        url = groupShelf[0] + 'to-read' + groupShelf[1]
        html = urllib.request.urlopen(url)
        try:
            soup = BeautifulSoup(html)
            table = soup.find_all(id='groupBooks')[0]
            bookElem = table.contents[3]
            bookName = bookElem.contents[3].contents[1].string
            return 'Next, we\'ll read: ' + search(bookName)
        except:
            return 'No books found.'
            raise

def userCurrent(name):
    if name.lower() not in userDict:
        return 'Amaan hasn\'t added that user to the pre-defined list'
    userId = userDict[name.lower()]
    url = userShelf[0] + userId + userShelf[1]
    html = urllib.request.urlopen(url)
    try:
        soup = BeautifulSoup(html)
        table = soup.find_all(id='booksBody')[0]
        # bookElems = (elem for elem in table.contents if elem != '\n')
        numBooks = soup.select('.h1Shelf .greyText')[0].text
        numBooks = re.search('[0-9]+', numBooks).group(0)
        retString = '{} is reading {} books.'.format(name, numBooks)
        if (numBooks != '0'):
            bookElem = table.contents[1]
            titleElem = bookElem.find(class_='title')
            div = titleElem.contents[1]
            link = div.contents[1]
            titleList = list(link.stripped_strings)
            bookName = ' '.join(titleList).strip()
            retString += ' Most recently added: {}'.format(search(bookName))
        return retString
    except Exception as e:
        return 'No books found. The user\'s profile might be private.'
        raise e


def main():
    print(userCurrent('Amaan'))
    return 0

if __name__ == '__main__':
    main()