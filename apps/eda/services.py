import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import networkx as nx

from apps.datasets.utils import load_dataframe

def get_eda_summary_statistics(df):
    """Calculates dataset summary, missing value stats, correlation & distributions."""
    num_df = df.select_dtypes(include=[np.number])
    cat_df = df.select_dtypes(include=['object', 'category'])
    
    corr_json = {}
    strong_correlations = []
    
    if not num_df.empty:
        corr = num_df.corr().round(2)
        corr_json = corr.to_dict()
        
        # Find strong correlations (|r| >= 0.4)
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                col1 = corr.columns[i]
                col2 = corr.columns[j]
                val = corr.iloc[i, j]
                if not np.isnan(val) and abs(val) >= 0.4:
                    rel_type = "positive" if val > 0 else "negative"
                    strength = "strong" if abs(val) >= 0.7 else "moderate"
                    explanation = f"'{col1}' and '{col2}' have a {strength} {rel_type} correlation ({val:.2f})."
                    strong_correlations.append({
                        'col1': col1,
                        'col2': col2,
                        'value': val,
                        'explanation': explanation
                    })
                    
    return {
        'num_cols': num_df.columns.tolist(),
        'cat_cols': cat_df.columns.tolist(),
        'corr': corr_json,
        'strong_correlations': strong_correlations,
    }


def compute_two_way_crosstab(df, col1, col2):
    """Calculates two-way cross tabulation (Unit 1.5 syllabus)."""
    if col1 in df.columns and col2 in df.columns:
        ct = pd.crosstab(df[col1], df[col2], margins=True)
        return ct.to_html(classes='table table-dark table-striped table-bordered text-center align-middle', border=0)
    return ""


def generate_networkx_visualization(df):
    """
    Builds network graph using NetworkX and calculates node degrees (Unit 2.4 syllabus).
    Uses circular layout for clean spacing between nodes.
    """
    num_df = df.select_dtypes(include=[np.number])
    G = nx.Graph()
    
    if num_df.shape[1] >= 2:
        corr = num_df.corr().abs()
        cols = num_df.columns.tolist()
        
        for c in cols:
            G.add_node(c)
            
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                col1, col2 = cols[i], cols[j]
                val = corr.loc[col1, col2]
                if not np.isnan(val) and val >= 0.25:
                    G.add_edge(col1, col2, weight=round(val, 2))
    else:
        G.add_edge("Node_A", "Node_B", weight=0.8)
        G.add_edge("Node_B", "Node_C", weight=0.6)
        
    node_degrees = {node: degree for node, degree in G.degree()}
    
    # Use circular / kamada_kawai layout for perfectly spaced non-overlapping nodes
    try:
        pos = nx.kamada_kawai_layout(G)
    except Exception:
        pos = nx.circular_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#38bdf8'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    display_labels = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        deg = node_degrees[node]
        node_text.append(f"Feature: {node}<br>Degree: {deg}")
        node_size.append(26 + deg * 6)
        # Truncate long node labels for clean layout display
        disp_name = (str(node)[:15] + '..') if len(str(node)) > 15 else str(node)
        display_labels.append(disp_name)
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=display_labels,
        textposition="top center",
        textfont=dict(color="#ffffff", size=12, family="Inter, sans-serif"),
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=node_size,
            color=[node_degrees[n] for n in G.nodes()],
            line_width=2,
            line=dict(color='#ffffff'),
            colorbar=dict(
                tickfont=dict(color="#ffffff"),
                title=dict(text="Degree", font=dict(color="#ffffff"))
            )
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<b style="color:#ffffff">NetworkX Feature Correlation Graph</b>',
                title_font_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=40, l=40, r=40, t=50),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            ))
            
    return _serialize_plotly_fig(fig), node_degrees


