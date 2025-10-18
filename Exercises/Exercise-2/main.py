import requests, pandas as pd, re, os
import Utils.utils as utils

weather_data_url = 'https://www.ncei.noaa.gov/data/local-climatological-data/access/2021/'
save_path = os.path.join(os.getcwd(), "downloads")

def main():
    response = requests.get(weather_data_url)
    if response.status_code == 200:
        print("Downloading file list")
        # removing html page initial description
        row_list_string = response.text[response.text.find("<tr>"):]
        # split by <tr> tag and remove table headings
        row_list_parsed = row_list_string.split("<tr>")[4:]
        print(f"{len(row_list_parsed)} files found")
        # search by tms
        matches = [r for r in row_list_parsed if '<td align="right">2024-01-19 15:29</td>' in r]
        print(f"{len(matches)} matched found, taking only the first")
        # extract href
        rgxp = r"<td><a href=\"(.*\.csv)\">.*<\/a><\/td>"
        match = re.search(rgxp, matches[0])
        file_name = match.group(1)
        print(file_name)

        # download
        file_path = os.path.join(save_path, file_name)
        response = requests.get(os.path.join(weather_data_url, file_name))
        if response.status_code == 200:    
            with open(file_path, "wb") as f:
                f.write(response.content)
            # parse in pandas
            df = pd.read_csv(file_path).sort_values(by="HourlyDryBulbTemperature", ascending=False)
            print(df[["STATION", "DATE", "LATITUDE", "LONGITUDE", "NAME", "HourlyDryBulbTemperature"]].head())
        else:
            print(f'Something went wrong, error {response.status_code}')
        
    else:
        print(f"Error: {response.status_code}")

    # utils.cleanup_folder(save_path)


if __name__ == "__main__":
    main()
