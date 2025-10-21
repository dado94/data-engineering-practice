import boto3
from botocore import UNSIGNED
from botocore.client import Config
import requests, gzip, io, urllib

def try_with_rest(key, backup_uri):
    full_path = urllib.parse.urljoin(backup_uri, key)
    print(f'Connecting to {full_path}')
    answer = requests.get(full_path)
    if answer.status_code == 200:
        return io.BytesIO(answer.content)
    else:
        print(f"Error, response code: {answer.status_code}")

def try_with_boto3(bucket, key, backup_uri):
    try:
        s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        obj = s3.get_object(Bucket=bucket, Key=key)
        print(obj)
        # unimplemented since it doesn't work anymore
        return None
    except:
        print(f'Error connecting to s3, trying with REST')
        return try_with_rest(key, backup_uri)

def main():
    bucket = 'commoncrawl'
    key = 'crawl-data/CC-MAIN-2022-05/wet.paths.gz'
    backup_uri = 'https://data.commoncrawl.org/'
    
    in_memory_file = try_with_boto3(bucket, key, backup_uri)

    with gzip.open(in_memory_file, "rt", encoding="utf-8") as file:
        new_key = file.readline()
    print(f'Found key: {new_key}')

    in_memory_file = try_with_boto3(bucket, new_key, backup_uri)
    print('File content: ')
    with gzip.open(in_memory_file, "rt", encoding="utf-8") as file:
        for i, row in enumerate(file):
            if i > 50:
                return
            print(row)


if __name__ == "__main__":
    main()
