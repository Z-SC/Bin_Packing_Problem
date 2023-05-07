from pyscipopt import Model, quicksum
import numpy as np
import itertools
import pandas as pd
import time


#The function below runs the optimization package and solves the Syndicate bin packing problem!
def Syndicate_BP(data, kappa):
    #Declare the name of the model, and suppress solver output to save screenspace.
    start_time = time.time()
    BP_Syndicate = Model()
    BP_Syndicate.hideOutput()
    
    #DATA SPECIFIC CODE, WATCH THE INDICES! 
    #data control is the key here, we're using verbose data, 
    #as reading verbose is likely faster than reading condensed
    #AND preforming to calculations to expand the data.
    
    #{
    #Extract bin/item info from DataFrame, exclude NAN values, casting as intger, reading into a list
    syndicate_names = data[data.columns[0]].dropna().astype('int').values.tolist()
    item_sizes = data[data.columns[1]].dropna().astype('int').values.tolist()
    bin_volumes = data[data.columns[2]].dropna().astype('int').values.tolist()
    bin_prices = data[data.columns[3]].dropna().astype('int').values.tolist()
    
    #Extract the binary paramter, A_{b,s}
    #"is bin b available from syndicate s?"
    #in the code we refer to it as a(vailability)_matrix
    #Create list of correct length
    #populate list with values from dataframe, dropping NAN, casting as int
    #select the correct values
    #width = #of syndicates
    #length = #of bins -done automatically by "data.columns[...]"
    a_matrix = [0]*len(syndicate_names)
    for s in range (len(syndicate_names)):
        a_matrix[s] = data[data.columns[4+s]].dropna().astype('int').values.tolist()
    #Convert bin\item name data to a list
    bin_names = list(range(len(bin_volumes)))
    item_names = list(range(len(item_sizes)))
    #}


    #The functions below set the decisionion variables as noted:
    #{
    #x_b = 1 if bin b is packed with any item, 0 otherwise
    x = {b: BP_Syndicate.addVar(vtype="B", name = "bin used?") for b in bin_names}
    
    #y_{i,b} = 1 if item i is packed into bin b, 0 otherwised
    y = {i: BP_Syndicate.addVar(vtype="B", name = "item i packed into bin b?") for i in itertools.product(item_names,bin_names)}
    #}


    #The below are constraints, and the call to optimize
    #{
    #two_sum = quicksum(quicksum(bin_prices[b]*a_matrix[s][b]*x[b] for b in bin_names) for s in syndicate_names)
    total_spend_on_bins = quicksum(bin_prices[b]*a_matrix[s][b]*x[b] for b in bin_names for s in syndicate_names)
    
    #Total size of items must be less than or equal to bin capacity
    for b in bin_names:
         BP_Syndicate.addCons(quicksum(y[i,b]*item_sizes[i] for i in item_names) <= x[b]*bin_volumes[b], name = "size restriction")
    
    #Items may only be packed in one bin
    for i in item_names:
        BP_Syndicate.addCons(quicksum(y[i,b] for b in bin_names) == 1, name = "all items must be packed")

    #Further restriction: need to ensure bins not filled are not used
    for b in bin_names:
        for i in item_names:
            BP_Syndicate.addCons(y[i,b] <= x[b])

    #Set the objective function for the optimization model, and solve:
    #we want to minimize total cost paid to syndiates (via bins)
    BP_Syndicate.setObjective(total_spend_on_bins, 'minimize')
    BP_Syndicate.optimize()
    #}
    
    
    #We need to modify the results to make sense of what the returned values:
    #{
    #First we determine which bins were filled, by looking at the variable x
    bins_filled_list = [0]*len(bin_names)
    bins_filled_raw_array = np.where([int(round(BP_Syndicate.getVal(x[b]))) for b in bin_names])[0]
    for b in range(len(bins_filled_raw_array)):
        bins_filled_list[int(bins_filled_raw_array[b])] = 1
    df_temp = pd.DataFrame({"bins filled" :pd.Series(bins_filled_list)})
    data =pd.concat([data,df_temp],axis = 1)
    
    #We also need to determine what the equity score is for this non-equity problem
    equity_value = sum(np.exp(-kappa*sum(bin_prices[b]*a_matrix[s][b]*bins_filled_list[b] for b in bin_names)) for s in syndicate_names)
    
    #The values retunred in items_packed_raw_array are the locations of 1's in the 2d array (item_name x bin_name)
    #in order to deteremine which bin they go into, we modulo these numbers with the total number of bins
    items_packed_scrubbed = []
    items_packed_raw_array = np.where([int(round(BP_Syndicate.getVal(y[i]))) for i in itertools.product(item_names,bin_names)])[0]
    #conversion between array object and lits object
    for item in range(len(item_names)):
        items_packed_scrubbed.append(items_packed_raw_array[item]%len(bin_names))
    #add results to the dataframe
    df_temp = pd.DataFrame({"items packed in below bin" :pd.Series(items_packed_scrubbed)})
    data =pd.concat([data,df_temp],axis = 1)

    
    #Finally we deterimne which bins were purchased from which syndicates
    #create a list, length = # of syndicates
    bins_purchased_from_syndicate = [0]*len(syndicate_names)
    for s in range(len(syndicate_names)):
        binary_list = list(np.multiply(bins_filled_list, a_matrix[s]))
        df_temp = pd.DataFrame({f"purchased from syndicate {s}?" :pd.Series(binary_list)})
        data =pd.concat([data,df_temp],axis = 1)
        
        
        #this list will be populated with lists, which correspond to bins purchased from each syndicate
        #need to convert from array to list
        #the below outputs a list of 
        bins_purchased_from_syndicate_s = list(np.where(binary_list)[0])
        bins_purchased_from_syndicate.append(bins_purchased_from_syndicate_s)
        df_temp = pd.DataFrame({f"bins purchased from syndicate {s}": pd.Series(bins_purchased_from_syndicate)})
        data = pd.concat([data,df_temp],axis = 1)
        bins_purchased_from_syndicate = []
    
    #Lastly, we populate the objective value (the sumproduct of the bins used times their value)
    total_spend_on_bins = BP_Syndicate.getObjVal()
    total_time = time.time()-start_time
    #}
    
    return(data, equity_value, total_spend_on_bins, total_time)


#Save for when you want to read from CSV
#{
#data_location = r"C:\Users\Digit\Documents\py\data"
#data_name = "synd.csv"
#data = pd.read_csv(os.path.join(data_location,data_name))
#}
