"""
BYU-Idaho Positron Annihilation Spectroscopy Team

Pictoral Extrapolator for Pappy Tabulated Observations - PepTo
"""
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Function to get the file names and directories for each
def GetDirectories():
    """Gets a full working list of directories for pappy.csv files beginning at the directory from which the program is located

    Returns:
        list: returns a complete list of the files in the directory within or below the installed location of the program
    """
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
class DataSet(object):
    def __init__(self, materials):
        if type(materials) != list:
            message = f"GenerateDataSet function called with incorrect parameter input\n\nExpected type 'list' but got type {type(materials)} instead"
            raise TypeError(message)
        
        # Make a dictionary for easy mapping of element names to an index for rows, columns, and depth
        self.row_indeces = {'annealed': 0, 'unannealed': 1}
        self.col_indeces = {material: materials.index(material) for material in materials}
        self.depth_indeces = {
            'S Parameter': 0,
            'S Uncertainty': 1,
            'Left W Parameter': 2,
            'Left W Uncertainty': 3,
            'Right W Parameter': 4,
            'Right W Uncertainty': 5,
            'N Samples': 6
        }
        
        # Set dimension constraints from input
        self.rows = len(self.row_indeces) # Anneal types
        self.cols = len(materials) # Possible material options
        self.depth = len(self.depth_indeces) # Number of values stored to dimension 3 of the tensor
        
        # Generate the empty dataset
        self.dataset = self.EmptyDataSet()
        
        return None
    
    def size(self):
        return f"[{self.rows} rows, {self.cols} cols, {self.depth} in depth]"
    
    def EmptyDataSet(self):
        """Builds an empty 3 dimensional tensor for the sample data

        Returns:
            tensor: empty data tensor
        """
        return [[[[] if _ < self.depth - 1 else 0 for _ in range(self.depth)] for j in range(self.cols)] for k in range(self.rows)]
    
    def FillDataSet(self, file_names):
        """Fills the self.dataset with data from the list of files inputted

        Args:
            file_names (list): list of file names, and files inside of folders with appended reference (on each inside of a folder)

        Returns:
            None: Returns None, but updates the self.dataset element
        """
        # Get the path directory for reference
        path = os.getcwd()
        
        # Take apart the file names and extrapolate row and column information
        file_name_information = [file_name.split('_') for file_name in file_names]
        
        # Extrapolate the row and column data
        rows = [self.row_indeces[row_[1]] for row_ in file_name_information]
        
        # If the material was not stated to be analyzed, we skip it with a None filler to the blank to maintain list length
        cols = [self.col_indeces[col_[0]] if col_[0] in self.col_indeces else None for col_ in file_name_information]
        
        # Add the data to the dataset through iteration
        for (row, col, file_name) in zip(rows, cols, file_names):
            # Check to make sure the column name being iterated is desired by the user, AKA not None
            if col == None:
                # If it is None, skip the loop
                continue
            
            # Open the file to read the information before passing to csv.reader()
            file = open((path + '/' + file_name), 'r')
            
            # Save the data from the csv file to a list while removing the first column (file name)
            csv_data = [float(data) for data in list(csv.reader(file))[1][1:]]
            
            # Add data to the dataset
            for _, depth in self.depth_indeces.items():
                # If the index is at the counting index (6), be sure not to use the csv data
                if depth == 6:
                    # Add to the n-samples deep layer
                    self.dataset[row][col][depth] += 1
                else:
                    # Add the parameter to the specified location in the tensor
                    self.dataset[row][col][depth].append(csv_data[depth])
        
        return None
    
    def DisplayData(self, depth_index):
        """Generates a console output to show the averaged S parameters and propogated uncertainties

        Args:
            depth_index (string): A string name for which parameter to examine (ie. 'S Parameter', 'L Wing Parameter', 'R Wing Parameter')

        Raises:
            IndexError: If the name is not found in the data report, it will raise an error of the index

        Returns:
            None: Outputs a display, returns None
        """
        # Check whether the depth_index name was a string reference to the material or an integer index
        if type(depth_index) == str:
            # Construct the error message in case the named element was not listed in analysis
            message = f"\nKey ({depth_index}) was not found in the dictionary\nEnter one of the options from the analysis: {list(self.depth_indeces.keys())}"
            
            # Raise the error if the key is not present
            if depth_index not in self.depth_indeces:
                raise IndexError(message)
            else:
                depth_index = self.depth_indeces[depth_index]
        
        # Make the sample material names
        script = f"\n{'':<12}"
        
        # Pass through each material listed in the analysis
        for element in self.col_indeces:
            # Append the next element centered about 12 spaces of width
            script += f"{element.title():^12}"
        
        # Print the names out to the console
        print(script)
        
        # Pass through the anneal types and row indeces - zip() allows for simultaneous multiple-item iterating
        for name, row in zip(self.row_indeces.keys(), range(self.rows)):
            # Add the anneal type to the row
            script = f"\n{name.title():^12}"
            for col in range(self.cols):
                # If the dataset is empty, then don't average. Otherwise, present the mean for visualization
                if np.sum(self.dataset[row][col][depth_index]) > 0:
                    mean = np.mean(self.dataset[row][col][depth_index])
                    script += f"{mean:^12.6f}"
                else:
                    mean = '(NO DATA)'
                    script += f"{mean:^12}"
            
            print(script)
        
        return None
    
    def SvW(self, trendline = False):
        """Scatter plot of S vs W parameters

        Args:
            trendline [bool]: Default 'False', if 'True' displays a trendline for each plot
        """
        fig, ax = plt.subplots(2, 3)
        fig.subplots_adjust(bottom = 0.18, top = 0.9, wspace = 0.5, hspace = 0.8)
        #fig.tight_layout()
        fig.set_facecolor('lightgray')
        
        # Lists to store the parameter and uncertainty data
        labels = []
        s_parameters = []
        s_uncertainty = []
        l_parameters = []
        l_uncertainty = []
        r_parameters = []
        r_uncertainty = []
        
        # List of plot colors
        colors = ['salmon', 'cadetblue', 'magenta', 'cyan', 'olivedrab', 'goldenrod']
        
        # Iterate through the columns which are the material names
        for material, col in self.col_indeces.items():
            # Iterate through the rows of the data which are the two anneal types
            for annealing_type, row in self.row_indeces.items():
                # Append to all of the lists to store them conveniently for plotting and analysis
                s_parameters.append(self.dataset[row][col][0])
                s_uncertainty.append(self.dataset[row][col][1])
                l_parameters.append(self.dataset[row][col][2])
                l_uncertainty.append(self.dataset[row][col][3])
                r_parameters.append(self.dataset[row][col][4])
                r_uncertainty.append(self.dataset[row][col][5])
                labels.append(material.title() + ' ' + annealing_type)

        # Add a trendline if necessary
        if trendline == True:
            for index, S, s_uncert, L, l_uncert, R, r_uncert in zip(range(self.cols), s_parameters, s_uncertainty, l_parameters, l_uncertainty, r_parameters, r_uncertainty):
                # Generate a list of the summed errors by propogation of the wing uncertainties
                W = [np.sqrt(l * l + r * r) for l, r in zip(L, R)]
                W_error = [np.sqrt(l_ * l_ + r_ * r_) for l_, r_ in zip(l_uncert, r_uncert)]
                # Get the line fit coefficients
                b, a = np.polyfit(W, S, deg=1)
                # Get the r_squared metric by using numpy correlation method and squaring it whilst maintaining the sign +/-
                r_squared = np.corrcoef(W, S)[0, 1] * np.corrcoef(W, S)[0, 1]
                # Generate a sequence of x points to plot
                xseq = np.linspace(0.99 * min(W), 1.01 * max(W), int((max(W) - min(W)) * 1000))
                # Set the x  and y labels, x label includes the print out of the line fit equation with the r^2 metric
                ax[0 if index < 3 else 1][index % 3].set_xlabel(f"W Parameter \n\nLine fit: S(W) = {b:.6f} * W + ({a:.6f}) \nr^2 value: {r_squared:.4f}", weight = 'bold', fontsize = 10.0)
                ax[0 if index < 3 else 1][index % 3].set_ylabel("S Parameter", weight = 'bold', fontsize = 10.0)
                # Establish the error bars
                ax[0 if index < 3 else 1][index % 3].errorbar(W, S, yerr = s_uncert, xerr = W_error, ls = 'None')
                # Plot the scatter points of the parameters
                ax[0 if index < 3 else 1][index % 3].scatter(W, S, color = colors[index], s = 1)
                # Add the title
                ax[0 if index < 3 else 1][index % 3].set_title(f"S vs. W -> {list(self.col_indeces)[index].title()}")
                # Plot the line fit equation using the x sequence data we created previously
                ax[0 if index < 3 else 1][index % 3].plot(xseq, a + b * xseq, color = 'k', lw = 2.5)
        
        return fig, ax
    
    def BoxPlots(self):
        theta = 45
        font_size = 6
        
        fig, ax = plt.subplots(3, 2)
        fig.subplots_adjust(bottom = 0.15, top = 0.95, wspace = 0.5, hspace = 1.0)
        fig.tight_layout()
        fig.set_facecolor('lightgray')
        
        labels = []
        s_parameters = []
        s_uncertainties = []
        l_parameters = []
        l_uncertainties = []
        r_parameters = []
        r_uncertainties = []
        
        for material, col in self.col_indeces.items():
            for annealing_type, row in self.row_indeces.items():
                s_parameters.append(self.dataset[row][col][0])
                s_uncertainties.append(self.dataset[row][col][1])
                l_parameters.append(self.dataset[row][col][2])
                l_uncertainties.append(self.dataset[row][col][3])
                r_parameters.append(self.dataset[row][col][4])
                r_uncertainties.append(self.dataset[row][col][5])
                labels.append(material.title() + f'\n' + annealing_type)
        
        ax[0][0].set_title('S Parameters')
        ax[0][0].boxplot(s_parameters, widths = 0.9, patch_artist = True)
        ax[0][0].tick_params(labelsize = font_size)
        ax[0][0].set_xticklabels(labels, rotation = theta)
        ax[0][1].set_title('S Uncertainties')
        ax[0][1].boxplot(s_uncertainties, widths = 0.9, patch_artist = True)
        ax[0][1].tick_params(labelsize = font_size)
        ax[0][1].set_xticklabels(labels, rotation = theta)
        
        ax[1][0].set_title('Left Wing Parameters')
        ax[1][0].boxplot(l_parameters, widths = 0.9, patch_artist = True)
        ax[1][0].tick_params(labelsize = font_size)
        ax[1][0].set_xticklabels(labels, rotation = theta)
        ax[1][1].set_title('Left Wing Uncertainties')
        ax[1][1].boxplot(l_uncertainties, widths = 0.9, patch_artist = True)
        ax[1][1].tick_params(labelsize = font_size)
        ax[1][1].set_xticklabels(labels, rotation = theta)
        
        ax[2][0].set_title('Right Wing Parameters')
        ax[2][0].boxplot(r_parameters, widths = 0.9, patch_artist = True)
        ax[2][0].tick_params(labelsize = font_size)
        ax[2][0].set_xticklabels(labels, rotation = theta)
        ax[2][1].set_title('Right Wing Uncertainties')
        ax[2][1].boxplot(r_uncertainties, widths = 0.9, patch_artist = True)
        ax[2][1].tick_params(labelsize = font_size)
        ax[2][1].set_xticklabels(labels, rotation = theta)
        
        return fig, ax
    
    def GetClasses(self):
        return [column for column in self.col_indeces]
    
    def ToCSV(self, date):
        path = os.getcwd()
        file_name = f"{path}/{date}_all_samples_pepto.csv"
        file = open(file_name, 'w')
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Material", "Anneal Type"] + list([item for item in self.depth_indeces.keys()]))
        for material, col in self.col_indeces.items():
            for anneal_type, row in self.row_indeces.items():
                csv_writer.writerow([material, anneal_type] + self.dataset[row][col])
        
        print(f"\t\nSuccessfully saved to '{file_name}'!\n")

def main():
    materials = ['nickel', 'aluminum', 'tungsten', 'gold', 'copper', 'lead']

    # Instantiate the dataset object and submit the materials you'd like to summarize
    dset = DataSet(materials)

    # Fill up the dataset object with the file output
    dset.FillDataSet(GetDirectories())

    # Display the output from the dataset using its built-in method
    dset.DisplayData('S Parameter')
    
    # Save the sample data to new pepto.csv file - Obviously, set the current date
    dset.ToCSV('06_15_2023')

    # Make the plots
    #dset.BoxPlots()
    dset.SvW(True)
    plt.show()
    
    # Stay open until the console needs to be closed
    """ Uncomment these lines for the computer on campus
    while True:
        input_ = input("Press 'Enter' to end session")
        if input_ == '':
            break
    """
    return None

if __name__ == '__main__()':
    main()
else:
    pass