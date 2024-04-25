# Data Engineer Test at Data Wow
Auther : Phanuphong Siriphongwatana

In this datapipeline will use airflow for pipeline managing and postgres database. All of the service will be on docker container using docker-compose.

## Prerequisites
To run this data pipeline please download and extract from this [Google drive link](https://drive.google.com/drive/folders/1X5mtciwiFYgEbDswzivNCxigq14O1Gw-?usp=sharing)

Ensure you have the following installed on your system:
- Docker
- Docker Compose

## Steps running pipeline

### 1. Set up the Docker Environment
- Download zip file and extract to your local machine.
- Navigate to the project directory (airflow).

### 2. Airflow DAG
- Inside this project there already contain DAG file in `dags` folder (datapipeline_dags.py).
- DAG containing three tasks:
  1. `generate_data_sample`: This task will generate sample data.
  2. `preprocess`: This task will preprocess will sperate data into 3 tables.
  3. `ingest_data_to_postgres`: This task will ingest the preprocessed data into PostgreSQL.

### 3.Run Docker Containers
- You can start the containers by using 
```
docker-compose up -d
```
- Docker will start three container:
    1. Airflow
    2. Postgres : For airflow
    3. Postgres2 : For ingest data from pipeline

- In this process will create three table in Postgres
    1. department
    2. product
    3. sensor
**Please see Database Diagram in sperate file.**
### 4. Login into Airflow console.
- Use web browser and go to localhost:8080 
- Login using :
    - **Username** : airflow
    - **Password** : airflow

### 5. Running pipeline
- In the DAG details page, you will see an DAG call data_pipeline.
- Click on the DAG name to view its details.
- Turn on DAG by click the `Pause/Unpause` near DAG name.
- Trigger the DAG by click on the `trigger button` (play button).
- Monitor for DAG run process to be green mean success.

### 6. Check data in Postgres
- Connecting to Postgres with your program of choice.
- Using HOST : `localhost:5434`
- Table :
    1. department
    2. product
    3. sensor

## Additional Notes
- This process take 31 minutes to run.
- Using PySpark provides a better approach for managing large scale data processing in big data environments.
