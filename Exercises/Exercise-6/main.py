import zipfile, os, logging
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import to_timestamp

file_list = ['Divvy_Trips_2019_Q4', 'Divvy_Trips_2020_Q1']
file_folder_path = 'data'

def main():
    
    # decompress
    for f in file_list:
        f_path = os.path.join(file_folder_path, f + '.zip')
        if zipfile.is_zipfile(f_path):
            print(f'Extracting {f_path}')
            with zipfile.ZipFile(f_path, "r") as z:
                z.extractall(file_folder_path)
            print('Extracted')

    

    # loading in spark
    spark = SparkSession.builder.appName("Exercise6").enableHiveSupport().getOrCreate()
    df_2019 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[0] + ".csv")}', header=True, inferSchema=True)
    df_2020 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[1] + ".csv")}', header=True, inferSchema=True)

    # data preparation 2020 >> 2019 (which has more fields)
    columns_rename = {
        "ride_id": "trip_id", # old: new
        "started_at": "start_time",
        "ended_at": "end_time",
        "rideable_type": "bikeid",
        "start_station_id": "from_station_id",
        "start_station_name": "from_station_name",
        "end_station_id": "to_station_id",
        "end_station_name": "to_station_name"
    }
    for old, new in columns_rename.items():
        df_2020 = df_2020.withColumnRenamed(old, new)


    common_columns = list(set(df_2019.columns) & set(df_2020.columns))

    df_merged = df_2019.select(common_columns).unionByName(df_2020.select(common_columns))
    df_merged.show()
    # df.orderBy('start_time', ascending=False).show()

    df_merged.createOrReplaceTempView("bikes")

    # typing
    df_merged = df_merged.withColumn("from_station_id", df_merged["from_station_id"].cast(IntegerType()))
    df_merged = df_merged.withColumn("bikeid", df_merged["bikeid"].cast(IntegerType()))
    df_merged = df_merged.withColumn("trip_id", df_merged["trip_id"].cast(IntegerType()))
    df_merged = df_merged.withColumn("start_time", to_timestamp(df_merged["start_time"], "yyyy-MM-dd HH:mm:SS"))
    df_merged = df_merged.withColumn("end_time", to_timestamp(df_merged["end_time"], "yyyy-MM-dd HH:mm:SS"))

    df_merged.printSchema()

    query_1 = ' \
        SELECT bikes.day, avg(bikes.duration) \
        FROM (\
            SELECT  \
               date_trunc(''DD'', start_time) as day, \
               (unix_timestamp(end_time) - unix_timestamp(start_time)) AS duration \
            FROM bikes \
        ) bikes \
        GROUP BY bikes.day \
        ORDER BY bikes.day\
    '
    spark.sql(query_1).show()

    # 2019: trip_id,start_time,end_time,bikeid,tripduration,from_station_id,from_station_name,to_station_id,to_station_name,usertype,gender,birthyear
    # 2020: ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual
    
if __name__ == "__main__":
    main()
