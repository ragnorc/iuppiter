import calendar
import numpy as np
import pandas as pd
from pandas import Period

from utils import fetch_all_from_db
cal = calendar.Calendar()
import time
import matplotlib.pyplot as plt
from fbprophet import Prophet
from curves import bootstrap_contracts, max_smooth_interp, adjustments
from curves import contract_period as cp
from utils import fetch_all_from_db, fetch_all_from_index, cached
from datetime import date
import pickle
import shelve



class HPFC:

    def __init__(self):

        self.years = [2021,2022,2023]
        self.forecasts_hourly = pd.DataFrame(fetch_all_from_db("PowerSpotForecast"))
        print(self.forecasts_hourly[self.forecasts_hourly["datetime"] == '2020-07-01T00:00:00.000']["weekly"].iloc[0])
        self.shelve = shelve.open("store.db")
        

        # Create full futures table for historical learning and one with removed redundancies to pass to curves
        #TODO: Remove redundant contracts automatically



        data = [
                ["year", 2021, None, None, 36.265, 40.84, None], #Redundant
                ["year", 2022, None, None, 40.63, 51.03, None],
                ["year", 2023, None, None, 42.71, 54.38, None],
                #["year", 2024, None, None, 44, 55.12, None],
                #["year", 2024, None, None, 44, 55.12, None],
                #["year", 2025, None, None, 44.55, 56, None],
                #["year", 2026, None, None, 45.1, 56.53, None],

                ["quarter", 2020, 3, None, 30.32,	34.69, None], #Redundant
                ["quarter", 2020, 4, None, 36.21,	46.99, None],
                ["quarter", 2021, 1, None, 38.71,	50.39, None],
                ["quarter", 2021, 2, None, 33.35, 38.19, None],
                ["quarter", 2021, 3, None, 35.35,	41.23, None],
                ["quarter", 2021, 4, None, 40.58,	54.35, None],
                ["quarter", 2022, 1, None, 44.51,	57.03, None],


                ["month", 2020, 2, 5, 18.98, 21.21, None],
                ["month", 2020, 2, 6, 24.15,	27.12, None],
                ["month", 2020, 3, 7, 29.01,	32.22, None],
                ["month", 2020, 3, 8, 28.07,	31.03, None],
                ["month", 2020, 3, 9, 33.99,	40.77, None],
                ["month", 2020, 4, 10, 34.13, 43.33, None],
                ["month", 2020, 4, 11, 38.53, 49.99, None]]

        data = fetch_all_from_index("power_futures_by_date", "2020-08-05")
        print(data)

        self.original_futures = pd.DataFrame(
            [x for x in data if("base" in x and "peak" in x) and x["base"] != "" and x["peak"] != ""], columns=['product', 'year', 'quarter', 'month', 'base', 'peak', 'offpeak']).astype({"year": pd.Int64Dtype(), "month": pd.Int64Dtype(), "quarter": pd.Int64Dtype()})
        print(self.original_futures)
        self.futures = self.get_cleaned_futures(self.original_futures)
        self.futures = self.futures[self.futures.year < date.today().year + 4]
        print(self.futures)

    def get_cleaned_futures(self, futures): # Remove redundant contracts
        cleaned_futures = pd.DataFrame(columns=['product', 'year', 'quarter', 'month', 'base', 'peak', 'offpeak']).astype({"year": pd.Int64Dtype(), "month": pd.Int64Dtype(), "quarter": pd.Int64Dtype()})
        for i, row in futures.query("product == 'year'").iterrows():
            year = row['year']
            if len(futures.query("product == 'quarter' and year == @year")) < 4:
                 cleaned_futures = cleaned_futures.append(row)

        for i, row in futures.query("product == 'quarter'").iterrows():
            year = row['year']
            quarter = row['quarter']
            if len(futures.query("product == 'month' and year == @year and quarter == @quarter")) < 3:
                cleaned_futures = cleaned_futures.append(row)

        cleaned_futures = cleaned_futures.append(futures.query("product == 'month'"))
        return cleaned_futures



    def get_hours(self, start, end):
        num_base_hours = len(pd.date_range(
            start=start, end=end, freq="D", closed="left"))*24
        num_peak_hours = len(pd.date_range(
            start=start, end=end, freq="B", closed="left"))*12
        # num_rest = num_days  - num_week_days
        return [num_base_hours, num_peak_hours, num_base_hours - num_peak_hours]

    def calc_offpeak(self):

        for i, row in self.futures.iterrows():
            pdindex = None
            if row["product"] == "year":
                pdindex = pd.PeriodIndex([row["year"]], freq="Y")

            elif row["product"] == "quarter":
                pdindex = pd.PeriodIndex(
                    [str(row["year"]) + "-Q" + str(row["quarter"])], freq="Q")
            elif row["product"] == "month":
                pdindex = pd.PeriodIndex(
                    ["{0}-{1}".format(row["year"], row["month"])], freq="M")
                print(pdindex.start_time)
                print(pdindex.end_time)
            num_hours, num_peak_hours, num_offpeak_hours = self.get_hours(pdindex.start_time[0], pdindex.end_time[0])

            self.futures.loc[i, "offpeak"] = [((row["base"]*num_hours-row["peak"]
                                                * num_peak_hours)/(num_offpeak_hours))]
            print(num_hours)
            print(num_peak_hours)

    def get_curve(self):
        contracts = []
        for i, row in self.futures.iterrows():
            pdindex = None
            if row["product"] == "year":
                contracts.append((cp.cal_year(row["year"]), row["peak"]))

            elif row["product"] == "quarter":
                contracts.append((cp.quarter(row["year"],row["quarter"]), row["peak"]))

            elif row["product"] == "month":
                contracts.append((cp.month(row["year"],row["month"]), row["peak"]))

           # print(pdindex.start_time[0])
           # print(pdindex.end_time[0])

            #contracts.append((pdindex.start_time[0], pdindex.end_time[0],row['peak'] ))
            #print((pdindex.start_time[0], pdindex.end_time[0],row['peak'] ))
        ratios = self.get_quartal_shaping_ratios()  +  self.get_monthly_shaping_ratios()
        peak_pc, peak_bc = bootstrap_contracts(contracts, freq='H', shaping_ratios=ratios, average_weight=(lambda x: 1 if self.is_peak(x) else 0))
        offpeak_pc, offpeak_bc = bootstrap_contracts(contracts, freq='H', shaping_ratios=ratios, average_weight=(lambda x: 0 if self.is_peak(x) else 1))
        peak_smooth_curve = max_smooth_interp(peak_bc, add_season_adjust=self.add_adjust, average_weight=(lambda x: 1 if self.is_peak(x) else 0), freq='H')
        offpeak_smooth_curve = max_smooth_interp(offpeak_bc, add_season_adjust=self.add_adjust, average_weight=(lambda x: 0 if self.is_peak(x) else 1), freq='H')
        #self.shelve["peak_smooth_curve"] = peak_smooth_curve
        #self.shelve["offpeak_smooth_curve"] = offpeak_smooth_curve
        #peak_smooth_curve = self.shelve["peak_smooth_curve"]
        #offpeak_smooth_curve =  self.shelve["offpeak_smooth_curve"]
        data = []
        for index, value in offpeak_smooth_curve.items():
            data.append(peak_smooth_curve.loc[index] if self.is_peak(pd.Period(index)) else value)
        print(data)
        pd.Series(data=data, index=offpeak_smooth_curve.index).plot()
        plt.show()

        
        #offpeak_df = offpeak_smooth_curve.to_frame(name="values")
        #peak_df = peak_smooth_curve.to_frame(name="values")
        #weighted_sum["period"] = offpeak_df.index
        #weighted_sum = weighted_sum.assign(offpeak=offpeak_df["values"])
        #print(weighted_sum)
        #weighted_sum["peak"] = peak_df["values"].iloc[:,0]
        #print(weighted_sum)
        
        #print(peak_df["values"]) 




        
        #print(bc_for_spline)
        #offpeak_pc.plot(legend=True)
        #ax = offpeak_smooth_curve.plot(legend=True)
        #ax.legend(["Piecewise Monthly Curve", "Smooth Monthly Curve"])
        plt.show()


