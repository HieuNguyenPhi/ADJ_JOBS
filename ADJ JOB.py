from azure.storage.blob import BlobServiceClient
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_list = blob_service_client.list_containers()
container_name = "adjuststbuatprocessed" #os.getenv('CONTAINER_NAME')
container_client = blob_service_client.get_container_client(container_name)
# already_processed = [file.name.split('/')[1].split('.')[0] for file in container_client.list_blobs() if file.name.split('/')[0] == 'output']
# already_processed[-5:]
already_processed_ts = sorted([file.name.split('/')[-1].split(".")[0] for file in container_client.list_blobs() if file.name.split('/')[0] == 'processing'])
already_processed_ts[-5:]

container_name_uat = "adjuststbuat"
container_client_uat = blob_service_client.get_container_client(container_name_uat)
from collections import defaultdict
files = [i.name for i in container_client_uat.list_blobs()]
groups = defaultdict(list)
for f in files:
    dt = f.split('_')[1]
    groups[dt].append(f)
groups[dt]

from datetime import datetime
import pandas as pd
B = datetime.strptime(dt, "%Y-%m-%dT%H0000")
A = datetime.strptime(already_processed_ts[-2], "%Y-%m-%dT%H0000")
need_process_ts =  pd.date_range(A, B, freq='h').strftime('%Y-%m-%dT%H0000').tolist()
need_process_ts

scheme_df = pl.scan_csv(f"az://adjuststbuat/{groups[dt][-1]}", storage_options = storage_options,glob=True, has_header = True, null_values = ["","NULL"], ignore_errors=True)
scheme_ = {i:pl.Utf8 for i in list(scheme_df.collect_schema())}
scheme_

import polars as pl 
from tqdm import tqdm
storage_options = {
    "account_name": account_name,
    "account_key":  account_key,
}

for ts, files in tqdm(groups.items()):
    if ts not in need_process_ts:
        continue
    dt = ts[:10]
    # if dt not in need_process:
    #     continue
    df = pl.scan_csv(f"az://adjuststbuat/*_{ts}_*.csv.gz", storage_options = storage_options,glob=True, has_header = True, null_values = ["","NULL"], ignore_errors=True, schema_overrides=scheme_)
    print(f'Uploading {dt}/{ts}.parquet')
    df.sink_parquet(f"az://adjuststbuatprocessed/processing/dt={dt}/{ts}.parquet", storage_options = storage_options, compression="snappy")
    print(f'Done dt={dt}/{ts}.parquet')
        
need_process = set([i.split("T")[0] for i in need_process_ts])
need_process

for dt in need_process:
  df = pl.scan_parquet(f"az://adjuststbuatprocessed/processing/dt={dt}/*.parquet", storage_options=storage_options,glob=True).with_columns(pl.lit(dt).alias("dt"))
  print(f'Uploading {dt}.parquet')
  df.sink_parquet(f"az://adjuststbuatprocessed/output/{dt}.parquet", storage_options=storage_options, compression="snappy")
  print(f'\n Done {dt}\n')

# LIVE

already_processed_ts = sorted([file.name.split('/')[-1].split(".")[0] for file in container_client.list_blobs() if (file.name.split('/')[0] + "/" + file.name.split('/')[1]) == 'live/processing'])
already_processed_ts[-5:]

container_name_uat = "adjuststblive"
container_client_uat = blob_service_client.get_container_client(container_name_uat)
from collections import defaultdict
files = [i.name for i in container_client_uat.list_blobs()]
groups = defaultdict(list)
for f in files:
    dt = f.split('_')[1]
    groups[dt].append(f)
groups[dt]

B = datetime.strptime(dt, "%Y-%m-%dT%H0000")
A = datetime.strptime(already_processed_ts[-1], "%Y-%m-%dT%H0000")
need_process_ts =  pd.date_range(A, B, freq='h').strftime('%Y-%m-%dT%H0000').tolist()
need_process_ts

scheme_df = pl.scan_csv(f"az://adjuststblive/{groups[dt][-1]}", storage_options = storage_options,glob=True, has_header = True, null_values = ["","NULL"], ignore_errors=True)
scheme_ = {i:pl.Utf8 for i in list(scheme_df.collect_schema())}
# scheme_

storage_options = {
    "account_name": account_name,
    "account_key":  account_key,
}

for ts, files in tqdm(groups.items()):
    if ts not in need_process_ts: continue
    dt = ts[:10]
    # if dt not in need_process:
    #     continue
    df = pl.scan_csv(f"az://adjuststblive/*_{ts}_*.csv.gz", storage_options = storage_options,glob=True, has_header = True, null_values = ["","NULL"], ignore_errors=True, schema_overrides=scheme_)
    print(f"Uploading {dt}/{ts}.parquet")
    df.sink_parquet(f"az://adjuststbuatprocessed/live/processing/dt={dt}/{ts}.parquet", storage_options = storage_options, compression="snappy")
    print(f'Done dt={dt}/{ts}.parquet')

need_process = ['2025-10-13','2025-10-14']
need_process

import polars as pl
account_name = "ststbrawadjrsbxsea001"
account_key = "EvVJvH/9JGncF743x9hLYWWedJCjbch8UGm81uu5tkEpNOoi8qc3Q+QvisTTg1aTZh1c3FCBvS5W+AStjHx5tg=="
storage_options = {
    "account_name": account_name,
    "account_key":  account_key,
}

for dt in need_process:
  df = pl.scan_parquet(f"az://adjuststbuatprocessed/live/processing/dt={dt}/*.parquet", storage_options=storage_options,glob=True).with_columns(pl.lit(dt).alias("dt"))
  print(f'Uploading {dt}')
  df.sink_parquet(f"az://adjuststbuatprocessed/live/output/{dt}.parquet", storage_options=storage_options, compression="snappy")
  print(f'\n Done {dt}\n')
  

