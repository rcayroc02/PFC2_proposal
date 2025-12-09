import os

root = r"C:\Users\ROG\Documents\GitHub\WACV23-workshop-TMGF\datasets\MSMT17"
test_line = open(os.path.join(root, "list_train.txt")).readline().strip()
print("Primera línea del txt:", test_line)
print("Ruta combinada:", os.path.join(root, "train", test_line))
print("Existe?:", os.path.exists(os.path.join(root, "train", test_line)))
