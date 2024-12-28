import mysql.connector as sql
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

fraud_detection = sql.connect(host='localhost',database='fraud_detection',user='root',password='Musicfreak411!')

print(fraud_detection)

cursor = fraud_detection.cursor()

def plot_ids(): 
    cursor.execute(f"SELECT DISTINCT customer_id FROM customer_transactions where customer_id between 0 and 26 ORDER BY customer_id")
    ids = [id[0] for id in cursor.fetchall()]

    num_ids = len(ids)
    fig, ax = plt.subplots(5,5,figsize=(15,15))
    fig.tight_layout(pad=4.0)

    ax = ax.flatten()

    for unique_id in ids:
        statement = (f"SELECT date, amount from customer_transactions WHERE customer_id={unique_id}")

        cursor.execute(statement)
        data = cursor.fetchall()

        xvals = ([date[0] for date in data])
        yvals = [amount[1] for amount in data]
        
        ax[unique_id-1].plot(xvals,yvals)
        ax[unique_id-1].set_title(f'Customer {unique_id}')

        try: 
            xlabels = [date.strftime('%m-%d') for date in xvals]
            ax[unique_id-1].set_xticklabels(xlabels)
        except ValueError:
            pass
        except AttributeError:
            pass

    plt.show()

    fraud_detection.close()

plot_ids()

def plot_times():
    #only ids with multiple large transactions
    ids = [1,3,6,7,9,12,16,18,24,25]

    fig, ax = plt.subplots(4,3,figsize=(10,10))
    fig.tight_layout(pad=4.0)

    ax = ax.flatten()

    for id in range(len(ids)):
        statement = (f"SELECT HOUR(date), SUM(amount) FROM customer_transactions WHERE customer_id={ids[id]} GROUP BY HOUR(date) ORDER BY HOUR(date) DESC")

        cursor.execute(statement)
        data=cursor.fetchall()

        xvals = [hour[0] for hour in data if hour[0] is not None]
        yvals = [amount[1] for amount in data if amount[0] is not None]

        ax[id].bar(xvals,yvals)
        ax[id].set_title(f"Customer {ids[id]}")

    plt.show()
    fraud_detection.close()

plot_times()

def plot_stacked_bars():
    #only ids with large transactions at odd hours
    ids = [1,3,6,7,9,12,16,18,25]

    fig, ax = plt.subplots(3,3,figsize=(10,10))
    fig.tight_layout(pad=4.0)

    ax = ax.flatten()
    processed = []
    items = []

    for id in range(len(ids)):
        statement = (f"SELECT HOUR(date),amount,merchant_description FROM customer_transactions WHERE customer_id = {ids[id]} order by hour(date)")
            
        cursor.execute(statement)
        data=cursor.fetchall()

        #convert to list of tuples
        restaurants = [(hour,amount, description) for hour, amount, description in data if description == 'restaurant']
        coffee = [(hour,amount, description) for hour, amount, description in data if description == 'coffee shop']
        bars = [(hour,amount, description) for hour, amount, description in data if description == 'bar']
        pubs = [(hour,amount, description) for hour, amount, description in data if description == 'pub']
        truck = [(hour,amount, description) for hour, amount, description in data if description == 'food truck']
        
        #convert to data frame
        df_rest = pd.DataFrame(restaurants,columns=['Hour','Restaurants','Merchant Type'])
        df_cof = pd.DataFrame(coffee,columns=['Hour','Coffee Shops','Merchant Type'])
        df_bar = pd.DataFrame(bars,columns=['Hour','Bars','Merchant Type'])
        df_pub = pd.DataFrame(pubs,columns=['Hour','Pubs','Merchant Type'])
        df_truck = pd.DataFrame(truck,columns=['Hour','Food Trucks','Merchant Type'])

        xvals = list(range(24))

        #sum duplicate values
        sum_rest = df_rest.groupby('Hour')['Restaurants'].sum().reindex(xvals,fill_value=0)
        sum_cof = df_cof.groupby('Hour')['Coffee Shops'].sum().reindex(xvals,fill_value=0)
        sum_bar = df_bar.groupby('Hour')['Bars'].sum().reindex(xvals,fill_value=0)
        sum_pub = df_pub.groupby('Hour')['Pubs'].sum().reindex(xvals,fill_value=0)
        sum_truck = df_truck.groupby('Hour')['Food Trucks'].sum().reindex(xvals,fill_value=0)

        ax[id].bar(xvals,sum_rest,color='steelblue',label='Restaurants')
        ax[id].bar(xvals,sum_cof,bottom=sum_rest,color='red',label='Coffee Shops')
        ax[id].bar(xvals,sum_bar,bottom=(sum_rest + sum_cof),color='green',label='Bars')
        ax[id].bar(xvals,sum_pub,bottom=(sum_rest + sum_cof + sum_bar),color='purple',label='Pubs')
        ax[id].bar(xvals,sum_truck,bottom=(sum_rest + sum_cof + sum_bar + sum_pub),color="orange",label='Food Trucks')
        ax[id].set_title(f"Customer {ids[id]}")

        consolidated = pd.merge(sum_rest,sum_cof, on='Hour')
        consolidated = pd.merge(consolidated,sum_bar,on='Hour')
        consolidated = pd.merge(consolidated,sum_pub,on='Hour')
        consolidated = pd.merge(consolidated,sum_truck,on='Hour')

        print(consolidated)

    handles, labels = ax[0].get_legend_handles_labels()

    fig.legend(handles, labels, loc='upper right')
    plt.show()

plot_stacked_bars()