def create_plotly_chart(df, chart_type, x_col, y_col=None, color_col=None):
    """Generates interactive Plotly JSON for any requested chart type."""
    fig = None
    
    if chart_type == 'histogram':
        fig = px.histogram(df, x=x_col, color=color_col, marginal="box", template="plotly_dark", title=f"Histogram of {x_col}")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, template="plotly_dark", title=f"{y_col} vs {x_col}")
    elif chart_type == 'boxplot':
        fig = px.box(df, x=x_col, y=y_col, color=color_col, points="all", template="plotly_dark", title=f"Box Plot of {y_col or x_col}")
    elif chart_type == 'violin':
        fig = px.violin(df, x=x_col, y=y_col, color=color_col, box=True, points="all", template="plotly_dark", title=f"Violin Plot of {y_col or x_col}")
    elif chart_type == 'bar':
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, template="plotly_dark", title=f"Bar Chart of {x_col}")
    elif chart_type == 'line':
        fig = px.line(df, x=x_col, y=y_col, color=color_col, template="plotly_dark", title=f"Line Chart of {y_col} over {x_col}")
    elif chart_type == 'pie':
        fig = px.pie(df, names=x_col, values=y_col, template="plotly_dark", title=f"Distribution of {x_col}")
    elif chart_type == 'heatmap':
        num_df = df.select_dtypes(include=[np.number])
        if num_df.empty or num_df.shape[1] < 1:
            num_df = df.apply(pd.to_numeric, errors='coerce').dropna(how='all', axis=1)
            
        short_labels = [(c[:12] + '..') if len(c) > 12 else c for c in num_df.columns]
        corr = num_df.corr().round(2)
        fig = px.imshow(
            corr,
            x=short_labels,
            y=short_labels,
            text_auto=True,
            color_continuous_scale="Viridis",
            template="plotly_dark",
            title="Correlation Heatmap",
            aspect="auto"
        )
    elif chart_type == 'bubble':
        fig = px.scatter(df, x=x_col, y=y_col, size=df.select_dtypes(include=[np.number]).columns[0] if y_col else None, color=color_col, template="plotly_dark", title="Bubble Chart")
    elif chart_type == 'treemap':
        fig = px.treemap(df, path=[x_col, color_col] if color_col else [x_col], values=y_col, template="plotly_dark", title="Treemap Chart")
    elif chart_type == 'sunburst':
        fig = px.sunburst(df, path=[x_col, color_col] if color_col else [x_col], values=y_col, template="plotly_dark", title="Sunburst Chart")
    elif chart_type == 'parallel':
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:5]
        fig = px.parallel_coordinates(df, dimensions=num_cols, template="plotly_dark", title="Parallel Coordinates Plot")
    elif chart_type == 'scatter_matrix':
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:4]
        fig = px.scatter_matrix(df, dimensions=num_cols, color=color_col, template="plotly_dark", title="Scatter Matrix Plot")
    else:
        fig = px.histogram(df, x=x_col, template="plotly_dark", title=f"Distribution of {x_col}")
        
    fig.update_layout(
        paper_bgcolor='rgba(15,23,42,0.8)',
        plot_bgcolor='rgba(15,23,42,0.8)',
        font=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
        title_font_color="#ffffff",
        margin=dict(l=80, r=40, t=50, b=80),
    )
    
    return _serialize_plotly_fig(fig)


import base64

def _serialize_plotly_fig(fig):
    """Safely converts a Plotly figure to JSON string, decoding base64 bdata arrays into plain lists."""
    if fig is None:
        return "{}"
    fig_dict = fig.to_dict()
    
    def sanitize(obj):
        if isinstance(obj, dict):
            if 'bdata' in obj and 'dtype' in obj:
                try:
                    arr = np.frombuffer(base64.b64decode(obj['bdata']), dtype=obj['dtype'])
                    return [None if (np.isnan(x) or np.isinf(x)) else float(x) for x in arr]
                except Exception:
                    pass
            return {k: sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return None if (np.isnan(obj) or np.isinf(obj)) else float(obj)
        elif isinstance(obj, np.ndarray):
            return [None if (np.isnan(x) or np.isinf(x)) else float(x) for x in obj.tolist()]
        return obj

    clean_dict = sanitize(fig_dict)
    return json.dumps(clean_dict)
