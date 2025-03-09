# import skforecast
from skforecast.recursive import ForecasterRecursive
from skforecast.model_selection import TimeSeriesFold, backtesting_forecaster

from xgboost import XGBRegressor
import pandas as pd


# def train_forecaster(data: pd.DataFrame)
#         -> :

# # trian an autoregressive model using lags using XGBoost

#     exog_features = [
#                     'temperature_2m_max', 
#                     'temperature_2m_min', 
#                     'weekend', 
#                     'quarter_x', 'quarter_y'
#                     ]

#     forecaster = ForecasterRecursive(regressor=XGBRegressor(random_state=769, 
#                                                       enable_categorical=True),
#                                                       lags=[1,2,7]
#                                                       )


#     forecaster.fit(y=data_df.loc[:end_valid, 'OCCUPANCY_RATE_BEDS'])

#     cv = TimeSeriesFold(steps=7, #prediction horizon
#                         initial_train_size=len(data_df[:end_valid])-1,
#                         fixed_train_size=True,
#                         gap=0,
#                         skip_folds=None,
#                         allow_incomplete_fold=True,
#                         refit=False # no re-fitting between predictions
#                         )
    
#     metric, predictions = backtesting_forecaster(forecaster=forecaster,
#                                                  y=data_df['OCCUPANCY_RATE_BEDS'],
#                                                  cv=cv,
#                                                  exog=data_df[exog_features],
#                                                  metric='mean_absolute_error',
#                                                  n_jobs='auto',
#                                                  verbose=True,
#                                                  show_progress=True
#                                                  )
    
#     return metric, predictions