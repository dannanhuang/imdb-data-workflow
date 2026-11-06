from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


BASE_DIR = Path(__file__).resolve().parent


def analyse_data():

    # 1. read the data and index
    df = pd.read_csv(BASE_DIR / "data" / "imdb_cleaned.csv")

    results_dir = BASE_DIR / "results"

    genre_stats = pd.read_csv(results_dir / "genre_stats.csv")
    runtime_by_year = pd.read_csv(results_dir / "runtime_by_year.csv")
    business_stats = pd.read_csv(results_dir / "business_stats.csv")
    threshold_data = pd.read_csv(results_dir / "gross_threshold.csv")

    gross_threshold = threshold_data["Gross_threshold"].iloc[0]

    # 2. create bar chat of gross index type
    earning_fig = px.bar(
        genre_stats,
        x="Genre",
        y="Average_earning_per_score",
        title="Average Earning per IMDb Score Point by Genre"
    )

    # 3. create bar chat of high gross proportion
    business_fig = px.bar(
        business_stats,
        x="Genre",
        y="High_gross_rate",
        hover_data=["Movie_count"],
        title="High-Grossing Movie Proportion by Genre"
    )

    business_fig.update_yaxes(title_text="High-grossing movies (%)")

    # 4. annual runtime data for each type of movie
    genre_df = df.copy()
    genre_df["Genre"] = genre_df["Genre"].str.split(",")
    genre_df = genre_df.explode("Genre")
    genre_df["Genre"] = genre_df["Genre"].str.strip()

    genre_names = ["All"] + sorted(
        genre_df["Genre"].dropna().unique()
    )

    # 5.  each type form a line graph
    runtime_fig = go.Figure()

    for genre in genre_names:

        if genre == "All":
            yearly_data = runtime_by_year
        else:
            filtered_df = genre_df[
                genre_df["Genre"] == genre
            ].dropna(subset=["Released_Year", "Runtime"])

            yearly_data = (
                filtered_df.groupby("Released_Year")
                .agg(
                    Average_runtime=("Runtime", "mean"),
                    Movie_count=("Runtime", "size")
                )
                .reset_index()
                .sort_values("Released_Year")
            )

        runtime_fig.add_trace(
            go.Scatter(
                x=yearly_data["Released_Year"],
                y=yearly_data["Average_runtime"],
                mode="lines+markers",
                name=genre,
                visible=(genre == "All")
            )
        )

    # 6. reate the selection 
    buttons = []

    for i, genre in enumerate(genre_names):

        visible = [
            j == i for j in range(len(genre_names))
        ]

        buttons.append(
            dict(
                label=genre,
                method="update",
                args=[
                    {"visible": visible},
                    {"title": "Average Runtime by Year - " + genre}
                ]
            )
        )

    runtime_fig.update_layout(
        title="Average Runtime by Year - All",
        xaxis_title="Release Year",
        yaxis_title="Average Runtime (minutes)",
        updatemenus=[
            dict(
                buttons=buttons,
                active=0,
                x=1,
                y=1.2
            )
        ],
        margin=dict(t=120)
    )

    # 7. transform the first 5 row into HTML graph
    preview_html = df.head().to_html(
        index=False,
        na_rep="",
        escape=True
    )

    earning_html = earning_fig.to_html(
        full_html=False,
        include_plotlyjs=True
    )

    runtime_html = runtime_fig.to_html(
        full_html=False,
        include_plotlyjs=False
    )

    business_html = business_fig.to_html(
        full_html=False,
        include_plotlyjs=False
    )

    # 9. form a page
    page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>IMDB 1000</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: auto;
                padding: 24px;
            }}
            .table-container {{
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <h1>IMDB 1000</h1>

        <h2>First 5 Movies</h2>
        <div class="table-container">{preview_html}</div>

        {earning_html}

        {runtime_html}

        <p>
            High-grossing threshold: {gross_threshold:,.2f}.
            This is the 75th percentile of available Gross values.
        </p>

        {business_html}
    </body>
    </html>
    """

    # 10. save
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "dashboard.html"
    output_path.write_text(page, encoding="utf-8")

    print("Dashboard saved to:", output_path)


if __name__ == "__main__":
    analyse_data()
