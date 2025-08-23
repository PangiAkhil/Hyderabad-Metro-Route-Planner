import networkx as nx
import pandas as pd

def load_metro_graph(file_path="hyderabad_metro_stations.csv"):
    """
    🚇 Load Hyderabad Metro data and build a graph of stations.
    """
    df = pd.read_csv(file_path)
    G = nx.Graph()

    # 🎯 Add stations as nodes with line information
    for station, line in zip(df['station'], df['line']):
        G.add_node(station, line=line)

    # 🧵 Connect stations for each line
    red_line = df[df['line'] == 'Red']['station'].tolist()
    blue_line = df[df['line'] == 'Blue']['station'].tolist()
    green_line = df[df['line'] == 'Green']['station'].tolist()

    def connect_stations(station_list):
        for i in range(len(station_list) - 1):
            G.add_edge(station_list[i], station_list[i+1])

    connect_stations(red_line)
    connect_stations(blue_line)
    connect_stations(green_line)

    print("✅ Metro graph loaded with", len(G.nodes), "stations and", len(G.edges), "connections.")
    return G

def get_route(graph, start, end, as_html=False):
    """
    🧭 Find the shortest path between two stations.
    Returns a list or an HTML-formatted string.
    """
    try:
        route = nx.shortest_path(graph, source=start, target=end)
        if as_html:
            # 🖼️ Return HTML-formatted string with emojis
            station_list = "<br>".join([f"{i+1}. 🚉 {station}" for i, station in enumerate(route)])
            return f"""
            <div style='font-family: Arial; font-size: 16px;'>
                <h3>🧭 Route from <span style='color: green;'>{start}</span> to <span style='color: red;'>{end}</span></h3>
                {station_list}
                <p>📍 <strong>Total Stations:</strong> {len(route)}</p>
                <p>⏱ <strong>Estimated Time:</strong> {len(route) * 2} mins</p>
                <p>💰 <strong>Estimated Fare:</strong> ₹{estimate_fare(len(route))}</p>
            </div>
            """
        else:
            return route
    except nx.NetworkXNoPath:
        return "<div style='color: red;'>❌ No path found between the selected stations.</div>" if as_html else []

def estimate_fare(n_stations):
    """
    💰 Fare estimation based on number of stations.
    """
    if n_stations <= 3:
        return 10
    elif n_stations <= 8:
        return 20
    elif n_stations <= 15:
        return 30
    else:
        return 40