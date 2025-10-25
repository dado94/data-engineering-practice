import zipfile, os
from pyspark.sql import SparkSession

file_list = ['Divvy_Trips_2019_Q4.zip', 'Divvy_Trips_2020_Q1.zip']
file_folder_path = 'data'

def main():
    
    
    # decompress
    for f in file_list:
        f_path = os.path.join(file_folder_path, f)
        if zipfile.is_zipfile(f_path):
            print(f'Extracting {f_path}')
            with zipfile.ZipFile(f_path, "r") as z:
                z.extractall(file_folder_path)
            print('Extracted')

    # loading in spark
    spark = SparkSession.builder.appName("Exercise6").enableHiveSupport().getOrCreate()
    df = spark.read.csv(f'{os.path.join(file_folder_path, file_list[0])}', header=True, inferSchema=True)
    df.orderBy('start_time', ascending=False).show()

    # query_1 = ' \
    #     SELECT avg(end_time - start_time) \
    #     FROM \
    #     GROUP BY \
    # '

    # trip_id,start_time,end_time,bikeid,tripduration,from_station_id,from_station_name,to_station_id,to_station_name,usertype,gender,birthyear
    # ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual
    # trip_id > ride_id (+-)
    # start_time > started_at
    # end_time > ended_at
    # bikeid ?
    # tripduration
    # from_station_id > start_station_id
    # from_station_name > start_station_name
    # to_station_id > end_station_id
    # to_station_name > end_station_name
    # usertype > ? member_casual
    # gender ? 
    # birthyear ? 

if __name__ == "__main__":
    main()
