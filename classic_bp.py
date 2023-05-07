from pyscipopt import Model, quicksum
import numpy as np
import itertools
import pandas as pd
import os

#this function runs the optimization package and solves the classic bin packing problem!
def Classic_BP(bin_data):

    #this looks like a self name variable?
    BP_Classic = Model()

    #extract bin/item info from CSV, add variables as needed
    bin_volume = bin_data[bin_data.columns[0]].values.tolist()
    item_size = bin_data[bin_data.columns[1]].values.tolist()

    #create lists of bin and item names, number them [0,1,...]
    #clean this up, it looks like this info is embedded in the dataframe via pandas?
    bin_name = []
    item_name = []
    for i in range(len(bin_volume)):
        bin_name_i = i
        bin_name.append(bin_name_i)
    for j in range(len(item_size)):
        item_name_j = j
        item_name.append(item_name_j)

    #the functions below set the decision variables as noted:
    #x_b = 1 if bin b is packed with any item, 0 otherwise
    x = {b: BP_Classic.addVar(vtype="B") for b in bin_name}

    #y_{i,b} = 1 if item i is packed into bin b, 0 otherwised
    y = {i: BP_Classic.addVar(vtype="B") for i in itertools.product(bin_name,item_name)}

    #Set the objective function for the optimization model:
    #We seek to minimize the number of bins used
    BP_Classic.setObjective(quicksum(x[b]for b in bin_name), 'minimize')

    #the functions below set the constraints forv the optimzation problem:
    #Items may only be packed in one bin
    for i in item_name:
        BP_Classic.addCons(quicksum(y[i,b] for b in bin_name) == 1)

    #Total size of items must be less than or equal to bin capacity
    for b in bin_name:
        BP_Classic.addCons(quicksum(y[i,b]*item_size[i] for i in item_name) <=  x[b]*bin_volume[b])
        
    #The function below calcuates the optimal solution
    BP_Classic.optimize()

    #We need to modify the results to make sense of what the returned values:
    #I don't remember what is going on here
    bins_filled_array = np.where([int(round(BP_Classic.getVal(x[b]))) for b in bin_name])[0]
    bins_filled_list = [0]*len(bin_name)
    for i in range (len(bins_filled_array)):
        bins_filled_list[bins_filled_array[i]]=1
    #add results to the dataframe
    bin_data['bins filled'] = bins_filled_list
    
    
    #the values retunred here are the locations of 1's in the 2d array item_name x bin_name
    #in order to deteremine which bin they go into, we modulo these numbers with the total number of bins
    items_packed_raw_array = np.where([int(round(BP_Classic.getVal(y[i]))) for i in itertools.product(item_name,bin_name)])[0]
    #the fucntion above produces an array object
    #conversion between raw and scrubbed lists
    items_packed_scrubbed = []
    for item in range(len(item_name)):
        items_packed_scrubbed.append(items_packed_raw_array[item]%len(item_name))
    #add results to the dataframe
    bin_data['items packed in below bin']=items_packed_scrubbed
    
    return(bin_data)

#determine file input/output directories and names
data_location = r"/home/showaltz/models/data"
data_name = "classic.csv"
results_location = r"/home/showaltz/models/data"
results_name = "output.csv"

#create the dataframe object from the chosen CSV
bin_data = pd.read_csv(os.path.join(data_location,data_name))
result = Classic_BP(bin_data)

#write updated dataframe object to csv
bin_data.to_csv(os.path.join(results_location,results_name))


#output_path = 'output.csv'
#add.to_csv(output_path, mode='a', header=not os.path.exists(output_path))
