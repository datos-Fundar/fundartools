from pandas import option_context
from IPython.display import display

show_full_dataframe_context = option_context('display.max_rows', None, 'display.max_columns', None)

def show_full_dataframe(df):
    with show_full_dataframe_context:
        display(df)

