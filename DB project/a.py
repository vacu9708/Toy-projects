import requests, json, threading, time
import collections

auth='N7GQODWFY4I9Q7Q4PDOB'

# def get_statistics(index_code, item_code, period, start_data, end_date):
#     res=requests.get(f'https://ecos.bok.or.kr/api/StatisticSearch/{auth}/json/kr/1/1000/{index_code}/{period}/{start_data}/{end_date}/{item_code}/?/?/?').content.decode()
#     rows=json.loads(res)['StatisticSearch']['row']
#     for i, a in enumerate(rows):
#         print(i, a)
#         print('')
# get_statistics('521Y001', 'A001', 'M', '202001', '202101')

class OpenAPI_project:
    def __init__(self) -> True:
        self.queries=collections.defaultdict(list)
        self.stocks={}
        self.criteria={}
        threading.Thread(target=self.get_criteria).start()
        threading.Thread(target=self.query_trade).start()
    
    def get_criteria(self):
        while 1:
            res=requests.get(f'https://ecos.bok.or.kr/api/KeyStatisticList/{auth}/json/kr/1/100').content.decode()
            criteria=json.loads(res)['KeyStatisticList']['row']
            for row in criteria:
                self.criteria[row['KEYSTAT_NAME']]=row['DATA_VALUE']
            time.sleep(3)
    
    def query_trade(self):
        while 1:
            queries_to_remove=[]
            for target_stock in self.queries:
                if self.queries[target_stock]==False:
                    queries_to_remove.append(target_stock)
                    continue
                all_conditions_matched=True
                for condition in self.queries[target_stock]:
                    target_criterion, operation, number=condition
                    if operation=='<=' and not(float(self.criteria[target_criterion])<=float(number)):
                        all_conditions_matched=False
                        break
                    elif operation=='>=' and not(float(self.criteria[target_criterion])>=float(number)):
                        all_conditions_matched=False
                        break
                if all_conditions_matched:
                    if target_stock not in self.stocks:
                        self.stocks[target_stock]=True
                    else:
                        del self.stocks[target_stock]
                    queries_to_remove.append(target_stock)
            for query_to_remove in queries_to_remove:
                del self.queries[query_to_remove]

    def add_query(self, query: list):
        if query[1] not in self.criteria:
            print('This statistics name does not exist')
            return
        self.queries[query[0]].append(query[1:])

    def clear_query(self, target_stock: str):
        self.queries[target_stock]=False

    def main(self):
        print('Type help')
        while 1:
            req=input().split(' ')
            if req[0]=='help':
                print('0: Show statistics')
                print('1: Show my stocks')
                print('2: Show my queries')
                print('add [target_stock] [target_criterion] [operation] [number]')
                print('clear [target_stock]')
            elif req[0]=='0':
                for key in self.criteria:
                    print(key, self.criteria[key])
            elif req[0]=='1':
                print(self.queries)
            elif req[0]=='2':
                print(self.stocks)
            elif req[0]=='add':
                self.add_query(req[1:])
                print('done')
            elif req[0]=='clear':
                self.clear_query(req[1])
                print('done')

openAPI_project=OpenAPI_project()
openAPI_project.main()