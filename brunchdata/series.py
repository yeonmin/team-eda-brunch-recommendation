import pandas as pd
from brunchdata.common import *


def shift_preprocessing(series, groupby_col, series_count):
    new_col_list = []
    for shift_num in range(1, series_count+1):
        new_col = f'lag_readYN_{shift_num}'
        new_col_list.append(new_col)
        series[new_col] = series.groupby(groupby_col)['readYN'].shift(-1*shift_num)
    
    new_readYN_sum_list = []
    for shift_num in range(1, series_count):
        new_col = f'readYN_sum_{shift_num}'
        new_readYN_sum_list.append(new_col)
        
        previous_col = f'readYN_sum_{shift_num-1}'
        if shift_num == 1:
            series[new_col] = series[new_col_list[shift_num]] + series[new_col_list[shift_num-1]]
        else:
            series[new_col] = series[previous_col] + series[new_col_list[shift_num]]
    
    series['flag_sum'] = series[new_readYN_sum_list[1:]].max(axis=1)
    series = series.loc[(series['readYN_sum_1']==2) & (series['readYN']==0)].reset_index(drop=True)
    return series


def get_weekly_metadata(metadata, meta_period=(pd.datetime(2017, 7, 27), pd.datetime(2019, 3, 15))):
    
    # meta 전처리
    # return ['following_id','article_id','magazine_id','diffday_from_end', 'reg_dt']
    new_meta = meta_preprocessing(metadata, meta_period, use_megazine=True, use_regdt=True)
    new_meta = new_meta.loc[new_meta['magazine_id'] != 0]
    new_meta['reg_dt_dayofweek'] = pd.to_datetime(new_meta['reg_dt']).dt.dayofweek
    
    # 최신것으로 sort
    new_meta = new_meta.sort_values(by='diffday_from_end', ascending=True)
    
    # dayofweek의 unique한 개수
    metadata_weekly = new_meta.groupby(['magazine_id'])['reg_dt_dayofweek'].agg({'nunique'}).reset_index()
    # 3월 15일부터 글을 올린 날짜의 차이의 unique한 개수
    metadata_reg_dt = new_meta.groupby(['magazine_id'])['diffday_from_end'].agg({'nunique'}).reset_index()
    
    metadata_temp = pd.merge(new_meta, metadata_weekly, on='magazine_id', how='left')
    metadata_temp = pd.merge(metadata_temp, metadata_reg_dt, on='magazine_id', how='left')
    
    # *5주 이상동안 같은 날 연재한 글*
    # nunique_x: reg_dt_dayofweek / nunique_y: diffday_from_end
    # 같은날 연재되면서 diffday가 5개 이상이라는 것을 weekly megazine으로 봄
    # 연속적이지 않을 수 있는데, 그것은 따로 판단
    weekly_megazine = metadata_temp.loc[(metadata_temp['nunique_x']==1) & (metadata_temp['nunique_y']>=5)]
    weekly_megazine['weekly'] = 1
    weekly_megazine = weekly_megazine[['magazine_id','article_id','weekly','diffday_from_end']]
    weekly_megazine['following_id'] = weekly_megazine['article_id'].apply(lambda x: x.split('_')[0])
    return weekly_megazine


def weekly_magazine_series(read_data, metadata, following, 
                           meta_period=(pd.datetime(2017,7, 14), pd.datetime(2019, 3, 15)), 
                           read_period=(20190207, 20190301),
                           series_count=6):
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)
    print("read")
    # get weekly article
    weekly_meta = get_weekly_metadata(metadata)
    print("weekly_meta")
    # weekly 매거진 추천도 내가 구독한 작가만 사용
    following_table = following.copy()
    magazine_table = following_table.merge(weekly_meta, on=['following_id'], how='left')
    print("magazine_table")
    # following table이 user_id, following_id / weekly_meta가 'magazine_id','article_id','weekly','diffday_from_end', following_id
    # following_id를 user_id로 변경
    magazine_table.columns = ['user_id','author_id','magazine_id','article_id','weekly','diffday_from_end']
    magazine_table = magazine_table.dropna(axis=0)
    
    check_reading_table = read[['user_id','article_id']] # df_table은 읽은 것만. 
    check_reading_table['readYN'] = 1
    magazine_table = pd.merge(magazine_table, check_reading_table, how='left',on=['user_id','article_id'])
    magazine_table['readYN'] = magazine_table['readYN'].fillna(0)
    
    magazine_table = magazine_table.sort_values(by='diffday_from_end') #날짜 
    magazine_table = magazine_table.drop_duplicates(['user_id','article_id'])
    
    magazine_table = shift_preprocessing(magazine_table, ['user_id','magazine_id'], series_count)
    
    how_many_read = get_how_many_read_by_eachuser(read)
    magazine_table = pd.merge(magazine_table, how_many_read, how='left', on=['user_id','author_id'])
    return magazine_table
    
    
