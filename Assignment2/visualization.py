import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from os.path import join



def print_latex_table(contents):

    pd.set_option("display.precision", 3)
    contents["experiment"] = list(range(len(contents)))

    contents = contents[["experiment"] + [c for c in contents.columns if c not in "conf_int_low conf_int_high max_total_admitted experiment".split()]]
    contents = contents[[c for c in contents.columns if c not in "conf_int_low conf_int_high max_total_admitted".split()]]
    contents = contents.to_latex(column_format="|{}|".format("|".join(["c"] * len(contents.columns))), index=False)
    contents = contents.replace("\\toprule","\\hline")
    contents = contents.replace("\\midrule","\\hline")
    contents = contents.replace("\\bottomrule","\\hline")
    contents = contents.replace("\\\\", "\\\\ \\hline")

    print("\n\\resizebox{\columnwidth}{!}{%\n" + contents + "}")

    print("""
    \\resizebox{\columnwidth}{!}{%
    \\begin{tabular}{|c|c|c|c|c|c|c|c|}
    \hline
    \\textbf{Experiment} & \\textbf{\\begin{tabular}[c]{@{}c@{}}Prob. no delay\\  (high)\end{tabular}} &
    \\textbf{\\begin{tabular}[c]{@{}c@{}}Blocking Prob.\\ (high)\end{tabular}} &
    \\textbf{\begin{tabular}[c]{@{}c@{}}Mean Waiting Time\\ (high)\end{tabular}} &
    \textbf{\begin{tabular}[c]{@{}c@{}}Prob. no delay\\  (low)\end{tabular}} &
    \textbf{\begin{tabular}[c]{@{}c@{}}Blocking Prob.\\ (low)\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}Mean Waiting Time\\ (low)\end{tabular}} & \textbf{Mean Queue Length} \\ \hline
    \\textbf{1}          & 0                                                                         & 0.68                                                                     & 235.18                                                                      & 0                                                                        & 0.11                                                                    & 256.56                                                                     & 192.45                     \\ \hline
    \\end{tabular} }
    """)

def visualize(output_folder):
    table_contents = []
    
    dataframe = pd.DataFrame(columns=["mean_waiting_time_high", "mean_waiting_time_low", "max_total_admitted"])
    all_dfs = []
    for file in glob.glob("{}/*_stats.csv".format(output_folder)):
        df = pd.read_csv(file)
        all_dfs.append(df)
        row = [df["mean_waiting_time_high"].item(), df["mean_waiting_time_low"].item(), df["max_total_admitted"].item()]
        print(row)
        if np.isnan(row[-1]):
            nan_admitted_info = row
        else:
            dataframe.loc[len(dataframe)] = row

    xlabels = dataframe["max_total_admitted"]
    plotstyle = "*" if len(dataframe) == 1 else "-"
    plt.plot(list(range(len(xlabels))), dataframe["mean_waiting_time_high"], plotstyle, label='mean_waiting_time_high')
    plt.plot(list(range(len(xlabels))), dataframe["mean_waiting_time_low"], plotstyle, label='mean_waiting_time_low')
    plt.axhline(row[0], label="mean_waiting_time_high_Ninf",linestyle="--", color="blue")
    plt.axhline(row[1], label="mean_waiting_time_low_Ninf",linestyle="--", color="orange")
    plt.legend("mean_waiting_high mean_waiting_low mean_waiting_time_low_Ninf mean_waiting_time_high_Ninf".split())
    plt.xticks(list(range(len(xlabels))), xlabels)
    
    plt.xlabel('Max Total Admitted')
    plt.ylabel('Mean Waiting Time')

    plt.title("System Behavior")
    plt.legend()
    plt.savefig(join(output_folder, 'plot.png'))
    #plt.show()
    print_latex_table(pd.concat(all_dfs))

if __name__ == '__main__':
    visualize("runs")
