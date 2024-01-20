# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 17:40:55 2023

@author: Digit
"""

import numpy as np
import pandas as pd
import os
import operator
import math
#import time


def create_data(num_syndicates, num_items, num_bins):
    #start = time.time()
    #create the original datframe, from which we'll add info to, and reference later
    bin_data = pd.DataFrame({})

    unique_bins = 0
    syn_names = pd.Series(i for i in range(num_syndicates))
    item_sizes = pd.Series(np.random.randint(2,5) for i in range(num_items))
    bin_vols = pd.Series(np.random.randint(5,9) for b in range(num_bins))
    price_of_bins = [np.random.randint(3,10) for b in range(num_bins)]
    
    input_matrix = []
    a_matrix_col_s = []
    bin_price = []
    bin_volume = []
    #DATA SPECIFIC, WATCH THE INDICIES
    #Create the a(vailabiltiy)_matrix, which bins are available from each syndicate.
        #We want to ensure our random availability matrix is a possible solution, by 
    #ensuring there is enough volume in the total bin space to pack every item.
    #We break this up into smaller pieces, forcing the availability column for 
    #each syndicate to have a total bin volume of at least ceiling(total_item_size/num_syndicates) 
        for s in range(num_syndicates):
        #create random list of 1's/0's
        input_matrix_col_s = [np.random.randint(0,2) for i in range(num_bins)]
        
        #sum_{num_synd} bin_volume(b) * input_matrix_col_s(b) for all bins
        sumProduct_bincap_x_pmatrix = sum(map(operator.mul, bin_vols, input_matrix_col_s))
        
        #we need to ensure the total above it at least equal to the average? find better language here
        sumProduct_LowerBound = math.ceil(sum(item_sizes/num_syndicates))  
                
        #What if the input_matrix did not yield enough bin volume? 
        #We randomly change elements of input_matrix into 1, to increase the volume
        while(sumProduct_bincap_x_pmatrix < sumProduct_LowerBound):
            input_matrix_col_s[np.random.randint(0,num_bins)] =1 
            sumProduct_bincap_x_pmatrix = sum(map(operator.mul, bin_vols, input_matrix_col_s))
        
        #We need to ensure that each duplicate from the availabilty_matrix is treated as a uniquie bin
        #thus we redo some work, and create the new a_matrixf
        a_matrix_col_s = [0]*unique_bins
        
        location_of_ones_in_input_matrix_col_s = np.where(input_matrix_col_s)[0]
        number_of_ones_in_input_matrix_col_s = len(location_of_ones_in_input_matrix_col_s)
        
        for b in range(number_of_ones_in_input_matrix_col_s):
            a_matrix_col_s.append(1)
            bin_price.append(price_of_bins[location_of_ones_in_input_matrix_col_s[b]])
            bin_volume.append(bin_vols[location_of_ones_in_input_matrix_col_s[b]])
        df_temp = pd.DataFrame({f"available from syndicate {s}?":pd.Series(a_matrix_col_s)})
        bin_data =pd.concat([bin_data,df_temp],axis = 1).fillna(0)
        unique_bins += len(np.where(input_matrix_col_s)[0])
        
        input_matrix.append(input_matrix_col_s)
    df_temp = pd.DataFrame({"Syndicate Names": pd.Series(i for i in range(num_syndicates)),
                            "Item Size": pd.Series(np.random.randint(2,5) for i in range(num_items)),
                            "Bin Volume":pd.Series(bin_volume),
                            "Price to purchase bin":pd.Series(bin_price)
                            })
    bin_data = pd.concat([bin_data,df_temp],axis = 1)

#need to re-arrange to meet the criteria of the original data creator
    cols = bin_data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    cols = cols[-1:] + cols[:-1]
    cols = cols[-1:] + cols[:-1]
    cols = cols[-1:] + cols[:-1]
    bin_data = bin_data[cols]
    return(bin_data)

#USE THE BELOW TO RUN THE PROGRAM!
#result = create_data(3,4,5)

#print(result)
