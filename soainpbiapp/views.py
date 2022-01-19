from django.shortcuts import render
import json
import pandas as pd
from . import soa
# Create your views here.
def index(request): # index word can be any, but request is to define it is view
    cursor = soa.conn.cursor()
    para = request.GET["customer"] # jobnum is parameter name in the request
    sql = """select a.[CUSTOMER NAME],a.[CUSTOMER CODE],a.[MASTER REF],a.[HOUSEBILL REF],a.[DOCUMENT NO], a.[DOCUMENT DATE], a.[DUE DAYS],a.[INVOICE AMOUNT],a.[BALANCE AMOUNT]
from [dbo].[soa_data] as a left join [dbo].[dimCustomerEmail] as b on a.[CUSTOMER CODE]=b.[CustomerCode] where b.[EmailId] =  ? and a.[Delete_status]='No' """
    df = pd.DataFrame()
    data = []
    cursor.execute(sql,para)
    data_list =[]
    for j in cursor:
        data_list.append(list(j))
    no_data_msg = ""
    if len(data_list) > 0:
        df = pd.DataFrame(data_list)

        json_records = df.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records) 
    else:
        print("Done")
        no_data_msg = "Data Not Available"
    
    context = {"table":data, "customername":para,"no_data_msg":no_data_msg}
    # what so ever we add in the context variable it can be passed to HTML, even context is a generic word not some statndard, it wil render only if you input in below line in return
    
    return render(request,"index.html",context) # template html in flask render_template


def export_data(request):
    try:
        cursor = soa.conn.cursor()
        para = request.GET["customer"] # jobnum is parameter name in the request
        sql = """select a.[CUSTOMER NAME],a.[CUSTOMER CODE],a.[MASTER REF],a.[HOUSEBILL REF],a.[DOCUMENT NO], a.[DOCUMENT DATE], a.[DUE DAYS],a.[INVOICE AMOUNT],a.[BALANCE AMOUNT] from [dbo].[soa_data] as a left join [dbo].[dimCustomerEmail] as b on a.[CUSTOMER CODE]=b.[CustomerCode] where b.[EmailId] = ?  and a.[Delete_status]='No' """
        cursor.execute(sql,para)
        data_list =[]
        for j in cursor:
            data_list.append(list(j))
        no_data_msg = ""
        if len(data_list) > 0:
            df = pd.DataFrame(data_list)
            df.columns = ["CUSTOMER NAME","CUSTOMER CODE","MASTER REF","HOUSEBILL REF","DOCUMENT NO","DOCUMENT DATE","DUE DAYS","INVOICE AMOUNT","BALANCE AMOUNT"]
            json_records = df.reset_index().to_json(orient ='records')
            data = []
            data = json.loads(json_records)
        else:
            print("Done")
            no_data_msg = "Data Not Availlable"
        import os.path
        if os.path.exists("my_raw_data.csv"):
            os.remove("my_raw_data.csv")
            df.to_csv("my_raw_data.csv", index = False)
        else:
            df.to_csv("my_raw_data.csv", index = False)

        file_name = "my_raw_data"
        path_to_file = "my_raw_data.csv"
        from django.views.static import serve
        import os
        filepath = 'my_raw_data.csv'
    except Exception as ex:
        print(ex)
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))


def data_load(request):
    return render(request,'data_load.html')



