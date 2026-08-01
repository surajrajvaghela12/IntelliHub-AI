import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

def train_neural_network_simulation(epochs=10, hidden_activation='relu', output_activation='softmax'):
    """
    Simulates / Trains Keras Dense Neural Network (Unit 6.1 syllabus).
    Activations: ReLU, Sigmoid, Softmax.
    Generates training loss and accuracy per epoch curves.
    """
    np.random.seed(42)
    history = {'loss': [], 'val_loss': [], 'accuracy': [], 'val_accuracy': []}
    
    base_loss = 0.85
    base_acc = 0.55
    
    for epoch in range(1, epochs + 1):
        loss = max(0.05, base_loss * (0.8 ** epoch) + np.random.normal(0, 0.02))
        val_loss = max(0.08, loss + 0.04 + np.random.normal(0, 0.015))
        acc = min(0.99, base_acc + (1 - base_acc) * (1 - 0.7 ** epoch) + np.random.normal(0, 0.01))
        val_acc = min(0.96, acc - 0.03 + np.random.normal(0, 0.01))
        
        history['loss'].append(round(float(loss), 4))
        history['val_loss'].append(round(float(val_loss), 4))
        history['accuracy'].append(round(float(acc), 4))
        history['val_accuracy'].append(round(float(val_acc), 4))
        
    epochs_range = list(range(1, epochs + 1))
    
    # Plotly training graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=epochs_range, y=history['accuracy'], mode='lines+markers', name='Train Accuracy', line=dict(color='#38bdf8', width=2)))
    fig.add_trace(go.Scatter(x=epochs_range, y=history['val_accuracy'], mode='lines+markers', name='Val Accuracy', line=dict(color='#4ade80', width=2)))
    fig.add_trace(go.Scatter(x=epochs_range, y=history['loss'], mode='lines+markers', name='Train Loss', line=dict(color='#f43f5e', width=2)))
    fig.add_trace(go.Scatter(x=epochs_range, y=history['val_loss'], mode='lines+markers', name='Val Loss', line=dict(color='#fbbf24', width=2)))
    
    fig.update_layout(
        title=f"Keras Training Loss & Accuracy per Epoch (Activation: {hidden_activation.upper()})",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Epoch",
        yaxis_title="Score / Loss",
        font=dict(family="Inter, sans-serif", color="#f8fafc")
    )
    
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return history, graph_json


def get_cnn_layer_structure():
    """
    Returns CNN architecture visualization details (Unit 6.2 syllabus):
    Kernels, Convolution, Max Pooling, Dropout layers.
    """
    layers = [
        {'name': 'Input Image Layer', 'type': 'Input', 'shape': '(228, 228, 3)', 'params': 0, 'details': 'Raw RGB Image input'},
        {'name': 'Conv2D (32 Filters)', 'type': 'Convolution', 'shape': '(226, 226, 32)', 'params': 896, 'details': 'Kernel Size: 3x3, ReLU Activation'},
        {'name': 'MaxPooling2D', 'type': 'Pooling', 'shape': '(113, 113, 32)', 'params': 0, 'details': 'Pool Size: 2x2, Reduces Spatial Dimensions'},
        {'name': 'Conv2D (64 Filters)', 'type': 'Convolution', 'shape': '(111, 111, 64)', 'params': 18496, 'details': 'Kernel Size: 3x3, ReLU Activation'},
        {'name': 'MaxPooling2D', 'type': 'Pooling', 'shape': '(55, 55, 64)', 'params': 0, 'details': 'Pool Size: 2x2'},
        {'name': 'Dropout Layer (0.3)', 'type': 'Dropout', 'shape': '(55, 55, 64)', 'params': 0, 'details': 'Prevents Overfitting by dropping 30% units'},
        {'name': 'Flatten Layer', 'type': 'Reshape', 'shape': '(193600,)', 'params': 0, 'details': 'Converts 2D maps into 1D feature vector'},
        {'name': 'Dense Layer (128 units)', 'type': 'Dense', 'shape': '(128,)', 'params': 24780928, 'details': 'Fully Connected, ReLU Activation'},
        {'name': 'Output Dense Layer', 'type': 'Dense Output', 'shape': '(10,)', 'params': 1290, 'details': 'Softmax Activation for Classification'},
    ]
    return layers


def get_transfer_learning_summary():
    """
    Returns Transfer Learning pre-trained models summary (Unit 6.3 syllabus):
    ResNet50, MobileNetV2, EfficientNetB0.
    """
    return [
        {'name': 'ResNet50', 'params': '25.6M', 'depth': 50, 'accuracy': '92.5%', 'ideal_for': 'Deep Image Feature Extraction'},
        {'name': 'MobileNetV2', 'params': '3.4M', 'depth': 53, 'accuracy': '90.1%', 'ideal_for': 'Lightweight Mobile & Web AI'},
        {'name': 'EfficientNetB0', 'params': '5.3M', 'depth': 237, 'accuracy': '93.8%', 'ideal_for': 'High Accuracy Image Recognition'},
    ]
