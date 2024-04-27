import pandas as pd
import warnings

def process_data(df_lines):
    pd.set_option('display.max_colwidth', 0)
    pd.set_option('display.max_columns', None)
    pd.options.display.max_seq_items = 2000
    warnings.filterwarnings('ignore')

    # df_lines = pd.read_csv('Data/order_lines.csv', index_col = 0)
    print("{:,} order lines to process".format(len(df_lines)))
    df_lines.head()

    df_uom = pd.read_csv('Data/uom_conversions.csv', index_col = 0)
    print("{:,} Unit of Measure Conversions".format(len(df_uom)))

    # Join
    df_join = df_lines.copy()
    COLS_JOIN = ['Item Code']
    df_join = pd.merge(df_join, df_uom, on=COLS_JOIN, how='left', suffixes=('', '_y'))
    df_join.drop(df_join.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
    print("{:,} records".format(len(df_join)))

    df_dist = pd.read_csv('Data/' + 'distances1.csv', index_col = 0)
    # Location
    df_dist['Location'] = df_dist['Customer Country'].astype(str) + ', ' + df_dist['Customer City'].astype(str)

    df_gps = pd.read_csv('Data/' + 'gps_locations.csv', index_col = 0)
    print("{:,} Locations".format(len(df_gps)))

    df_dist = pd.merge(df_dist, df_gps, on='Location', how='left', suffixes=('', '_y'))
    df_dist.drop(df_dist.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)

    COLS_JOIN = ['Warehouse Code', 'Customer Code']
    df_join = pd.merge(df_join, df_dist, on = COLS_JOIN, how='left', suffixes=('', '_y'))
    df_join.drop(df_join.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
    print("{:,} records".format(len(df_join)))

    # Calculate Weight (KG)
    df_join['KG'] = df_join['Units'] * df_join['Conversion Ratio']

    # Agg by order
    GPBY_ORDER = ['Date', 'Month-Year', 
            'Warehouse Code', 'Warehouse Name', 'Warehouse Country', 'Warehouse City',
            'Customer Code', 'Customer Country', 'Customer City','Location', 'GPS 1', 'GPS 2', 
            'Road', 'Rail', 'Sea', 'Air',
            'Order Number']
    df_agg = pd.DataFrame(df_join.groupby(GPBY_ORDER)[['Units', 'KG']].sum())
    df_agg.reset_index(inplace = True)

    # CO2 Emissions
    dict_co2e = dict(zip(['Air' ,'Sea', 'Road', 'Rail'], [2.1, 0.01, 0.096, 0.028]))
    MODES = ['Road', 'Rail','Sea', 'Air']
    for mode in MODES:
        df_agg['CO2 ' + mode] = df_agg['KG'].astype(float)/1000 * df_agg[mode].astype(float) * dict_co2e[mode]
    df_agg['CO2 Total'] = df_agg[['CO2 ' + mode for mode in MODES]].sum(axis = 1)

    # Calculation @ line level
    df_line = df_join.copy()
    dict_co2e = dict(zip(['Air' ,'Sea', 'Road', 'Rail'], [2.1, 0.01, 0.096, 0.028]))
    MODES = ['Road', 'Rail','Sea', 'Air']
    for mode in MODES:
        df_line['CO2 ' + mode] = df_line['KG'].astype(float)/1000 * df_line[mode].astype(float) * dict_co2e[mode]    
    df_line['CO2 Total'] = df_line[['CO2 ' + mode for mode in MODES]].sum(axis = 1)
    df_line.to_csv('Data/detailed_report.csv')

    # Mapping the delivery Mode
    def find_best_mode(row):
        product_values = [row[mode] * row[f'CO2 {mode}'] for mode in MODES]
        min_product = min(product_values)
        if min_product > 0:
            best_mode_index = product_values.index(min_product)
            return MODES[best_mode_index]
        else:
            return '-'

    df_agg['Best Mode'] = df_agg.apply(find_best_mode, axis=1)

    df_agg['Delivery Mode'] = df_agg[MODES].astype(float).apply(
        lambda t: [mode if t[mode]>0 else '-' for mode in MODES], axis = 1)
    dict_map = dict(zip(df_agg['Delivery Mode'].astype(str).unique(), 
    [i.replace(", '-'",'').replace("'-'",'').replace("'",'') for i in df_agg['Delivery Mode'].astype(str).unique()]))
    df_agg['Delivery Mode'] = df_agg['Delivery Mode'].astype(str).map(dict_map)

    # Save Final Report
    df_agg.to_csv('Data/final_report.csv')
    return df_agg
# df_lines1 = pd.read_csv('Data/order_lines.csv', index_col = 0)
# print(process_data(df_lines1))