def magazine_series(read_data, metadata, following_table, 
                    meta_period=(pd.datetime(2019, 2, 14), pd.datetime(2019, 3, 15)), 
                    read_period=(20190207, 20190301),
                    series_count=7):
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)
    
    # meta 전처리
    new_meta = meta_preprocessing(metadata, meta_period, use_megazine=True)
    
    following = following_table.copy()
    series_table = pd.merge(following, new_meta, how='left', on='following_id') # 읽은 글하고 안읽은 글이 섞여요. 
    series_table = series_table.loc[series_table['article_id']!='']
    series_table = series_table.loc[series_table['following_id']!='']
    series_table = series_table.dropna(axis=0)
    series_table.columns = ['user_id','author_id','article_id','magazine_id','diffday_from_end']
    
    check_reading_table = read[['user_id','article_id']] # df_table은 읽은 것만. 
    check_reading_table['readYN'] = 1
    series_table = pd.merge(series_table, check_reading_table, how='left',on=['user_id','article_id'])
    series_table['readYN'] = series_table['readYN'].fillna(0)
    
    series_table = series_table.sort_values(by='diffday_from_end') #날짜 
    series_table = series_table.drop_duplicates(['user_id','article_id'])
    
    series_table = shift_preprocessing(series_table, ['user_id','author_id','magazine_id'], series_count)
    
    how_many_read = get_how_many_read_by_eachuser(read)
    series_table = pd.merge(series_table, how_many_read, how='left',on=['user_id','author_id'])
    
    return series_table

def dont_following_magazine_series(read_data, metadata, following_table, 
                    meta_period=(pd.datetime(2019, 2, 14), pd.datetime(2019, 3, 15)), 
                    read_period=(20190214, 20190301),
                    series_count=7):
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)
    
    # meta 전처리
    new_meta = meta_preprocessing(metadata, meta_period, use_megazine=True)
    
    # 구독한 정보를 토대로 구독하지 않은 작가들의 글만 추출할 것임. 
    following = following_table[['user_id','following_id']]
    following = following.drop_duplicates(subset=['user_id','following_id'])
    following['following'] = 1
    
    # 구독하지 않은 작가의 읽은 정보
    series_table = pd.DataFrame()
    series_table['user_id'] = read['user_id']
    series_table['following_id'] = read['article_id'].apply(lambda x: x.split('_')[0])
    series_table = pd.merge(series_table,following,how='left',on=['user_id','following_id'])
    series_table = series_table[series_table['following'].isnull()].reset_index(drop=True)
    del series_table['following']
    
    # 아래부터는 기존과 동일 
    series_table = pd.merge(series_table, new_meta, how='left', on='following_id') # 읽은 글하고 안읽은 글이 섞여요. 
    series_table = series_table.loc[series_table['article_id']!='']
    series_table = series_table.loc[series_table['following_id']!='']
    series_table = series_table.dropna(axis=0)
    series_table.columns = ['user_id','author_id','article_id','magazine_id','diffday_from_end']
    
    check_reading_table = read[['user_id','article_id']] # df_table은 읽은 것만. 
    check_reading_table['readYN'] = 1
    series_table = pd.merge(series_table, check_reading_table, how='left',on=['user_id','article_id'])
    series_table['readYN'] = series_table['readYN'].fillna(0)
    
    series_table = series_table.sort_values(by='diffday_from_end') #날짜 
    series_table = series_table.drop_duplicates(['user_id','article_id'])
    
    series_table = shift_preprocessing(series_table, ['user_id','author_id','magazine_id'], series_count)
    
    # 선호도로 얼마나 작가의 다양한 글을 읽었는지로 판단.  
    how_many_each_article_read = get_how_many_read_each_article_by_eachuser(read)
    series_table = pd.merge(series_table, how_many_each_article_read, how='left',on=['user_id','author_id'])
    
    return series_table

