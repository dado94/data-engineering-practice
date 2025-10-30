import zipfile, os
from datetime import datetime
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType

file_list = ['Divvy_Trips_2019_Q4', 'Divvy_Trips_2020_Q1']
file_folder_path = 'data'

def query1(spark):
    # What is the average trip duration per day?
    print('----- QUERY 1 -----')
    query_1 = " \
        SELECT  \
           date_trunc('day', start_time) as day, \
           avg(unix_timestamp(end_time) - unix_timestamp(start_time)) as duration \
        FROM bikes \
        GROUP BY date_trunc('day', start_time) \
        ORDER BY date_trunc('day', start_time) \
    "
    spark.sql(query_1).show(5)
    print('----- END OF QUERY 1 -----')

def query2(df):
    # How many trips were taken each day?
    print('----- QUERY 2 -----')
    result = df.groupBy(F.date_trunc('day', 'start_time').alias('day'))   \
        .agg(F.count('trip_id').alias('trip_count'))                      \
        .orderBy(F.col('trip_count').desc())
    print('----- END OF QUERY 2 -----')
    return result

def query3(df):
    # What was the most popular starting trip station for each month?
    print('----- QUERY 3 -----')
    window = Window.partitionBy('month').orderBy(F.col('trip_count').desc())
    result = df.groupBy(
        F.col('from_station_id').alias('station_id'),
        F.col('from_station_name').alias('station_name'),
        F.date_trunc('month', 'start_time').alias('month')
    ) \
        .agg(F.count('*').alias('trip_count')) \
        .withColumn('rank', F.rank().over(window)) \
        .filter(F.col('rank') == 1) \
        .orderBy('month')
    print('----- END OF QUERY 3 -----')
    return result

def query4(df):
    # What were the top 3 trip stations each day for the last two weeks?
    print('----- QUERY 4 -----')
    # finding the first day
    starting_day = df.select(F.date_sub(F.max('start_time'), 14).alias('starting_day')).first()['starting_day']
    print(f'Starting day: {starting_day}')
    window = Window.partitionBy('day').orderBy(F.col('trip_count').desc())
    result = df.filter(F.col('start_time') >= starting_day) \
        .groupBy(
            F.date_trunc('day', 'start_time').alias('day'),
            F.col('from_station_id').alias('station_id'),
            F.col('from_station_name').alias('station_name')
        ).agg(F.count('*').alias('trip_count')) \
        .withColumn('rownum', F.row_number().over(window)) \
        .filter(F.col('rownum') <= 3)
                 
    print('----- END QUERY 4 -----')
    return result

def query5(df):
    # Do Males or Females take longer trips on average?
    print('----- QUERY 5 -----')
    result = df.groupBy(F.col('gender')) \
        .agg(F.avg('tripduration').alias('average_trip_duration'), 
             F.count('*').alias('trip_count'))
    print('----- END QUERY 5 -----')
    return result

def query6(df):
    # What is the top 10 ages of those that take the longest trips, and shortest?
    print('----- QUERY 6 -----')
    # age, duration, rownum
    shortest = df.orderBy(F.col('tripduration').asc()) \
        .withColumn('age', F.lit(datetime.now().year) - F.col('birthyear')) \
        .select('trip_id', 'tripduration', 'birthyear', 'age') \
        .limit(10)
    longest = df.orderBy(F.col('tripduration').desc()) \
        .withColumn('age',F.lit(datetime.now().year) - F.col('birthyear')) \
        .select('trip_id', 'tripduration', 'birthyear', 'age') \
        .limit(10)
    result = shortest.union(longest)
    print('----- END QUERY 6 -----')
    return result

def data_load_and_preparation(spark):
    df_2019 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[0] + ".csv")}', header=True, inferSchema=True)
    df_2020 = spark.read.csv(f'{os.path.join(file_folder_path, file_list[1] + ".csv")}', header=True, inferSchema=True)

    # 2020 df >> 2019 df (which has more fields)
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

    # merge the dfs
    common_columns = list(set(df_2019.columns) & set(df_2020.columns))
    df_merged = df_2019.select(common_columns).unionByName(df_2020.select(common_columns))

    # typing
    df_merged = df_merged.withColumn("from_station_id", df_merged["from_station_id"].cast(IntegerType()))
    df_merged = df_merged.withColumn("bikeid", df_merged["bikeid"].cast(IntegerType()))
    df_merged = df_merged.withColumn("start_time", F.to_timestamp(df_merged["start_time"], "yyyy-MM-dd HH:mm:SS"))
    df_merged = df_merged.withColumn("end_time", F.to_timestamp(df_merged["end_time"], "yyyy-MM-dd HH:mm:SS"))

    # creating view, required for some sql queries
    df_merged.createOrReplaceTempView("bikes")

    # check schema
    df_merged.printSchema()

    return df_merged, df_2019, df_2020

def main():
    
    # decompress
    for f in file_list:
        f_path = os.path.join(file_folder_path, f + '.zip')
        if zipfile.is_zipfile(f_path):
            print(f'Extracting {f_path}')
            with zipfile.ZipFile(f_path, "r") as z:
                z.extractall(file_folder_path)
            print('Extracted')

    # init spark
    spark = SparkSession.builder.appName("Exercise6").enableHiveSupport().getOrCreate()

    # load data
    df_merged, df_2019, df_2020 = data_load_and_preparation(spark)
    df_2019.printSchema()

    # queries
    #query1(spark) # no df is required, it uses the view "bikes"
    #query2(df_merged).show(5)
    #query3(df_merged).show(50)
    #query4(df_merged).show()
    query5(df_2019).show()
    #query6(df_2019).show()
    

# 2019: trip_id,start_time,end_time,bikeid,tripduration,from_station_id,from_station_name,to_station_id,to_station_name,usertype,gender,birthyear
# 2020: ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual
    
if __name__ == "__main__":
    main()
