#this function returns the kappa value for our syndicate equity
#Input = dataframe object,
#the one created by the synd_data_creator.py file

#Output = kappas


def kappa(data):
#you dont need this. Data control. You made all the bins as big as the itemss

    total_cost_of_purchased_bins = 0
    for j in range(len(data["Item Size"])):
        bin_counter = 0
        while data["Item Size"].iloc[j] >= data["Bin Volume"].iloc[bin_counter]:
            bin_counter += 1
        total_cost_of_purchased_bins += data["Price to purchase bin"].iloc[bin_counter]
    return(-len(data["Syndicate Names"])/total_cost_of_purchased_bins)
