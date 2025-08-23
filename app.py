import gradio as gr
import pandas as pd
import networkx as nx
import folium
from folium import PolyLine

# --- Load Station Data and Build Graph ---
def load_data(file_path="hyderabad_metro_stations.csv"):
    df = pd.read_csv(file_path)
    G = nx.Graph()
    
    for _, row in df.iterrows():
        G.add_node(row['station'], line=row['line'], lat=row['lat'], lon=row['lon'])

    for line in df['line'].unique():
        line_df = df[df['line'] == line]
        for i in range(len(line_df) - 1):
            G.add_edge(line_df.iloc[i]['station'], line_df.iloc[i + 1]['station'])
    
    return df, G

def get_route(G, start, end):
    try:
        return nx.shortest_path(G, source=start, target=end)
    except nx.NetworkXNoPath:
        return []

def estimate_fare(n_stations):
    if n_stations <= 3:
        return 10
    elif n_stations <= 8:
        return 20
    elif n_stations <= 15:
        return 30
    else:
        return 40

def estimate_travel_time(n_stations):
    return n_stations * 2  # 2 minutes per station

def get_coordinates(df, route):
    return df[df['station'].isin(route)].drop_duplicates('station')

def generate_map_html(route_df):
    if route_df.empty:
        return "<p>No route found to render.</p>"

    center = [route_df['lat'].mean(), route_df['lon'].mean()]
    route_map = folium.Map(location=center, zoom_start=12)

    for _, row in route_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=6,
            color='blue',
            fill=True,
            fill_color='blue',
            popup=row['station']
        ).add_to(route_map)

    coords = list(zip(route_df['lat'], route_df['lon']))
    PolyLine(coords, color="red", weight=4.5, opacity=0.8).add_to(route_map)

    return route_map._repr_html_()

# --- Gradio Interface Function ---
def metro_route_planner(start, end):
    if start == end:
        return "<div style='color: orange; font-size: 16px;'>⚠️ Start and destination are the same.</div>", "<p>No map to display.</p>", ""

    route = get_route(G, start, end)
    if not route:
        return "<div style='color: red; font-size: 16px;'>❌ No route found between selected stations.</div>", "<p>No map to display.</p>", ""

    route_df = get_coordinates(df, route)
    station_list = "<br>".join([f"{i+1}. 🚉 {station}" for i, station in enumerate(route)])
    travel_time = estimate_travel_time(len(route))
    fare = estimate_fare(len(route))

    info = f"""
    <div style='font-family: Arial; font-size: 16px; line-height: 1.6;'>
        <h3 style='color: green;'>✅ Route from {start} to {end}</h3>
        <p><strong>🛤️ Stations:</strong><br>{station_list}</p>
        <p>📍 <strong>Total Stations:</strong> {len(route)}<br>
        ⏱ <strong>Estimated Time:</strong> {travel_time} mins<br>
        💰 <strong>Estimated Fare:</strong> ₹{fare}</p>
    </div>
    """

    map_html = generate_map_html(route_df)
    summary = f"{start} → {end} ({len(route)} stations)"
    return info, map_html, summary

# --- Load Data ---
df, G = load_data()
stations = sorted(G.nodes)

# --- Gradio UI ---
with gr.Blocks() as demo:
    # Add some custom CSS
    gr.Markdown("""
    <style>
        .gradio-container {
            font-family: 'Segoe UI', sans-serif;
        }
        h1 {
            color: #2E8B57;
            font-size: 32px;
            margin-bottom: 0.5em;
        }
        .subtitle {
            font-size: 18px;
            color: #555;
            margin-bottom: 1em;
        }
    </style>
    """)

    gr.Markdown("<h1>🚇 Hyderabad Metro Route Planner</h1>")
    gr.Markdown("<div class='subtitle'>Plan your journey with shortest route, fare, and time estimates. 🧳</div>")

    with gr.Row():
        start = gr.Dropdown(stations, label="🟢 Start Station")
        end = gr.Dropdown(stations, label="🔴 Destination Station")
    
    route_btn = gr.Button("🚀 Find Route")

    output_text = gr.HTML()
    output_map = gr.HTML()
    output_info = gr.Textbox(label="📋 Route Summary", interactive=False)

    route_btn.click(fn=metro_route_planner,
                    inputs=[start, end],
                    outputs=[output_text, output_map, output_info])

demo.launch()