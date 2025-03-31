import seaborn as sns
import os
import pandas as pd
import altair as alt
from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget
from shiny import App, render, ui
from faicons import icon_svg
import matplotlib.pyplot as plt
from shapely.geometry import Point
import geopandas as gpd
import contextily as ctx


# Define the app directory and read the data
app_dir = "/Users/kishikamahajan/Desktop/UPReP/dashboard/"
combined_data = pd.read_csv("/Users/kishikamahajan/Desktop/UPReP/basic-navigation/combined_data.csv")
combined_data['Manner of Death'] = combined_data['Manner of Death'].replace("ACCIDENT", "Accident")
combined_data['Manner of Death'] = combined_data['Manner of Death'].replace("HOMICIDE", "Homicide")
combined_data['Manner of Death'] = combined_data['Manner of Death'].replace("SUICIDE", "Suicide")


raw_data = pd.read_csv("/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Medical_Examiner_Case_Archive_20250109.csv")
raw_data['Date of Incident'] = pd.to_datetime(raw_data['Date of Incident'], errors='coerce')
raw_data['Incident Month'] = raw_data['Date of Incident'].dt.month
raw_data['Incident Year'] = raw_data['Date of Incident'].dt.year
raw_data = raw_data[~raw_data["Manner of Death"].isin(["PENDING", "UNDETERMINED", "NATURAL"])]
raw_data = raw_data[raw_data["Incident Year"] > 2013]
raw_data = raw_data[raw_data["Incident Year"] < 2025]
raw_data['Manner of Death'] = raw_data['Manner of Death'].replace("ACCIDENT", "Accident")
raw_data['Manner of Death'] = raw_data['Manner of Death'].replace("HOMICIDE", "Homicide")
raw_data['Manner of Death'] = raw_data['Manner of Death'].replace("SUICIDE", "Suicide")

raw_data_transform = pd.read_csv("/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Medical_Examiner_Case_Archive_20250109.csv")
binary_columns = ['Gun Related', 'Opioid Related', 'Cold Related', 'Heat Related']
expanded_rows = []

for _, row in raw_data_transform.iterrows():
    true_causes = [col for col in binary_columns if pd.notna(row[col]) and row[col] == True]

    # Create a new row for each true value
    for cause in true_causes:
        new_row = row.copy()
        new_row['Transformed Manner of Death'] = cause  # Only one cause per row
        expanded_rows.append(new_row)

# Create new DataFrame with expanded rows
raw_data_transform_expanded = pd.DataFrame(expanded_rows)

raw_data_transform_expanded['Date of Incident'] = pd.to_datetime(raw_data_transform_expanded['Date of Incident'], errors='coerce')
raw_data_transform_expanded['Incident Month'] = raw_data_transform_expanded['Date of Incident'].dt.month
raw_data_transform_expanded['Incident Year'] = raw_data_transform_expanded['Date of Incident'].dt.year
raw_data_transform_expanded = raw_data_transform_expanded[raw_data_transform_expanded["Incident Year"] > 2013]
raw_data_transform_expanded = raw_data_transform_expanded[raw_data_transform_expanded["Incident Year"] < 2025]


# The contents of the first 'page' is a navset with two 'panels'.
page1 = ui.page_sidebar(
    ui.sidebar(
        ui.input_checkbox_group(
            "Manner_of_Death",
            "Manner of Death",
            choices=["Accident", "Homicide", "Suicide", "Gun Related", "Heat Related", "Cold Related", "Opioid Related"],
            selected=["Accident"]
        ),
        title="Filter the cause of death",
    ),
    ui.navset_tab(  # Use ui.navset_tab here to wrap the navigation items
        ui.nav_panel(
            output_widget("line_graph")
        )
    ),
    title="Trends of Deaths Overtime",
    fillable=True,
)

# Accidents
page2 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_accidents"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_accidents"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_accidents"),  # First pie chart
                title="Bar Chart 1"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_accidents"),  # Second pie chart
                title="Pie Chart 2"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_accidents"),  # Map placeholder
            title="Map Visualization",
        ),
    ),
)

# Homicides
page3 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_2", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_homicides"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_homicides"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_homicides"),  # First pie chart
                title="Bar Chart 1 - Homicides"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_homicides"),  # Second pie chart
                title="Pie Chart 2 - Homicides"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_homicides"),  # Map placeholder
            title="Map Visualization - Homicides",
        ),
    ),
)

