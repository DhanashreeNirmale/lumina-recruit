import io
import pandas as pd


def applications_to_dataframe(applications):

    if not applications:
        return pd.DataFrame()

    return pd.DataFrame(applications)


def dataframe_to_csv_bytes(df):

    buffer = io.StringIO()

    df.to_csv(
        buffer,
        index=False
    )

    return buffer.getvalue().encode("utf-8")