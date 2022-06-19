def findAfterString(string, frontOfHtmlElement, backOfHtmlElement): # To find changes in posts
    beginningOfHtmlElement=0
    endOfHtmlElement=0

    # Find the beginning of HTML element
    for i in range(len(string)-len(frontOfHtmlElement)):
        same=True
        for j in range(len(frontOfHtmlElement)):
            # print(i,j, chr(string[i+j]), frontOfHtmlElement[j])
            if chr(string[i+j])!=frontOfHtmlElement[j]:
                same=False
                break
        if same:
            beginningOfHtmlElement=i
            break
    # Find the end of HTML element
    for i in range(beginningOfHtmlElement+len(frontOfHtmlElement), len(string)-len(backOfHtmlElement)):
        same=True
        for j in range(len(backOfHtmlElement)):
            if chr(string[i+j])!=backOfHtmlElement[j]:
                same=False
                break
        if same:
            endOfHtmlElement=i
            break
    # print(beginningOfHtmlElement, endOfHtmlElement)
    # print(string[beginningOfHtmlElement:beginningOfHtmlElement+len(frontOfHtmlElement)])
    # print(string[endOfHtmlElement:endOfHtmlElement+len(backOfHtmlElement)])
    return beginningOfHtmlElement, endOfHtmlElement

# Default database
try:
    open("./webpage_list.txt", 'r', encoding='utf-8')
except:
    database = open("./webpage_list.txt", 'w', encoding='utf-8')
    database.write('((INU notices)) ((https://www.inu.ac.kr/user/boardList.do?boardId=48510&page=1&search=&column=&categoryId=&categoryDepth=&id=inu_070201000000&parent=)) ((//*[@id="list_frm"]/div/table/tbody/tr[50]/td[1])) (())')
    database.write('((Test[인터넷방송 갤러리])) ((https://gall.dcinside.com/board/lists/?id=ib_new2)) ((//*[@id="container"]/section[1]/article[2]/div[2]/table/tbody/tr[6]/td[1])) (())\n')
    database.close()

webpageNames=[]
urls = [] # URLs to be monitored
frontOfHtmlElements=[] # Find element by XPATH
backOfHtmlElements=[] # Find element by css selector

def parseDatabase():
    parsedStrings=[]
    database = open("./webpage_list.txt", 'r', encoding='utf-8')
    database.seek(0)
    document=database.read()
    database.close()

    for i in range(len(document)): # Find string between 2 quotation marks
        if document[i]=='(' and document[i+1]=='(': # First distinguisher found
            beginningOfString=i+2
            for j in range(beginningOfString, len(document)-1): # Look for second distinguisher
                if document[j]==')' and document[j+1]==')':
                    closingOfString=j
                    break
            parsedStrings.append(document[beginningOfString:closingOfString])

    for i in range(0, len(parsedStrings), 4):
        webpageNames.append(parsedStrings[i])
        urls.append(parsedStrings[i+1])
        frontOfHtmlElements.append(parsedStrings[i+2])
        backOfHtmlElements.append(parsedStrings[i+3])

def deleteWebpageFromDatabase(targetRow):
    currentRow=0
    beginningOfTargetRow=0
    beginningOfNextRow=0

    database = open("./webpage_list.txt", 'r', encoding='utf-8')
    document=database.read()
    for i in range(len(document)):
        # Go to target index
        if document[i]=='\n':
            currentRow+=1
        if currentRow==targetRow: # If target index found
            beginningOfTargetRow=i+1
            for j in range(beginningOfTargetRow, len(document)):
                if document[j]=='\n':
                    beginningOfNextRow=j+1
                    break
            break

    database = open("./webpage_list.txt", 'w', encoding='utf-8')
    if currentRow!=0: # To handle deleting the first row
        database.write(document[:beginningOfTargetRow])
        database.write(document[beginningOfNextRow:])
    database.close()