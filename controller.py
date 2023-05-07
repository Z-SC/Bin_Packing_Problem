# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 12:04:00 2023

@author: Digit
"""

import synd_data_creator as sdc
import synd
import time
import os
import datetime
import synd_equity
import math
import kappa
import pandas as pd
import csv
import pyscipopt

#define results directory and name
#{
results_location = r"/home/showaltz/models/data"
#}

syndicate_list = [10,10,15,25,50]
item_list =      [5, 20,30,10,40]
bin_list  =      [10,30,40,20,50]

num_runs = 100

#syndicate_list = [10]
#item_list =      [5]
#bin_list  =      [10]
size_of_list = len(item_list)*num_runs

combined_time_list = [0]*size_of_list
size_of_sumulation = [0]*size_of_list

time_synd = [0]*size_of_list
synd_spend_on_bins = [0]*size_of_list
synd_equity_score = [0]*size_of_list

time_equity = [0]*size_of_list
equity_spend_on_bins = [0]*size_of_list
equity_equity_score = [0]*size_of_list


for i in range(len(syndicate_list)*num_runs):
    print(f'time start for run {i}', datetime.datetime.now())
    data = sdc.create_data(syndicate_list[math.floor(i/num_runs)],item_list[math.floor(i/num_runs)],bin_list[math.floor(i/num_runs)])
    K = kappa.kappa(data)
    combined_time = time.time()
    
    #our data outputs 4 data points
    #DataFrame object, the 'Equity score', the total spent on bins (sumproduct) and the total time taken to run
    synd_result, NE_equity_val, NE_total_spend_on_bins, NE_total_time = synd.Syndicate_BP(data,K)

    equity_result, E_equity_val, E_total_spend_on_bins, E_total_time  = synd_equity.Equity_BP(data,K)

    time_synd[i] = NE_total_time
    synd_spend_on_bins[i] = NE_total_spend_on_bins
    synd_equity_score[i] = NE_equity_val
    
    time_equity[i] = E_total_time
    equity_spend_on_bins[i] = E_total_spend_on_bins
    equity_equity_score[i] = E_equity_val
    size_of_sumulation[i] = [syndicate_list[math.floor(i/num_runs)],item_list[math.floor(i/num_runs)],bin_list[math.floor(i/num_runs)]]
    
    end_time = time.time()-combined_time
    combined_time_list[i] = end_time/60
    
    analysis = pd.DataFrame({"Simulation size" : pd.Series(size_of_sumulation),
                         "Run time non-equity": pd.Series(time_synd),
                         "Run time equity": pd.Series(time_equity),
                         "Total run time": pd.Series(combined_time_list),
                         "Non-equity total spend on bins" : pd.Series(synd_spend_on_bins),
                         "Equity total spend on bins" : pd.Series(equity_spend_on_bins),
                         "Non-equity equity score" : pd.Series(synd_equity_score),
                         "Equity equity score": pd.Series(equity_equity_score)})

    if(2*i%num_runs == 0):
            equity_name = f"synd_equity_output{i}.csv"
            synd_name= f"synd_output{i}.csv"
        
            synd_result.to_csv(os.path.join(results_location,synd_name))
            equity_result.to_csv(os.path.join(results_location,equity_name))
            analysis_name = f"analysis_data_part_{i}.csv"
            analysis.to_csv(os.path.join(results_location,analysis_name))
