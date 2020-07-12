import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import pandas as pd


def plot_price_distribution(input):
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    # Remove the plot frame lines. They are unnecessary chartjunk.
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Along the same vein, make sure your axis labels are large
    # enough to be easily read as well. Make them slightly larger
    # than your axis tick labels so they stand out.
    plt.xlabel("Arbeitspreis in Ct/kWh", fontsize=16)
    plt.ylabel("Anzahl", fontsize=16)

    # Plot the histogram. Note that all I'm passing here is a list of numbers.
    # matplotlib automatically counts and bins the frequencies for us.
    # "#3F5D7D" is the nice dark blue color.
    # Make sure the data is sorted into enough bins so you can see the distribution.
    plt.hist(input,
             color="#3F5D7D", bins=100)

    # Always include your data source(s) and copyright notice! And for your
    # data sources, tell your viewers exactly where the data came from,
    # preferably with a direct link to the data. Just telling your viewers
    # that you used data from the "U.S. Census Bureau" is completely useless:
    # the U.S. Census Bureau provides all kinds of data, so how are your
    # viewers supposed to know which data set you used?
    plt.text(1300, -5000, "Data source: www.check24.com | "
             "Author: Thomas Sontag", fontsize=10)

    # Finally, save the figure as a PNG.
    # You can also save it as a PDF, JPEG, etc.
    # Just change the file extension in this call.
    # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.
    # plt.savefig("chess-elo-rating-distribution.png", bbox_inches="tight")

    plt.show()


if __name__ == "__main__":

    url = 'postgresql://thomas:1234@localhost/iuppiter_dev'

    engine = create_engine(url)

    dbConnection = engine.connect()

    df = pd.read_sql("select * from \"end_customer_rates\"", dbConnection)

    dbConnection.close()
    hourly_rates = df['hourly_rates']
    basic_rates = df['basic_rates']
    plot_price_distribution(hourly_rates)
    plot_price_distribution(basic_rates)
    print(df)
