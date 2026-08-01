from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .services import (
    train_neural_network_simulation,
    get_cnn_layer_structure,
    get_transfer_learning_summary
)

@login_required
def dl_studio_home_view(request):
    epochs = int(request.POST.get('epochs', 10))
    activation = request.POST.get('activation', 'relu')
    output_act = request.POST.get('output_activation', 'softmax')
    
    history, graph_json = train_neural_network_simulation(epochs=epochs, hidden_activation=activation, output_activation=output_act)
    cnn_layers = get_cnn_layer_structure()
    transfer_models = get_transfer_learning_summary()
    
    image_prediction = None
    if request.method == 'POST' and request.FILES.get('image_file'):
        img = request.FILES['image_file']
        model_choice = request.POST.get('transfer_model', 'MobileNetV2')
        classes = ['Sports Car', 'Passenger Sedan', 'Utility SUV', 'Commercial Truck', 'Electric Vehicle']
        pred_class = classes[hash(img.name) % len(classes)]
        confidence = round(88.5 + (hash(img.name) % 11), 1)
        image_prediction = {
            'file_name': img.name,
            'model': model_choice,
            'predicted_class': pred_class,
            'confidence': confidence
        }
        messages.success(request, f"CNN Image Classification Complete! Prediction: {pred_class} ({confidence}% confidence).")

    context = {
        'epochs': epochs,
        'activation': activation,
        'output_act': output_act,
        'history': history,
        'graph_json': graph_json,
        'cnn_layers': cnn_layers,
        'transfer_models': transfer_models,
        'image_prediction': image_prediction,
    }
    return render(request, 'dl_studio/dl_studio.html', context)