# Data Loading for us
def data_load_us_ajax(request):
    if request.method == "POST":
        print("For US")
        handle_uploaded_file(request.FILES["file_name"])
        # Reading Dataset
        df = pd.read_excel('data_file.xlsx',engine='openpyxl')
        print(df)
        df = df.astype(str)

        # Converting ETD , ETA, CURRENT DAYS to Datetime
        df["ETD"] = pd.to_datetime(df["ETD"])
        df["ETA"] = pd.to_datetime(df["ETA"])
        df["CURRENT DAYS"] = pd.to_datetime(df["CURRENT DAYS"])

        # Filling Date 
        df["ETD"] = df["ETD"].fillna("1970-01-01")
        df["ETA"] = df["ETA"].fillna("1970-01-01")
        df["CURRENT DAYS"] = df["CURRENT DAYS"].fillna("1970-01-01")

        # Converting CREDIT DAYS , PAST DUE, DUE DAYS to Float and fillnan as 0
        df["CREDIT DAYS"] = df["CREDIT DAYS"].fillna(0).astype(float)
        df["CREDIT AMOUNT"] = df["CREDIT AMOUNT"].astype(float)
        df["PAST DUE"] = df["PAST DUE"].fillna(0).astype(float)
        df["DUE DAYS"] = df["DUE DAYS"].fillna(0).astype(float)

        # Converting EXCHANGE RATE, INVOICE AMOUNT, LOCAL AMOUNT, BALANCE AMOUNT to float
        df["EXCHANGE RATE"] = df["EXCHANGE RATE"].astype(float)
        df["INVOICE AMOUNT"] = df["INVOICE AMOUNT"].astype(float)
        df["LOCAL AMOUNT"] = df["LOCAL AMOUNT"].astype(float)
        df["BALANCE AMOUNT"] = df["BALANCE AMOUNT"].astype(float)

        # Filling all na to blank
        df = df.fillna('')

        # Updating Delete Status

        sql_del = "Update soa_data SET Delete_status='Yes' where CONVERT(VARCHAR, country)='US'"
        cursor = soa.conn.cursor()
        cursor.execute(sql_del)
        soa.conn.commit()

        # Inserting Record
        for index,row in df.iterrows():
            sql = "insert into [dbo].[soa_data]([CUSTOMER NAME],[CUSTOMER CODE],[SETTLEMENT GROUP NAME],[SETTLEMENT GROUP CODE],[SUBLEDGER TYPE],[SALESMAN NAME],[COLLECTIONS MANAGER],[JOB NO],[SHIPMENT/CONSOL DESCRIPTION],[DEPT],[MASTER REF],[HOUSEBILL REF],[CONTAINER NUMBER],[ETD],[ETA],[JOB OPERATIONS REP],[JOB CREATE USER],[INV TYPE],[CATEGORY],[DOCUMENT NO],[DOCUMENT DATE],[CREATE DATE],[CREDIT DAYS],[CREDIT AMOUNT],[CREDIT INSURANCE STATUS],[CURRENT DAYS],[PAST DUE],[STATUS],[SHIPPER NAME],[CONSIGNEE NAME],[DESCRIPTION],[DR CR],[DUE DAYS],[FOREIGN CURRENCY CODE],[EXCHANGE RATE],[INVOICE AMOUNT],[CURRENCY CODE],[LOCAL AMOUNT],[BALANCE AMOUNT],[country]) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (row["CUSTOMER NAME"],row["CUSTOMER CODE"],row["SETTLEMENT GROUP NAME"],row["SETTLEMENT GROUP CODE"],row["SUBLEDGER TYPE"],row["SALESMAN NAME"],row["COLLECTIONS MANAGER"],row["JOB NO"],row["SHIPMENT/CONSOL DESCRIPTION"],row["DEPT"],row["MASTER REF"],row["HOUSEBILL REF"],row["CONTAINER NUMBER"],row["ETD"],row["ETA"],row["JOB OPERATIONS REP"],row["JOB CREATE USER"],row["INV TYPE"],row["CATEGORY"],row["DOCUMENT NO"],row["DOCUMENT DATE"],row["CREATE DATE"],row["CREDIT DAYS"],row["CREDIT AMOUNT"],row["CREDIT INSURANCE STATUS"],row["CURRENT DAYS"],row["PAST DUE"],row["STATUS"],row["SHIPPER NAME"],row["CONSIGNEE NAME"],row["DESCRIPTION"],row["DR CR"],row["DUE DAYS"],row["FOREIGN CURRENCY CODE"],row["EXCHANGE RATE"],row["INVOICE AMOUNT"],row["CURRENCY CODE"],row["LOCAL AMOUNT"],row["BALANCE AMOUNT"],'US')
            cursor = soa.conn.cursor()
            cursor.execute(sql,params)
            print(index , "Data Updated and  - Row Inserted")
        soa.conn.commit()
    return render(request,'data_load.html')
    


