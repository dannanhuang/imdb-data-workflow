from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent


def process_data():

    # 1. read the data
    df = pd.read_csv(BASE_DIR / "data" / "imdb_cleaned.csv")

    # 2. seperate movie type
    genre_df = df.copy()
    genre_df["Genre"] = genre_df["Genre"].str.split(",")
    genre_df = genre_df.explode("Genre")
    genre_df["Genre"] = genre_df["Genre"].str.strip()

    # 3. index 1: avg_grossof each score of each type of movie
    valid_genre = genre_df.dropna(
        subset=["Gross", "IMDB_Rating"]
    ).copy()

    valid_genre = valid_genre[
        valid_genre["IMDB_Rating"] > 0
    ].copy()

    valid_genre["Earning_per_score"] = (
        valid_genre["Gross"] / valid_genre["IMDB_Rating"]
    )

    genre_stats = (
        valid_genre.groupby("Genre")
        .agg(
            Average_gross=("Gross", "mean"),
            Average_rating=("IMDB_Rating", "mean"),
            Average_earning_per_score=("Earning_per_score", "mean"),
            Movie_count=("Series_Title", "size")
        )
        .reset_index()
        .sort_values("Average_earning_per_score", ascending=False)
    )

    # 4. index 2：avg_annual_runtime 
    runtime_data = df.dropna(
        subset=["Released_Year", "Runtime"]
    ).copy()

    runtime_data["Released_Year"] = (
        runtime_data["Released_Year"].astype(int)
    )

    runtime_by_year = (
        runtime_data.groupby("Released_Year")
        .agg(
            Average_runtime=("Runtime", "mean"),
            Movie_count=("Runtime", "size")
        )
        .reset_index()
        .sort_values("Released_Year")
    )

    # 5. index 3 ：high gross proportion of each type of movie
    gross_threshold = df["Gross"].quantile(0.75)

    business_data = genre_df.dropna(subset=["Gross"]).copy()

    business_data["High_gross"] = (
        business_data["Gross"] >= gross_threshold
    )

    business_stats = (
        business_data.groupby("Genre")
        .agg(
            Movie_count=("Gross", "size"),
            High_gross_rate=("High_gross", "mean")
        )
        .reset_index()
    )

    business_stats["High_gross_rate"] *= 100

    business_stats = business_stats.sort_values(
        "High_gross_rate",
        ascending=False
    )

    # 6. save 3 index
    output_dir = BASE_DIR / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    genre_stats.to_csv(
        output_dir / "genre_stats.csv", index=False
    )

    runtime_by_year.to_csv(
        output_dir / "runtime_by_year.csv", index=False
    )

    business_stats.to_csv(
        output_dir / "business_stats.csv", index=False
    )

    # save the threshold of high gross
    pd.DataFrame({
        "Gross_threshold": [gross_threshold]
    }).to_csv(
        output_dir / "gross_threshold.csv", index=False
    )

    # 7. print the outcome
    print("Genre indicators:")
    print(genre_stats.head().to_string(index=False))

    print("\nRuntime indicators:")
    print(runtime_by_year.head().to_string(index=False))

    print("\nHigh-grossing threshold:", gross_threshold)

    print("\nHigh-grossing proportions:")
    print(business_stats.head().to_string(index=False))

    print("\nIndicator tables saved to:", output_dir)


if __name__ == "__main__":
    process_data()