# Suicides
page4 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_3", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_suicides"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_suicides"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_suicide"),  # First pie chart
                title="Bar Chart 1 - Suicide"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_suicides"),  # Second pie chart
                title="Pie Chart 2 - Suicide"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_suicides"),  # Map placeholder
            title="Map Visualization - Suicides",
        ),
    ),
)

# Gun Related deaths
page5 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_4", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_guns"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_guns"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_guns"),  # First pie chart
                title="Bar Chart 1 - Gun"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_guns"),  # Second pie chart
                title="Pie Chart 2 - Gun"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_guns"),  # Map placeholder
            title="Map Visualization - Guns",
        ),
    ),
)

# Cold Related
page6 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_5", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_cold"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_cold"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_cold"),  # First pie chart
                title="Bar Chart 1 - Cold"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_cold"),  # Second pie chart
                title="Pie Chart 2 - Cold"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_cold"),  # Map placeholder
            title="Map Visualization - Cold",
        ),
    ),
)

# Heat Related    
page7 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_6", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_heat"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_heat"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_heat"),  # First pie chart
                title="Bar Chart 1 - Heat"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_heat"),  # Second pie chart
                title="Pie Chart 2 - Heat"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_heat"),  # Map placeholder
            title="Map Visualization - Heat",
        ),
    ),
)

# Opioid Related    
page8 = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("year_slider_7", "Year of Death", 2014, 2024, 1),
        title="Filter the year of death",
    ),
    ui.layout_column_wrap(
        # Top section: Retaining the two value boxes
        ui.value_box(
            "Total number of deaths",
            ui.output_text("count_opioid"),
            showcase=icon_svg("person"),
        ),
        ui.value_box(
            "Deaths in this year",
            ui.output_text("deaths_selected_year_opioid"),
            showcase=icon_svg("chart-line"),
        ),
    ),
    ui.layout_column_wrap(
        1/2, 
        # Left half with two pie charts, stacked vertically
        ui.layout_column_wrap(
            1,  # Full width within the left half for stacking two charts
            ui.card(
                ui.output_plot("bar_chart_age_opioid"),  # First pie chart
                title="Bar Chart 1 - Opioid"
            ),
            ui.card(
                ui.output_plot("pie_chart_gender_opioid"),  # Second pie chart
                title="Pie Chart 2 - Opioid"
            ),
        ),
        # Right half with a map
        ui.card(
            ui.output_plot("map_opioid"),  # Map placeholder
            title="Map Visualization - Opioid",
        ),
    ),
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),  # Push the navbar items to the right
    ui.nav_panel("Overtime Trends", page1),
    ui.nav_panel("Accidents", page2),
    ui.nav_panel("Homicides", page3),
    ui.nav_panel("Suicides", page4),
    ui.nav_panel("Gun Related", page5),
    ui.nav_panel("Cold Related", page6),
    ui.nav_panel("Heat Related", page7),
    ui.nav_panel("Opioid Related", page8),
    title = "Analysis of Causes of Deaths in Cook County",
)


