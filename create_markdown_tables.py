TESTS = [
    "get user",
    "update user",
    "plain",
    "to json",
]
import pandas as pd
from markdownTable import markdownTable

if __name__ == "__main__":
    import json

    with open("./reports/2023-01-30.json", "r") as f:
        data = json.loads(f.read())["results"]
    df = pd.DataFrame.from_dict(
        {i: r for (i, r) in enumerate(data)},
        orient="index",
        columns=[
            "test_name",
            "language",
            "webserver_name",
            "database",
            "orm",
            "requests_per_second",
            "latency_p50",
            "latency_p75",
            "latency_p90",
            "latency_p99",
        ],
    )
    df.loc[df["test_name"] == "to json", "orm"] = None
    df.loc[df["test_name"] == "to json", "database"] = None
    df.loc[df["test_name"] == "plain", "orm"] = None
    df.loc[df["test_name"] == "plain", "database"] = None

    df.drop_duplicates(subset=["test_name", "webserver_name", "database", "orm"])

    for test in TESTS:
        try:
            tdf = df[df["test_name"] == test]
            if test in ("plain", "to json"):

                del tdf['orm']
                del tdf['database']

            del tdf['test_name']
            table = (
                markdownTable(tdf.sort_values(by="requests_per_second", ascending=False).to_dict(orient="records"))
                .setParams(row_sep="markdown")
                .getMarkdown()
            )
            print(table)
        except Exception as e:
            print(e)
