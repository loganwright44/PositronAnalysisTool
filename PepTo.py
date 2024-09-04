"""
BYU-Idaho Positron Annihilation Spectroscopy Team

Pictoral Extrapolator for Pappy Tabulated Observations - PepTo
"""
import matplotlib.pyplot as plt
import csv
import copy
import os

# Function to get the file names and directories for each
def GetDirectories():
    # Get current directory path
    path = os.getcwd()
    
    # Get the files and folders list within this directory
    files = [file for file in os.listdir(path) if file.split('_')[-1] == 'pappy.csv']
    folders = [folder for folder in os.listdir(path) if len(folder.split('.')) == 1]
    
    for folder in folders:
        path = os.getcwd() + '/' + folder
        for file in os.listdir(path):
            if file.split('_')[-1] == 'pappy.csv':
                files.append(folder + '/' + file)
            elif len(file.split('.')) == 1:
                folders.append(folder + '/' + file)
            else:
                pass
    
    return files

# Function to generate the dataset of the samples
def SampleDataSet(materials):
    annealing_data = {
        'annealed': [0, 0., 0.],
        'unannealed': [0, 0., 0.]
    }
    
    Data = {}
    
    for material in materials:
        Data[material] = copy.deepcopy(annealing_data)
    
    return Data

# Function to build the dataset as a Pandas dataframe
def DisplayDataSimple(file_data, files, print_ = True):
    """Basic display of the dataset as a dictionary to the console

    Args:
        file_data (list): raw data from the files
        files (list): list of the file names in the directory to open
        print_ (bool): Set to false if no need to display findings, default set to true

    Returns:
        dictionary: dataset used for the display function below
    """
    data = pd.DataFrame()
    
    # Columns order
    column_order = [
        'Sample Name',
        'Anneal Type',
        'S Parameter',
        'S Uncertainty',
        'Left W Parameter',
        'Left W Uncertainty',
        'Right W Parameter',
        'Right W Uncertainty'
    ]
    
    # We need the path again to build the complete file directory for hidden files in folders
    path = os.getcwd()
    
    # Also, we need to define a few named indeces
    material = 0
    anneal_type = 1
    trial_number = -2
    
    print(f'\nFile information:\n')
    if len(files) > 0:
        for file in files:
            # Read the csv file and put into a pandas dataframe
            # The columns are filename, s-parameter, s-param uncertainty, and the rest don't matter to us yet
            csv_data = pd.read_csv(path + '/' + file)
            file = (file.split('/')[-1]).split('_')
            
            if print_ == True:
                print(f"Material: {file[material].title()} \
                    | Anneal Type: {file[anneal_type].title()} \
                    | Trial {int(file[trial_number])}")

            # Add 1 to the number of samples row in the list
            file_data[file[material]][file[anneal_type]][0] += 1
            # Then add the s-parameter from the csv to the second row of the list
            file_data[file[material]][file[anneal_type]][1] += csv_data['S Parameter'].iloc[0]
            # Finally, add the s-param uncertainty to the 3rd row in the list
            file_data[file[material]][file[anneal_type]][2] += csv_data['S Uncertainty'].iloc[0]
            csv_data["Anneal Type"] = file[anneal_type]
            csv_data["Sample Name"] = file[material]
            
            try:
                csv_data = csv_data.drop(columns = ["Unnamed: 7"])
            except KeyError:
                pass
            
            data = pd.concat((data, csv_data))

        data = data.reindex(columns = column_order).reset_index(drop = True)
        return data.sort_values(by = 'Sample Name')
    
    else:
        print("No PapPy files found!")
        return None

# Create a function that computes and plots the data from a sample in the dictionary format
# created below
def DisplayDataComplex(dataset):
    """Cleanly prints out the data from pappy files

    Args:
        dataset (dictionary): expects a dictionary of a depth and format such that
            dataset = {'material': {'anneal_type': [0, 0.0, 0.0]}} where each value in the columns of the list,
            by the end of this operation, will be filled with num_samples, sum of s-parameters, and the sum of
            the s-parameter uncertainties
    """
    
    # Start by printing a line of titles
    print("\nMaterial   |   Annealed   |  Sample Size | S-Param   |   Uncertainty | Unannealed  | Sample Size | S-Param   |   Uncertainty\n")
    # Print the data out to the console in a nice format
    for material in dataset:
        # Initialize a string variable to store the output to print at each loop
        output = f"{material.title():<12}"
        # Go through the anneal types
        for anneal in dataset[material]:
            output += f"\t {anneal.title():<12}"
            # Compute and store the mean s-params and uncertainty
            mean_s_param = dataset[material][anneal][1] / dataset[material][anneal][0] if dataset[material][anneal][0] > 0 else 0
            mean_uncertainty = dataset[material][anneal][2] / dataset[material][anneal][0] if dataset[material][anneal][0] > 0 else 0
            dataset[material][anneal].append(mean_s_param)
            dataset[material][anneal].append(mean_uncertainty)
            # Go through the list containing num samples, sum of S params, and s-param uncertainty
            for index in range(len(dataset[material][anneal]) - 2):
                if index == 0:
                    output += f"\t {str(round(dataset[material][anneal][index], 8)):<12}"
                if index == 1:
                    output += f"\t {str(round(dataset[material][anneal][index + 2], 8)):<12}"
                elif index == 2:
                    output += f"\t {str(round(dataset[material][anneal][index + 2], 8)):<12}"
        
        print(output)
    
    return None

def PlotBox(dataset, show = False):
    """Generates a box plot of a pandas dataframe

    Args:
        dataset (pandas dataframe): dataset given from the .csv pappy files

    Returns:
        None
    """
    if show:
        boxplot = dataset.boxplot(column = ["S Parameter", "S Uncertainty"], by = ["Sample Name", "Anneal Type"], grid = False, rot = 45)
        plt.show()
    
    return None

def DataToCSV(date, data):
    path = os.getcwd()
    data.to_csv(f"{path}/{date}_all_samples_pepto.csv", index = False)
    print(f"\nSuccessfully saved to '{path}/{date}_all_samples_pepto.csv'!")
    return None

def main():
    """Runs all previous functions
    """
    # Get the file and folder names
    files = GetDirectories()
    
    # Sample names to generate the dictionary
    sampled_elements = [
        'aluminum',
        'copper',
        'gold',
        'nickel',
        'tungsten'
    ]
    
    # Empty dataframe to contain all of the data from everywhere below this directory
    # from a pappy file
    file_data = SampleDataSet(sampled_elements)
    
    # Generate another dataset as a pandas dataframe for plotting
    data = DisplayDataSimple(file_data, files, False)
    
    # Show the data to the console
    DisplayDataComplex(file_data)
    
    # If you need a csv file of the complete dataset, uncomment the following 2 lines and type the date
    # in the form of '01_31_2043' or 'month_day_year'
    DataToCSV('06_13_2023', data)

    # Plot the data on boxplot
    PlotBox(data, True)

main()