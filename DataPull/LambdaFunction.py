import boto3
from datetime import datetime, timezone
import json
from os import listdir
from os.path import isfile, join
import urllib3

s3_client = boto3.client("s3")
LOCAL_FILE_SYS = "/tmp"
S3_BUCKET = "your-s3-bucket"  # please replace with your bucket name
CHUNK_SIZE = 10000  # determined based on API, memory constraints, experimentation


def _get_key():
    dt_now = datetime.now(tz=timezone.utc)
    KEY = (
        dt_now.strftime("%Y-%m-%d")
        + "/"
        + dt_now.strftime("%H")
        + "/"
        + dt_now.strftime("%M")
        + "/"
    )
    return KEY

#CHUNK_SIZE = 10000  # determined based on API, memory constraints, experimentation
def get_num_records():
    # This gives the count of records in chunks, it depends on API and amount of data. 
    # Dummy function, to replicate GET http://jsonplaceholder.typicode.com/number_of_users call
    return 100000

#the get_data funtion is the funtion that gets data from api
#start_id and end_id it relates to pagination or chunks - it saves 1 -1000 then 1001 to 2000 tc 

def get_data(
    start_user_id, end_user_id, get_path="http://jsonplaceholder.typicode.com/posts"
):
    http = urllib3.PoolManager()
    data = {"userId": None, "id": None, "title": None, "body": None}
    try:
        r = http.request(
            "GET",
            get_path,
            retries=urllib3.util.Retry(3),
            fields={"start_user_id": start_user_id, "end_user_id": end_user_id},
        )
        data = json.loads(r.data.decode("utf8").replace("'", '"'))
    except KeyError as e:
        print(f"Wrong format url {get_path}", e)
    except urllib3.exceptions.MaxRetryError as e:
        print(f"API unavailable at {get_path}", e)
    return data
:wq
def parse_data(json_data):
    return f'{json_data.get("userId")},{json_data["id"]},"{json_data["title"]}"\n'


def write_to_local(data, part, loc=LOCAL_FILE_SYS):
    file_name = loc + "/" + str(part)
    with open(file_name, "w") as file:
        for elt in data:
            file.write(parse_data(elt))
    return file_name


def download_data(N):
    for i in range(0, N, CHUNK_SIZE):
        data = get_data(i, i + CHUNK_SIZE)
        write_to_local(data, i // CHUNK_SIZE) #this will save data in chunks 

#When creating a lambda function the entry code for execution is lambda_handler

def lambda_handler(event, context):
    N = get_num_records() #we get the number of record to download
    download_data(N) #we download the number of records 
    key = _get_key() 
    

    files = [f for f in listdir(LOCAL_FILE_SYS) if isfile(join(LOCAL_FILE_SYS, f))]
    for f in files:
        s3_client.upload_file(LOCAL_FILE_SYS + "/" + f, S3_BUCKET, key + f)
#we save to S3, we need different loation for each save, meaning every 5 minutes.  





