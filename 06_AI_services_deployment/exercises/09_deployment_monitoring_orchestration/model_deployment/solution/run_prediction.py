import numpy as np
import requests

x_test_path = 'X_test.csv'
y_test_path = 'y_test.csv'

X_test = np.loadtxt(x_test_path, delimiter=",")
y_test = np.loadtxt(y_test_path, delimiter=",")

for row in X_test:
    output = requests.get(f"http://localhost:8000/predict_single_row?alcohol={row[0]}&malic_acid={row[1]}&ash={row[2]}"
                          f"&alcalinity_of_ash={row[3]}&magnesium={row[4]}&total_phenols={row[5]}&flavanoids={row[6]}"
                          f"&nonflavanoid_phenols={row[7]}&proanthocyanins={row[8]}&color_intensity={row[9]}"
                          f"&hue={row[10]}&od280_od315_of_diluted_wines={row[11]}&proline={row[12]}")
    print(output.json())