# print(calc_offpeak(futures["month"]))
    #def calc_adjust(self):



    def is_peak(self, period):
        return period.dayofweek < 5 and period.hour >= 8 and period.hour <= 20

    def add_adjust(self, period):
        datetime = period.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        add_daily =  self.forecasts_hourly[self.forecasts_hourly["datetime"] == datetime]["weekly"].iloc[0] #self.forecasts_daily.query("ds == @day")["weekly"].iloc[0]
        add_hourly = self.forecasts_hourly[self.forecasts_hourly["datetime"] == datetime]["daily"].iloc[0]
        return  add_daily + add_hourly
        

    def calc_quartals(self):
        for i, row in self.futures.query('product == "year"').iterrows():
            year = row["year"]
            available_quarters = [None, None, None, None]
            for i, row in self.futures.query(
                    'product == "quarter" and year == @year').iterrows():
                available_quarters[row["quarter"]-1] = i
            print(available_quarters)

    def get_quartal_ratio_matrix(self): #
        ratios = np.zeros((4,4))
        for year in self.years:
            #year = row["year"]
            year_quarters = self.futures.query(
                'product == "quarter" and year == @year')
            if len(year_quarters.index) == 4:
                for i, row1 in year_quarters.iterrows():
                    for i, row2 in year_quarters.iterrows():
                        ratios[row1["quarter"]-1,row2["quarter"]-1] = row1["peak"] / row2["peak"]  # Check order or ratios #TODO: Change to offpeak

        return ratios

    def get_quartal_shaping_ratios(self):
        ratio_matrix = self.get_quartal_ratio_matrix()
        shaping_ratios = []
        for year in self.years:
            #year = row["year"]
            year_quarters = self.futures.query(
                'product == "quarter" and year == @year')
            available_quarters = []
            unavailable_quarters = []
            for i in range(1,5):
                if len(year_quarters.query('quarter == @i').index) == 0:
                    if i != 1: # Don't include Q1 because ratios are calculated with Q1 as denominator (ie. in relation to Q1)
                        unavailable_quarters.append(i)
                else:
                    available_quarters.append(i)
            print(available_quarters)
            print(unavailable_quarters)
            for num_ratios, q in enumerate(unavailable_quarters):
                if num_ratios < 3 - len(available_quarters):  # Only add sufficient ratio conditions to solve LSQ
                    if len(available_quarters) > 0:
                        shaping_ratios.append((cp.quarter(year,q),cp.quarter(year,available_quarters[0]),ratio_matrix[q-1,available_quarters[0]-1]))
                    else:
                        shaping_ratios.append((cp.quarter(year,q),cp.quarter(year,1),ratio_matrix[q-1,0]))
        print(shaping_ratios)
        return shaping_ratios
        

    def get_monthly_shaping_ratios(self):
        shaping_ratios = []
        ratios = [1.152986757,	1.177284948,	0.669728294,	0.879009972,	0.957106812,	1.163883215,	0.95958735,	0.934722549,	1.105690101,	0.956957418,	1.06373893,	0.979303652]
        for year in self.years + [2020] :
            for q_index in range(0,3):
                q = q_index+1
                available_months = self.futures.query("year == @year and quarter == @q and product == 'month'")["month"]
                if len(available_months) == 1:
                    shaping_ratios.append((cp.month(year,available_months.iloc[0]+1),cp.quarter(year,q), ratios[available_months.iloc[0]]))
                elif len(available_months) == 0:
                    shaping_ratios.append((cp.month(year,3*q_index+1),cp.quarter(year,q), ratios[3*q_index]))
                    shaping_ratios.append((cp.month(year,3*q_index+2),cp.quarter(year,q), ratios[3*q_index+1]))
        print(shaping_ratios)
        return list(filter(lambda x: x[0].end_time >= date.today() ,shaping_ratios))






hpfc = HPFC()
hpfc.calc_offpeak()
print(hpfc.futures)
#hpfc.calc_quartals()
hpfc.get_curve()
hpfc.get_quartal_shaping_ratios()
print(hpfc.get_monthly_shaping_ratios())
