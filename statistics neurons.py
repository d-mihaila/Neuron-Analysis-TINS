import numpy as np
import matplotlib.pyplot as plt
import csv
import glob
import json
import os

def extract_info_from_json(json_file_path):
    # Extract information from a JSON file
    with open(json_file_path, 'r') as file:
        data = file.read()
        data = json.loads(data)
        extracted = data['dendrites']['struct']['adjList']
    
    path_parts = json_file_path.split("/")
    generation = path_parts[-2].replace("Generation_", " ")  # "Generation_38" to "Generation 38"
    neuron_id, accuracy = path_parts[-1].split("_")
    neuron_id = neuron_id.replace("NeuronID-", "")
    accuracy = accuracy.replace("Acc-", "")
    accuracy = accuracy.replace(".json", "")
    #neuron_id = path_parts[-2].replace("NeuronID-", "Neuron ")  # "NeuronID-4" to "Neuron 4"
    #accuracy = path_parts[-1].replace("Acc-", "").replace(".json", "")  # "Acc-0.705625.json" to "0.705625"
    return [generation, neuron_id, accuracy], extracted


def calculate_histogram(extracted):
    # Calculate histogram using numpy.histogram
    
    data = []
    for i in extracted: 
        elm = extracted[i]
        count = len(elm) - 1
        data.append(count)
        
    n_sum = np.sum(data)
    av_n = n_sum / len(data)
    # print(data, len(data), av_n)
    
    data = [float(i) for i in data]
    hist, edges = np.histogram(data, bins=np.arange(min(data), max(data) + 7, 1))
    x = edges[1:]  # Get the bin centers as x values
    y = hist  # Use the histogram values as y values
    # print(x, y)
    return x, y, av_n

def loglog(x, y):
    # filtering out the 0's in y
    mask = y != 0
    nr_in = len(y) - len(mask)
    x_filtered = x[mask]
    y_filtered = y[mask]

    # print(y_filtered, x_filtered)

    x_log = np.log(x_filtered)
    y_log = np.log(y_filtered)


    # Perform linear regression
    slope, intercept = np.polyfit(x_log, y_log, 1)

    # Calculate the predicted values
    y_pred = slope * x_log + intercept

    # Calculate the R-squared value
    residuals = y_log - y_pred
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y_log - np.mean(y_log)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Plot the data and the linear fit
    plt.figure()
    # TODO plt.title('')  put the generation, number, accuracy
    plt.plot(x_log, y_pred, '--', label = f'gradient is = {slope:.3f}')
    plt.scatter(x_log, y_log, c='red', label=f'R-squared = {r_squared:.2f}')
    plt.xlabel("log(node degree)")  
    plt.ylabel("log(count)")       
    plt.legend()
    plt.close()
    
    
    return slope, r_squared, nr_in

# TODO def path():
    # finding the shortest path length, average path length
    
# TODO def centralising():
    # finding the clustering coefficient

def main():
    folder_path = input("Enter the folder path containing JSON files: ")
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    
    if not json_files:
        print("No JSON files found in the specified folder.")
        return
    
    
    # Specify the CSV file name
    csv_file_name = "/Users/utilizator/Desktop/extracted_info.csv"
    
    with open(csv_file_name, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write the header row to the CSV file
        csv_writer.writerow(['Generation', 'Neuron ID', 'Accuracy', 'Complexity', 'Complexity Error', 'Average node degree', 'Number of inputs'])
        
        for json_file in json_files:
            extracted_info, data = extract_info_from_json(json_file)
            x, y, av_n = calculate_histogram(data)  # Calculate x and y using the calculate_histogram function
            r_squared, slope, nr_in = loglog(x, y)
            new_row = extracted_info + [slope, r_squared, av_n, nr_in]
            csv_writer.writerow(new_row)
    
    print(f"Extracted information saved to {csv_file_name}")

if __name__ == "__main__":
    main()