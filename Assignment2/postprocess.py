import pandas
def run(file_customers, file_loops):
    cust = pandas.read_csv(file_customers)
    # ....

    # prob. of delay out
    len(data[data.delay_out == True]) / len(data)

    # prob. of delay out for high priority
    data[data.priority == 'high'][data.delay_out == True]

    # filter by arrival index (for burnin)
    data[data["arrival_index"].isin([1,2,3,4,5])]

    # prob no delay for high priority
    len(data[data.priority == "high"][data.delay_in == False][data.delay_out == False]) / len(data)
