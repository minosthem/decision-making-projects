import pandas as pd
import matplotlib.pyplot as plt
import os
from os.path import join


def visualize(output_folder):
    dataframe = pd.DataFrame(columns=["mean_waiting_time_high", "mean_waiting_time_low", "max_total_admitted"])
    for file in os.listdir(output_folder):
        if file.endswith("stats.csv"):
            df = pd.read_csv(join(output_folder, file))
            row = [df["mean_waiting_time_high"], df["mean_waiting_time_low"], df["max_total_admitted"]]
            dataframe.loc[len(dataframe)] = row
    # fig, ax = plt.subplots(1, 1)
    # df = pd.DataFrame(dataframe, columns=['mean_waiting_time_high', 'mean_waiting_time_low'])
    # ax.get_xaxis().set_visible(False)
    # df.plot(table=True, ax=ax)

    plt.plot(dataframe["max_total_admitted"], dataframe["mean_waiting_time_high"], label='mean_waiting_time_high')
    plt.plot(dataframe["max_total_admitted"], dataframe["mean_waiting_time_low"], label='mean_waiting_time_low')

    plt.xlabel('Max Total Admitted')
    plt.ylabel('Mean Waiting Time')

    plt.title("System Behavior")
    plt.legend()
    plt.savefig(join(output_folder, 'plot.png'))
    plt.show()


if __name__ == '__main__':
    visualize("output")
