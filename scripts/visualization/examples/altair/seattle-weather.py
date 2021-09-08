#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

import os
from pathlib import Path

import altair as alt
from vega_datasets import data

# %%

settle_data = data.seattle_weather()
# %%

scale = alt.Scale(
    domain=["sun", "fog", "drizzle", "rain", "snow"],
    range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
)
# %%

color = alt.Color("weather:N", scale=scale)
# %%

# We create two selections
# - a brush that is active on the top panel
# - a multi-click that is active on the bottom panel
brush = alt.selection_interval(encodings=["x"])
click = alt.selection_multi(encodings=["color"])
# %%

# 1. Top panel is scatter plot of temperature vs time
points = (
    alt.Chart()
    .mark_point()
    .encode(
        alt.X("monthdate(date):T", title="Date"),
        alt.Y(
            "temp_max:Q",
            title="Maximum Daily Temperature (C)",
            scale=alt.Scale(domain=[-5, 40]),
        ),
        color=alt.condition(brush, color, alt.value("lightgray")),
        size=alt.Size("precipitation:Q", scale=alt.Scale(range=[5, 200])),
    )
    .properties(width=550, height=300)
    .add_selection(brush)
    .transform_filter(click)
)
# %%

# 2. Bottom panel is a bar chart of weather type
bars = (
    alt.Chart()
    .mark_bar()
    .encode(
        x="count()",
        y="weather:N",
        color=alt.condition(click, color, alt.value("lightgray")),
    )
    .transform_filter(brush)
    .properties(
        width=550,
    )
    .add_selection(click)
)
# %%

# 3. Build Compound Plot
chart = alt.vconcat(points, bars, data=settle_data, title="Seattle Weather: 2012-2015")
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

html_path = output_path.joinpath(
    "visualization", "examples", "altair", "seattle-weather.html"
)
html_path.parent.mkdir(parents=True, exist_ok=True)
chart.save(str(html_path))

chart.show()
# %%
