
root_path = './res/'

read_check_period = (20190101, 20190301)

weekly_meta_period=(pd.datetime(2017, 7, 14, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
weekly_read_period=(20190207, 20190301)
weekly_series_count = 6

series_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
series_read_period=(20190207, 20190301)
series_series_count = 7

dont_following_series_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
dont_following_series_read_period=(20190214, 20190301)
dont_following_series_series_count = 7

following_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
following_read_period=(20190207, 20190301)
following_favor_cutoff=0.05

variable_user_model_read_period = (20190214, 20190301)

regression_model_meta_period=(pd.datetime(2019, 3, 1, 0, 0), pd.datetime(2019, 3, 15, 0, 0))
regression_model_read_period=(20190214, 20190301)
regresssion_before_meta_period=(pd.datetime(2019, 2, 1, 0, 0), pd.datetime(2019, 3, 1, 0, 0))
regression_before_read_period=(20190201, 20190301)

best_read_period = (20190222, 20190301)
best_correction_read_period = (20190207, 20190301)
time_based_best_period = (20190221, 20190301)