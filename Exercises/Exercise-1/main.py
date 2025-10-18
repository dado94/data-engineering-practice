import requests, os, zipfile, unittest
from concurrent.futures import ThreadPoolExecutor

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip"
    ,
]

save_path = os.path.join(os.getcwd(), "downloads")


def worker(index):
    # download
    url = download_uris[index]
    file_name = url.split("/")[-1]
    zip_file_path = os.path.join(save_path, file_name)
    print(f"Worker #{index}: Downloading: " + file_name)
    response = requests.get(url)
    if response.status_code == 200:    
        with open(zip_file_path, "wb") as f:
            f.write(response.content)
        # extract
        print(f"Worker #{index}: Extracting \"{file_name}\"")
        with zipfile.ZipFile(zip_file_path, "r") as zip_file:
            zip_file.extractall(save_path)
        os.remove(zip_file_path)
        print(f"Worker #{index}: File \"{file_name}\" extact completed")
    else:
        print(f"Worker #{index}: Error downloading \"{file_name}\" response code: {response.status_code}")     
    
def main():
    # init folder
    if not (os.path.exists(save_path)): # windows does not allow file and folders with the same name, os.path.isdir is not needed
        os.mkdir(save_path)
        print(f"Folder \"{save_path}\" created")
    else:
        print(f"Folder \"{save_path}\" already exists")

    # launch threads
    with ThreadPoolExecutor(max_workers=7) as executor:
        executor.map(worker, range(7))

if __name__ == "__main__":
    main()
