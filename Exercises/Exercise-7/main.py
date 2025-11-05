from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import zipfile, os, pandas as pd
from io import BytesIO

download_uri = 'https://www.backblaze.com/b2/hard-drive-test-data.html'
file_folder_path = 'data'
zip_file_name = 'hard-drive-2022-01-01-failures.csv.zip'

def load_zip_into_spark(spark):
    zip_file_path = os.path.join(file_folder_path, zip_file_name)
    print(f"Reading {zip_file_path}")

    # read in memory
    with zipfile.ZipFile(zip_file_path, "r") as z:
        csv_file_name = z.namelist()[0]
        print(f"File name: {csv_file_name}")
        try:
            with z.open(csv_file_name) as f:
                pd_df = pd.read_csv(f)
                print(f"Size: {pd_df.shape}")
                print(pd_df.head(5))
        except FileNotFoundError:
            print("Error: FileNotFoundError")
        except Exception as e:
            print(f"Error: {e}")

    print("Loading into spark")
    df = spark.createDataFrame(pd_df)
    print("Done loading into memory, sample:")
    return df

def parquet_exists(save_location):
    return os.path.exists(save_location) and any(f.endswith(".parquet") for f in os.listdir(save_location))

def print_subset(df, count):
    df.select("date", "serial_number", "model", "capacity_bytes", "source_file").show(count)    

def get_df(spark):
    save_location = os.path.join(file_folder_path, "temp_parquet")
    if not parquet_exists(save_location):
        print("Dataframe never loaded (no parquet file)")
        df = load_zip_into_spark(spark)
        print('Saving to a temporary parquet file')
        df = df.repartition(500)
        df.write.option("compression", "none").mode("overwrite").parquet(save_location)
        print(f"Saved in {save_location}")
        return df
    else:
        print("Dataframe already loaded previously, using parquet")
        df = spark.read.parquet(save_location)
        return df

def query1(df):
    return df.withColumn("source_file", F.lit(zip_file_name[:-3]))

def main():
    # init pyspark
    spark = SparkSession.builder \
        .appName("Exercise7") \
        .config("spark.driver.memory", "6g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "100") \
        .config("spark.default.parallelism", "100") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .enableHiveSupport().getOrCreate()
    

    df = get_df(spark)
    print_subset(df, 1)
    
    df = query1(df)
    print_subset(df, 5)
    
    
    # your code here


if __name__ == "__main__":
    main()