def data_load_uk_ajax(request):
    if request.method == "POST":

        handle_uploaded_file(request.FILES["file_name"])
        df = pd.read_excel('data_file.xlsx',engine='openpyxl')

        df = df.astype(str)

        # Converting ETD , ETA, CURRENT DAYS to Datetime
        df["ETD"] = pd.to_datetime(df["ETD"])
        df["ETA"] = pd.to_datetime(df["ETA"])
        df["CURRENT DAYS"] = pd.to_datetime(df["CURRENT DAYS"])
        
        # Filling Date 
        df["ETD"] = df["ETD"].fillna("1970-01-01")
        df["ETA"] = df["ETA"].fillna("1970-01-01")
        df["CURRENT DAYS"] = df["CURRENT DAYS"].fillna("1970-01-01")
        
        # Converting CREDIT DAYS , PAST DUE, DUE DAYS to Float and fillnan as 0
        df["CREDIT DAYS"] = df["CREDIT DAYS"].fillna(0).astype(float)
        df["CREDIT AMOUNT"] = df["CREDIT AMOUNT"].astype(float)
        df["PAST DUE"] = df["PAST DUE"].fillna(0).astype(float)
        df["DUE DAYS"] = df["DUE DAYS"].fillna(0).astype(float)

        # Converting EXCHANGE RATE, INVOICE AMOUNT, LOCAL AMOUNT, BALANCE AMOUNT to float
        df["EXCHANGE RATE"] = df["EXCHANGE RATE"].astype(float)
        df["INVOICE AMOUNT"] = df["INVOICE AMOUNT"].astype(float)
        df["LOCAL AMOUNT"] = df["LOCAL AMOUNT"].astype(float)
        df["BALANCE AMOUNT"] = df["BALANCE AMOUNT"].astype(float)
        df = df.fillna('')

        # Updating Delete Status
        sql_del = "Update soa_data SET Delete_status='Yes' where CONVERT(VARCHAR, country)='UK'"
        cursor = soa.conn.cursor()
        cursor.execute(sql_del)
        soa.conn.commit()

        # Inserting Records
        for index,row in df.iterrows():
            sql = "insert into [dbo].[soa_data]([CUSTOMER NAME],[CUSTOMER CODE],[SETTLEMENT GROUP NAME],[SETTLEMENT GROUP CODE],[SUBLEDGER TYPE],[SALESMAN NAME],[COLLECTIONS MANAGER],[JOB NO],[SHIPMENT/CONSOL DESCRIPTION],[DEPT],[MASTER REF],[HOUSEBILL REF],[CONTAINER NUMBER],[ETD],[ETA],[JOB OPERATIONS REP],[JOB CREATE USER],[INV TYPE],[CATEGORY],[DOCUMENT NO],[DOCUMENT DATE],[CREATE DATE],[CREDIT DAYS],[CREDIT AMOUNT],[CREDIT INSURANCE STATUS],[CURRENT DAYS],[PAST DUE],[STATUS],[SHIPPER NAME],[CONSIGNEE NAME],[DESCRIPTION],[DR CR],[DUE DAYS],[FOREIGN CURRENCY CODE],[EXCHANGE RATE],[INVOICE AMOUNT],[CURRENCY CODE],[LOCAL AMOUNT],[BALANCE AMOUNT],[country]) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (row["CUSTOMER NAME"],row["CUSTOMER CODE"],row["SETTLEMENT GROUP NAME"],row["SETTLEMENT GROUP CODE"],row["SUBLEDGER TYPE"],row["SALESMAN NAME"],row["COLLECTIONS MANAGER"],row["JOB NO"],row["SHIPMENT/CONSOL DESCRIPTION"],row["DEPT"],row["MASTER REF"],row["HOUSEBILL REF"],row["CONTAINER NUMBER"],row["ETD"],row["ETA"],row["JOB OPERATIONS REP"],row["JOB CREATE USER"],row["INV TYPE"],row["CATEGORY"],row["DOCUMENT NO"],row["DOCUMENT DATE"],row["CREATE DATE"],row["CREDIT DAYS"],row["CREDIT AMOUNT"],row["CREDIT INSURANCE STATUS"],row["CURRENT DAYS"],row["PAST DUE"],row["STATUS"],row["SHIPPER NAME"],row["CONSIGNEE NAME"],row["DESCRIPTION"],row["DR CR"],row["DUE DAYS"],row["FOREIGN CURRENCY CODE"],row["EXCHANGE RATE"],row["INVOICE AMOUNT"],row["CURRENCY CODE"],row["LOCAL AMOUNT"],row["BALANCE AMOUNT"],'UK')
            cursor = soa.conn.cursor()
            cursor.execute(sql,params)
            print(index , "Data Updated and  - Row Inserted")
        soa.conn.commit()
    return render(request,'data_load.html')
    

def logout_view(request):  # Logout and redirect to login page
    logout(request)
    return redirect('/')


def handle_uploaded_file(f):
    with open('data_file.xlsx', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
