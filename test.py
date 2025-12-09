import torch
print("PyTorch:", torch.__version__)
print("CUDA en PyTorch:", torch.version.cuda)
print("CUDA disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


python -c "import torch, faiss; print(f'PyTorch: {torch.__version__}'); print(f'PyTorch CUDA: {torch.version.cuda}'); print(f'CUDA disponible: {torch.cuda.is_available()}')"
