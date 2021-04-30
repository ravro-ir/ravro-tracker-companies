import requests
import json
import time


class GlobalVariable:

    header = {
        "Host": "www.ravro.ir",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "Content-Length": "704",
        "Origin": "https://www.ravro.ir"
    }
    last_status_company = None
    current_status_company = []


class Variables:
    offset: int
    limit: int
    order: str
    direction: str
    search: str

    def __init__(self, offset: int, limit: int, order: str, direction: str, search: str) -> None:
        self.offset = offset
        self.limit = limit
        self.order = order
        self.direction = direction
        self.search = search

    def ret_dict(self):
        return {
            "offset": self.offset,
            "limit": self.limit,
            "order": self.order,
            "direction": self.direction,
            "search": ""
        }


class GraphQLAPI:

    operation_name: str
    variables: Variables
    query: str

    def setter(self):
        self.obj_var = Variables(0, 36, "createdAt", "desc", "").ret_dict()
        self.query = "query companies($offset: Int!, $limit: Int!, $search: String, $status: Int, $type: Int, $order: String, $direction: String) {\n  companies(\n    pagination: {limit: $limit, offset: $offset}\n    search: $search\n    order: {field: $order, direction: $direction}\n    filters: {status: $status, type: $type}\n  ) {\n    rows {\n      id\n      realname\n      email\n      name\n      avatar\n      hunts\n      rewards\n      activeReports\n      __typename\n    }\n    pageInfo {\n      total\n      count\n      nextOffset\n      __typename\n    }\n    __typename\n  }\n}\n"
        self.company = "companies"

    def add_dict(self):
        return {
            "operationName": self.company,
            "variables": self.obj_var,
            "query": self.query
        }

    def add_to_lst(self):
        lst = []
        self.out = self.add_dict()
        lst.append(self.out)
        return json.dumps(lst)


class HttpReq:

    def __init__(self, data, apiurl, header):
        self.data = data
        self.apiurl = apiurl
        self.header = header

    def postreq(self):
        try:
            letreq = requests.post(self.apiurl, self.data, headers=self.header)
        except:
            return ""
        if letreq.status_code == 200:
            return letreq.text


class Parser:

    def __init__(self, res):
        self.res = res

    def resparser(self):
        GlobalVariable.current_status_company.clear()
        self.decode_res = json.loads(self.res)
        for data in self.decode_res:
            for raw in data['data']['companies']['rows']:
                if raw["activeReports"] == 1:
                    print(raw["id"], raw["name"], raw["activeReports"] , "===== ACTIVE COMPANY =====" )
                    GlobalVariable.current_status_company.append({"id": raw["id"], "name": raw["name"], "status": raw["activeReports"]})
        if not GlobalVariable.last_status_company:
            GlobalVariable.last_status_company = GlobalVariable.current_status_company.copy()

        # GlobalVariable.current_status_company.append(
        #     {"id": 254, "name": "test", "status": 0})

        if len(GlobalVariable.current_status_company) > len(GlobalVariable.last_status_company):
            print("Added New Company for hunters")
            # TODO - send SMS or send email
            GlobalVariable.last_status_company.clear()
            GlobalVariable.last_status_company = GlobalVariable.last_status_company.copy()
        if len(GlobalVariable.current_status_company) < len(GlobalVariable.last_status_company):
            print("Removed New Company for Hunters")


apiurl = "https://www.ravro.ir/api/graphql"
obj = GraphQLAPI()
obj.setter()
encode_data = obj.add_to_lst()
while 1:
    get_response = HttpReq(encode_data, apiurl, GlobalVariable().header).postreq()
    if not get_response:
        time.sleep(600) #10 min
        continue
    Parser(get_response).resparser()
    print("@" * 100)
    time.sleep(10)
    