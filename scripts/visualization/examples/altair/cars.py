#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

import os
import sys
from pathlib import Path

import altair as alt
from vega_datasets import data

# %%

alt.renderers.enable("mimetype" if "ipykernel" in sys.modules else "altair_viewer")
# %%

# Load the cars dataset
cars = data.cars()
# %%

# Create an interval selection
brush = alt.selection_interval()
# %%

points = (
    alt.Chart(cars)
    .mark_point()
    .encode(
        x="Horsepower:Q",
        y="Miles_per_Gallon:Q",
        color=alt.condition(brush, "Origin:N", alt.value("lightgray")),
    )
    .add_selection(brush)
)

# Create a bar chart
bars = (
    alt.Chart(cars)
    .mark_bar()
    .encode(y="Origin:N", color="Origin:N", x="count(Origin):Q")
    .transform_filter(brush)
)

chart = points & bars
# %%

research_output = os.getenv("RESEARCH_OUTPUT")
if research_output:
    output_path = Path(research_output)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    if not output_path.is_dir():
        raise ValueError(f"The path {output_path} is not a directory")
else:
    output_path = Path.home()

html_path = output_path.joinpath("visualization", "examples", "altair", "cars.html")
html_path.parent.mkdir(parents=True, exist_ok=True)
chart.save(str(html_path))

chart.show()
# %%