# Define the Server
def server(input, output, session):
    @reactive.calc
    def filtered_df():
        # Filter the data based on the selected causes of death
        filtered_df = combined_data[combined_data["Manner of Death"].isin(input["Manner_of_Death"]())]
        return filtered_df
    
    @output
    @render_altair
    def line_graph():
        chart = alt.Chart(filtered_df()).mark_line().encode(
            x=alt.X('Year-Month:T', title='Year'),  
            y=alt.Y('Count:Q', title='Number of Cases'),
            color=alt.Color('Manner of Death:N', title='Category'),
            tooltip=['Manner of Death', 'Year-Month', 'Count']
            ).properties(
                title="Trends of Cases Over Time",
            width=800,
            height=400
        )
        return chart

    # Accidents Page
    @reactive.calc
    def accident_df():
        # Filter accidents data
        accident_df = combined_data[combined_data["Manner of Death"] == "Accident"]
        accident_df['Year-Month'] = pd.to_datetime(accident_df['Year-Month'], errors='coerce')
        accident_df["Year"] = accident_df["Year-Month"].dt.year
        # Filter by selected years from the slider
        selected_year = input["year_slider"]()  # Get the selected year from the slider input
        accident_df_filtered = accident_df[accident_df["Year"] == selected_year]  # Apply the filter

        return accident_df_filtered
    
    @render.text
    def count_accidents():
        accidents_count = combined_data[combined_data["Manner of Death"] == "Accident"]
        accidents_total = accidents_count["Count"].sum()
        return accidents_total
    
    @reactive.calc
    @render.text
    def deaths_selected_year_accidents():
        df = accident_df()  # Use accident_df() to get the filtered DataFrame
        accidents_year = df["Count"].sum()
        return accidents_year

    @render.plot
    def bar_chart_age_accidents():
        accident_type = raw_data[raw_data["Manner of Death"] == "Accident"]        
        accident_type_filtered = accident_type[accident_type["Incident Year"] == input["year_slider"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        accident_type_filtered['Age Group'] = pd.cut(accident_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = accident_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_accident_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Accidents', pad=20, fontsize=16, fontweight='bold')

        return age_accident_plot

    @render.plot
    def pie_chart_gender_accidents():
        accident_type = raw_data[raw_data["Manner of Death"] == "Accident"]
        accident_type_filtered = accident_type[accident_type["Incident Year"] == input["year_slider"]()]
        gender_counts = accident_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_accident_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Accidents', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_accident_plot
    
    @render.plot
    def map_accidents():
        # First create the GeoDataFrame with the correct CRS
        accident_type = raw_data[raw_data["Manner of Death"] == "Accident"]
        accident_type_filtered = accident_type[accident_type["Incident Year"] == input["year_slider"]()]
        geometry = [Point(xy) for xy in zip(accident_type_filtered['longitude'], accident_type_filtered['latitude'])]
        accident_filtered_gdf = gpd.GeoDataFrame(
            accident_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        accident_filtered_gdf = accident_filtered_gdf.to_crs(shapefile_crs)

        accident_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        accident_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Accidents in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return accident_deaths_map 
    
    # Homicides page
    @reactive.calc
    def homicide_df():
        # Filter accidents data
        homicide_df = combined_data[combined_data["Manner of Death"] == "Homicide"]
        homicide_df['Year-Month'] = pd.to_datetime(homicide_df['Year-Month'], errors='coerce')
        homicide_df["Year"] = homicide_df["Year-Month"].dt.year
        # Filter by selected years from the slider
        selected_year = input["year_slider_2"]()  # Get the selected year from the slider input
        homicide_df_filtered = homicide_df[homicide_df["Year"] == selected_year]  # Apply the filter

        return homicide_df_filtered

    @render.text
    def count_homicides():
        homicides_count = combined_data[combined_data["Manner of Death"] == "Homicide"]
        homicides_count = homicides_count["Count"].sum()
        return homicides_count
    
    @reactive.calc
    @render.text
    def deaths_selected_year_homicides():
        df_2 = homicide_df()  
        homicides_year = df_2["Count"].sum()
        return homicides_year
    
    @render.plot
    def bar_chart_age_homicides():
        homicide_type = raw_data[raw_data["Manner of Death"] == "Homicide"]        
        homicide_type_filtered = homicide_type[homicide_type["Incident Year"] == input["year_slider_2"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        homicide_type_filtered['Age Group'] = pd.cut(homicide_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = homicide_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_homicide_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Homicides', pad=20, fontsize=16, fontweight='bold')
        return age_homicide_plot

    @render.plot
    def pie_chart_gender_homicides():
        homicide_type = raw_data[raw_data["Manner of Death"] == "Homicide"]
        homicide_type_filtered = homicide_type[homicide_type["Incident Year"] == input["year_slider_2"]()]
        gender_counts = homicide_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_homicide_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Homicides', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_homicide_plot
    
    @render.plot
    def map_homicides():
        # First create the GeoDataFrame with the correct CRS
        homicide_type = raw_data[raw_data["Manner of Death"] == "Homicide"]
        homicide_type_filtered = homicide_type[homicide_type["Incident Year"] == input["year_slider_2"]()]
        geometry = [Point(xy) for xy in zip(homicide_type_filtered['longitude'], homicide_type_filtered['latitude'])]
        homicide_filtered_gdf = gpd.GeoDataFrame(
            homicide_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        homicide_filtered_gdf = homicide_filtered_gdf.to_crs(shapefile_crs)

        homicide_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        homicide_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Homicides in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return homicide_deaths_map
    
    # Suicide page
    @reactive.calc
    def suicide_df():
        # Filter accidents data
        suicide_df = combined_data[combined_data["Manner of Death"] == "Suicide"]
        suicide_df['Year-Month'] = pd.to_datetime(suicide_df['Year-Month'], errors='coerce')
        suicide_df["Year"] = suicide_df["Year-Month"].dt.year
        # Filter by selected years from the slider
        selected_year = input["year_slider_3"]()  # Get the selected year from the slider input
        suicide_df_filtered = suicide_df[suicide_df["Year"] == selected_year]  # Apply the filter

        return suicide_df_filtered

    @render.text
    def count_suicides():
        suicides_count = combined_data[combined_data["Manner of Death"] == "Suicide"]
        suicides_count = suicides_count["Count"].sum()
        return suicides_count
    
    @reactive.calc
    @render.text
    def deaths_selected_year_suicides():
        df_3 = suicide_df()  
        suicides_year = df_3["Count"].sum()
        return suicides_year
    
    @render.plot
    def bar_chart_age_suicide():
        suicide_type = raw_data[raw_data["Manner of Death"] == "Suicide"]        
        suicide_type_filtered = suicide_type[suicide_type["Incident Year"] == input["year_slider_3"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        suicide_type_filtered['Age Group'] = pd.cut(suicide_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = suicide_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_suicide_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Suicides', pad=20, fontsize=16, fontweight='bold')
        return age_suicide_plot

    @render.plot
    def pie_chart_gender_suicides():
        suicide_type = raw_data[raw_data["Manner of Death"] == "Homicide"]
        suicide_type_filtered = suicide_type[suicide_type["Incident Year"] == input["year_slider_3"]()]
        gender_counts = suicide_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_suicide_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Suicides', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_suicide_plot
    
    @render.plot
    def map_suicides():
        # First create the GeoDataFrame with the correct CRS
        suicide_type = raw_data[raw_data["Manner of Death"] == "Suicide"]
        suicide_type_filtered = suicide_type[suicide_type["Incident Year"] == input["year_slider_3"]()]
        geometry = [Point(xy) for xy in zip(suicide_type_filtered['longitude'], suicide_type_filtered['latitude'])]
        suicide_filtered_gdf = gpd.GeoDataFrame(
            suicide_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        suicide_filtered_gdf = suicide_filtered_gdf.to_crs(shapefile_crs)

        suicide_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        suicide_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Suicides in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return suicide_deaths_map


    # Gun Related Page
    @reactive.calc
    def gun_df():
        # Filter accidents data
        gun_df = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Gun Related"]
        # Filter by selected years from the slider
        selected_year = input["year_slider_4"]()  # Get the selected year from the slider input
        gun_df_filtered = gun_df[gun_df["Incident Year"] == selected_year]  # Apply the filter

        return gun_df_filtered
    
    @render.text
    def count_guns():
        guns_count = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Gun Related"]
        guns_total = len(guns_count)
        return guns_total
    
    @reactive.calc
    @render.text
    def deaths_selected_year_guns():
        df = gun_df()  
        selected_year = input["year_slider_4"]()
        guns_year = len(df.loc[df['Incident Year'] == selected_year])
        return guns_year

    @render.plot
    def bar_chart_age_guns():
        gun_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Gun Related"]        
        gun_type_filtered = gun_type[gun_type["Incident Year"] == input["year_slider_4"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        gun_type_filtered['Age Group'] = pd.cut(gun_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = gun_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_gun_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Gun Relates Deaths', pad=20, fontsize=16, fontweight='bold')

        return age_gun_plot

    @render.plot
    def pie_chart_gender_guns():
        gun_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Gun Related"]
        gun_type_filtered = gun_type[gun_type["Incident Year"] == input["year_slider_4"]()]
        gender_counts = gun_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_gun_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Gun Related Deaths', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_gun_plot
    
    @render.plot
    def map_guns():
        # First create the GeoDataFrame with the correct CRS
        gun_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Gun Related"]
        gun_type_filtered = gun_type[gun_type["Incident Year"] == input["year_slider_4"]()]
        geometry = [Point(xy) for xy in zip(gun_type_filtered['longitude'], gun_type_filtered['latitude'])]
        gun_filtered_gdf = gpd.GeoDataFrame(
            gun_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        gun_filtered_gdf = gun_filtered_gdf.to_crs(shapefile_crs)

        gun_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        gun_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Accidents in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return gun_deaths_map
    
    # Cold Related Page
    @reactive.calc
    def cold_df():
        # Filter accidents data
        cold_df = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]
        # Filter by selected years from the slider
        selected_year = input["year_slider_5"]()  # Get the selected year from the slider input
        cold_df_filtered = cold_df[cold_df["Incident Year"] == selected_year]  # Apply the filter

        return cold_df_filtered
    
    @render.text
    def count_cold():
        cold_count = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]
        cold_total = len(cold_count)
        return cold_total
    
    @reactive.calc
    @render.text
    def deaths_selected_year_cold():
        df = cold_df()  
        selected_year = input["year_slider_5"]()
        cold_year = len(df.loc[df['Incident Year'] == selected_year])
        return cold_year

    @render.plot
    def bar_chart_age_cold():
        cold_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]        
        cold_type_filtered = cold_type[cold_type["Incident Year"] == input["year_slider_5"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        cold_type_filtered['Age Group'] = pd.cut(cold_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = cold_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_cold_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Cold Relates Deaths', pad=20, fontsize=16, fontweight='bold')

        return age_cold_plot

    @render.plot
    def pie_chart_gender_cold():
        cold_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]
        cold_type_filtered = cold_type[cold_type["Incident Year"] == input["year_slider_5"]()]
        gender_counts = cold_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_cold_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Cold Related Deaths', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_cold_plot
    
    @render.plot
    def map_cold():
        # First create the GeoDataFrame with the correct CRS
        cold_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]
        cold_type_filtered = cold_type[cold_type["Incident Year"] == input["year_slider_5"]()]
        geometry = [Point(xy) for xy in zip(cold_type_filtered['longitude'], cold_type_filtered['latitude'])]
        cold_filtered_gdf = gpd.GeoDataFrame(
            cold_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        cold_filtered_gdf = cold_filtered_gdf.to_crs(shapefile_crs)

        cold_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        cold_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Cold in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return cold_deaths_map
    
    # Heat Related Page
    @reactive.calc
    def heat_df():
        # Filter accidents data
        heat_df = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Heat Related"]
        # Filter by selected years from the slider
        selected_year = input["year_slider_6"]()  # Get the selected year from the slider input
        heat_df_filtered = heat_df[heat_df["Incident Year"] == selected_year]  # Apply the filter

        return heat_df_filtered
    
    @render.text
    def count_heat():
        heat_count = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Heat Related"]
        heat_total = len(heat_count)
        return heat_total
    
    @reactive.calc
    @render.text
    def deaths_selected_year_heat():
        df = heat_df()  
        selected_year = input["year_slider_6"]()
        heat_year = len(df.loc[df['Incident Year'] == selected_year])
        return heat_year

    @render.plot
    def bar_chart_age_heat():
        heat_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Cold Related"]        
        heat_type_filtered = heat_type[heat_type["Incident Year"] == input["year_slider_6"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        heat_type_filtered['Age Group'] = pd.cut(heat_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = heat_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_heat_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Heat Related Deaths', pad=20, fontsize=16, fontweight='bold')

        return age_heat_plot

    @render.plot
    def pie_chart_gender_heat():
        heat_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Heat Related"]
        heat_type_filtered = heat_type[heat_type["Incident Year"] == input["year_slider_6"]()]
        gender_counts = heat_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_heat_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Heat Related Deaths', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_heat_plot
    
    @render.plot
    def map_heat():
        # First create the GeoDataFrame with the correct CRS
        heat_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Heat Related"]
        heat_type_filtered = heat_type[heat_type["Incident Year"] == input["year_slider_6"]()]
        geometry = [Point(xy) for xy in zip(heat_type_filtered['longitude'], heat_type_filtered['latitude'])]
        heat_filtered_gdf = gpd.GeoDataFrame(
            heat_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        heat_filtered_gdf = heat_filtered_gdf.to_crs(shapefile_crs)

        heat_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        heat_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Heat in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return heat_deaths_map
    
    # Opioid Related Page
    @reactive.calc
    def opioid_df():
        # Filter accidents data
        opioid_df = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Opioid Related"]
        # Filter by selected years from the slider
        selected_year = input["year_slider_7"]()  # Get the selected year from the slider input
        opioid_df_filtered = opioid_df[opioid_df["Incident Year"] == selected_year]  # Apply the filter

        return opioid_df_filtered
    
    @render.text
    def count_opioid():
        opioid_count = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Opioid Related"]
        opioid_total = len(opioid_count)
        return opioid_total
    
    @reactive.calc
    @render.text
    def deaths_selected_year_opioid():
        df = opioid_df()  
        selected_year = input["year_slider_7"]()
        opioid_year = len(df.loc[df['Incident Year'] == selected_year])
        return opioid_year

    @render.plot
    def bar_chart_age_opioid():
        opioid_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Opioid Related"]        
        opioid_type_filtered = opioid_type[opioid_type["Incident Year"] == input["year_slider_7"]()]
        age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]
        age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        opioid_type_filtered['Age Group'] = pd.cut(opioid_type_filtered['Age'], bins=age_bins, labels=age_labels, right=False)
        age_counts = opioid_type_filtered['Age Group'].value_counts().sort_index()
        # Custom color palettes for each chart
        age_colors = ['#ADD8E6', '#87CEFA', '#4682B4', '#5F9EA0', '#1E90FF', '#00BFFF', '#4169E1', '#0000FF']

        # Age Distribution
        age_opioid_plot = plt.figure(figsize=(10, 8))

        plt.bar(age_counts.index, age_counts.values, color=age_colors, edgecolor='black', alpha=0.7)

        plt.title('Age Distribution for Opioid Related Deaths', pad=20, fontsize=16, fontweight='bold')

        return age_opioid_plot

    @render.plot
    def pie_chart_gender_opioid():
        opioid_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Opioid Related"]
        opioid_type_filtered = opioid_type[opioid_type["Incident Year"] == input["year_slider_7"]()]
        gender_counts = opioid_type_filtered["Gender"].value_counts()
    
        gender_colors = ['#ADD8E6', '#4169E1']
        common_props = {
            'wedgeprops': {'width': 0.7, 'edgecolor': 'white', 'linewidth': 2},
            'textprops': {'fontsize': 12, 'fontweight': 'bold'},
            'startangle': 90,
            'shadow': True
        }
    
        gender_opioid_plot = plt.figure(figsize=(10, 8))
        explode_gender = [0.05, 0.05]  # Separation for both slices

        gender_counts.plot.pie(colors=gender_colors,
        explode=explode_gender,
        autopct='%1.1f%%',
        **common_props)

        plt.title('Gender Distribution for Opioid Related Deaths', pad=20, fontsize=16, fontweight='bold')
        plt.axis('equal')
        return gender_opioid_plot
    
    @render.plot
    def map_opioid():
        # First create the GeoDataFrame with the correct CRS
        opioid_type = raw_data_transform_expanded[raw_data_transform_expanded["Transformed Manner of Death"] == "Opioid Related"]
        opioid_type_filtered = opioid_type[opioid_type["Incident Year"] == input["year_slider_7"]()]
        geometry = [Point(xy) for xy in zip(opioid_type_filtered['longitude'], opioid_type_filtered['latitude'])]
        opioid_filtered_gdf = gpd.GeoDataFrame(
            opioid_type_filtered, 
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 - standard for latitude/longitude coordinates
            )

        shapefile_path = "/Users/kishikamahajan/Desktop/UPReP/basic-navigation/Municipal_Incorporation_Inventory/Municipal_Incorporation_Inventory.shp"
        gdf = gpd.read_file(shapefile_path)
        shapefile_crs = gdf.crs

        # Now transform to match the shapefile's CRS
        opioid_filtered_gdf = opioid_filtered_gdf.to_crs(shapefile_crs)

        opioid_deaths_map = fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the shapefile with a light blue fill
        gdf.plot(ax=ax,
        edgecolor='#2b2b2b',  # Darker edge color
        color='#e6f3ff',      # Light blue fill
        alpha=0.7,            # Slight transparency
        linewidth=0.5)        # Thinner borders

        # Plot accidents with better styling
        opioid_filtered_gdf.plot(ax=ax,
        marker='o', 
        color='Darkblue',    # Brighter red
        markersize=10,      # Larger markers
        alpha=0.4,          # Add transparency
        label='Accidents')

        # Customize the plot
        ax.set_title('Deaths by Opioids in Cook County',
        fontsize=16, 
        pad=20, 
        fontweight='bold')

        # Add a grid with partial transparency
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add a legend
        ax.legend(fontsize=12)

        # Remove axis labels (since they're in projected coordinates)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Adjust layout
        plt.tight_layout()

        ax.set_axis_off()

        return opioid_deaths_map
    
# Create the Shiny app
app = App(app_ui, server)
