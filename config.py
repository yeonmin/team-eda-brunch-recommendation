import pandas as pd

# root path
root_path = './res/'

# read check
read_check_period = (20190101, 20190301)

# series
weekly_meta_period=(pd.datetime(2017, 7, 14, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
weekly_read_period=(20190207, 20190301)
weekly_series_count = 6

series_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
series_read_period=(20190207, 20190301)
series_series_count = 7

dont_following_series_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
dont_following_series_read_period=(20190214, 20190301)
dont_following_series_series_count = 7

dont_following_weekly_meta_period=(pd.datetime(2017, 7, 14, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
dont_following_weekly_read_period=(20190214, 20190301)
dont_following_weekly_series_count = 6

# following
following_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
following_read_period=(20190207, 20190301)
following_favor_cutoff=0.05

dont_following_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
dont_following_read_period=(20190214, 20190301) # 구독을 안했기에 최신 선호도를 반영하고 싶음. 
dont_following_favor_cutoff=0.05

# variable user read
variable_user_model_read_period = (20190214, 20190301)

# regression
regression_model_meta_period=(pd.datetime(2019, 2, 28, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
regression_model_read_period=(20190214, 20190301)
regresssion_before_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 1, 0, 0))
regression_before_read_period=(20190201, 20190301)

# most read
best_read_period = (20190222, 20190301)
best_correction_read_period = (20190101, 20190301)
time_based_best_period = (20190221, 20190301)

# cutoff parameter
weekly_cutoff = 10
series_cutoff = 10
dontseries_cutoff = 5
following_favor_many_read_cutoff = 21
following_favor_repeat_read_cutoff = 21
variable_user_cutoff = 6
regression_march_cutoff = 21
correction_favor_cutoff = 30
most_read_article_cutoff = -1
