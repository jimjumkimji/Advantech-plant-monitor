import pandas as pd
import io

def csv_to_json(binary_data):
    df = pd.read_csv(io.BytesIO(binary_data))
    return df.to_dict(orient="records")
