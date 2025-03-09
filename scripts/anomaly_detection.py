import pandas as pd


def detect_outliers(df: pd.DataFrame,
                    forecasting_param: str) -> pd.DataFrame:
    '''
    detect outliers in the input data and replace with 
    the same value from last week.

    Param:
    =====
    df: input pandas dataframe
    forecasting_param: the parameter being forecasted
    '''


    # Calculate Q1, Q3, and IQR
    Q1 = df[forecasting_param].quantile(0.25)
    Q3 = df[forecasting_param].quantile(0.75)
    IQR = Q3 - Q1

    # Define outliers using the 1.5*IQR rule
    # use 3 (or higher) for a more conservative detection
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR

    outliers_iqr = df[forecasting_param][(df[forecasting_param] < lower_bound) 
                                        | (df[forecasting_param] > upper_bound)]

    return outliers_iqr