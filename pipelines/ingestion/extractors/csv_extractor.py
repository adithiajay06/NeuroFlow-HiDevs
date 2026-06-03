import pandas as pd
from . import ExtractedPage

def extract_csv(file_path: str) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []
    df = pd.read_csv(file_path)

    row_count = len(df)
    page_number = 1

    if row_count < 1000:
        # Small CSV → convert to markdown table
        md_table = df.to_markdown(index=False)
        pages.append(
            ExtractedPage(
                page_number=page_number,
                content=md_table,
                content_type="table",
                metadata={"rows": row_count, "mode": "markdown"},
            )
        )
    else:
        # Large CSV → statistical summary + sample blocks
        summary = []
        summary.append("### Column Summary")
        summary.append(str(df.dtypes))

        # Numeric stats
        numeric_stats = df.describe().to_string()
        summary.append("\n### Numeric Stats\n" + numeric_stats)

        # Top-5 categorical values
        for col in df.select_dtypes(include="object").columns:
            top_vals = df[col].value_counts().head(5).to_string()
            summary.append(f"\n### Top values for {col}\n{top_vals}")

        pages.append(
            ExtractedPage(
                page_number=page_number,
                content="\n".join(summary),
                content_type="text",
                metadata={"rows": row_count, "mode": "summary"},
            )
        )

        # Sample blocks of 100 rows
        for start in range(0, row_count, 100):
            block = df.iloc[start:start+100]
            md_block = block.to_markdown(index=False)
            page_number += 1
            pages.append(
                ExtractedPage(
                    page_number=page_number,
                    content=md_block,
                    content_type="table",
                    metadata={"rows": len(block), "start_row": start},
                )
            )

    return pages
