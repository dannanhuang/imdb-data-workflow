from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent


def clean_data():

    # 1. read the data
    input_path = BASE_DIR / "imdb_top_1000.csv"
    df = pd.read_csv(input_path)

    print("Original movie count:", len(df))

    # 2. clean the data 
    df["Gross"] = pd.to_numeric(
        df["Gross"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    df["Runtime"] = pd.to_numeric(
        df["Runtime"].astype(str).str.replace(" min", "", regex=False),
        errors="coerce"
    )

    df["Released_Year"] = pd.to_numeric(
        df["Released_Year"].map(str),
        errors="coerce"
    ).astype("Int64")

    df["IMDB_Rating"] = pd.to_numeric(
        df["IMDB_Rating"],
        errors="coerce"
    )

    print("Missing Gross:", df["Gross"].isna().sum())
    print("Missing Runtime:", df["Runtime"].isna().sum())
    print("Missing Released_Year:", df["Released_Year"].isna().sum())
    print("Missing IMDB_Rating:", df["IMDB_Rating"].isna().sum())

    # 7. create an output file
    output_dir = BASE_DIR / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 8. store the data
    output_path = output_dir / "imdb_cleaned.csv"
    df.to_csv(output_path, index=False)

    print("Cleaned data saved to:", output_path)


# directly run 
if __name__ == "__main__":
    clean_data()
