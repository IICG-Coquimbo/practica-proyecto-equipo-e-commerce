from pyspark.sql import SparkSession
from scraper import scraper_camila_ramos, Scrapper_Renato_Villalobos

# 1. Recolectamos listas de Python de todos los estudiantes
data_camila = scraper_camila_ramos.ejecutar_extraccion()
data_renatovilla = Scrapper_Renato_Villalobos.ejecutar_extraccion()

# 2. Iniciamos Spark
spark = SparkSession.builder \
    .appName("IntegradoraBigData") \
    .config("spark.mongodb.output.uri", "mongodb+srv://Renato_Villalobos:ubeiW7202\@@#%@cluster0.khaasrk.mongodb.net/?retryWrites=true&w=majority") \
    .getOrCreate()

# 3. Spark convierte las listas en un solo DataFrame unificado
df_camila = spark.createDataFrame(data_camila)
df_renatovilla = spark.createDataFrame(data_renatovilla)

df_final = df_camila.union(df_renatovilla)

# 4. A C C I N DE SPARK: Limpieza y Transformaci n
# Por ejemplo: Quitar s mbolos de moneda y convertir a n m e r o en milisegundos
from pyspark.sql.functions import col, regexp_replace

df_limpio = df_final.withColumn("valor_numerico", regexp_replace(col("valor"), "[^0-9]", "").cast("float"))

df_limpio.write.format("mongodb").mode("append").save()

