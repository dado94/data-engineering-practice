import os
import json
from pandas import json_normalize


def main():
    print('Listing files:')
    print(os.getcwd())
    for root, dirs, files in os.walk("data"):
        for file in files:
            name_and_extension = os.path.splitext(file)
            if name_and_extension[1] == '.json':
                current_json_path = os.path.join(root, file)
                print(f'Reading & parsing {current_json_path}')
                with open(current_json_path) as f:
                    json_file = json.load(f)
                    df = json_normalize(json_file)
                    if 'value_list' in df.columns:
                        df = df.explode("value_list")
                    if 'geolocation.coordinates' in df.columns:
                        df = df.explode("geolocation.coordinates")
                    print(df)
                    csv_file_path = os.path.join(root, name_and_extension[0] + '.csv')
                    print(f'Saving {csv_file_path}')
                    df.to_csv(csv_file_path, index=False)

            else:
                print(f'Ignoring "{file}"')

if __name__ == "__main__":
    main()
