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
    df_2019 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[0])}', header=True, inferSchema=True)
    df_2020 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[1])}', header=True, inferSchema=True)

    # data preparation 2020 > 2019 (which has more fields)
    columns_rename = {
        
    }
    df_2020.withColumnRenamed("ride_id", "trip_id")
    df_2020.withColumnRenamed("started_at", "start_time")
    df_2020.withColumnRenamed("ended_at", "end_time")


    df_total = df_2019.unionByName(df_2020)
    # df.orderBy('start_time', ascending=False).show()

    # query_1 = ' \
    #     SELECT avg(end_time - start_time) \
    #     FROM \
    #     GROUP BY \
    # '

    # 2019: trip_id,start_time,end_time,bikeid,tripduration,from_station_id,from_station_name,to_station_id,to_station_name,usertype,gender,birthyear
    # 2020: ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual
    
if __name__ == "__main__":
    main()
