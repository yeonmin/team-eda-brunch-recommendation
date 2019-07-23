import pandas as pd
from brunchdata.common import *

def get_regression_best(read_data, metadata, 
                        regresssion_meta_period=(pd.datetime(2019, 2, 1), pd.datetime(2019, 3, 1)), 
                        regression_read_period=(20190201, 20190301)):
    # regression_read2
    read_regression = read_preprocessing(read_data, metadata, regression_read_period)
    read_regression = read_regression['article_id'].value_counts().reset_index()
    read_regression.columns = ['article_id', 'value_counts']
    
    # regresssion_meta2 ['following_id', 'article_id', 'diffday_from_end', 'reg_dt']
    meta_regression = meta_preprocessing(metadata, regresssion_meta_period, use_megazine=False, use_regdt=True)
    meta_regression = meta_regression[['article_id','reg_dt']]
    
    regression_best = pd.merge(read_regression, meta_regression, how='left',on='article_id')
    regression_best['diff_reg_datetime'] = pd.datetime(2019, 3, 1, 0, 0) - pd.to_datetime(regression_best['reg_dt'])
    regression_best = regression_best.dropna(axis=0)

    # 차이가 나는 날짜 계산
    regression_best['diff_reg_hr'] = 24*regression_best['diff_reg_datetime'].dt.days + pd.to_datetime(regression_best['diff_reg_datetime']).dt.hour
    regression_best['count'] = regression_best['value_counts'] / regression_best['diff_reg_hr']

    # 작가 별 평균 count 계산하기. ( count = 시간당 사람들이 글을 읽는 횟수) 
    regression_best['author_id'] = regression_best['article_id'].apply(lambda x: x.split('_')[0])
    regression_best = regression_best.groupby(['author_id'])['count'].agg({'mean'}).reset_index()
    
    return regression_best


def regression_march(read_data, metadata, following_table,
                        meta_period=(pd.datetime(2019, 3, 1), pd.datetime(2019, 3, 15)), 
                        read_period=(20190214, 20190301),
                        regresssion_meta_period=(pd.datetime(2019, 2, 1), pd.datetime(2019, 3, 1)), 
                        regression_read_period=(20190201, 20190301)):
    
    regression_best = get_regression_best(read_data, metadata, regresssion_meta_period, regression_read_period)
    
    # meta 전처리 diffday_from_end
    new_meta = meta_preprocessing(metadata, meta_period, use_megazine=False, use_regdt=True)
    new_meta = new_meta[['article_id','reg_dt']]
    new_meta['reg_dt'] = pd.to_datetime(new_meta['reg_dt'])
    new_meta['diff_reg_datetime'] = pd.datetime(2019, 3, 15, 0, 0) - new_meta['reg_dt']
    new_meta['diff_reg_hr'] = 24*new_meta['diff_reg_datetime'].dt.days + pd.to_datetime(new_meta['diff_reg_datetime']).dt.hour
    new_meta['author_id'] = new_meta['article_id'].apply(lambda x: x.split('_')[0])
    
    new_meta = pd.merge(new_meta, regression_best, how='left', on='author_id')
    new_meta['count'] = new_meta['mean'] * new_meta['diff_reg_hr']
    new_meta = new_meta[['article_id','author_id','count']]
    
    # 3월달의 user별 구독작가 정보를 토대로 한 추천결과 만들기. 
    following = following_table.copy()
    following.columns = ['user_id','author_id']
    regression_march = pd.merge(following, new_meta, how='left',on='author_id')
    
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)
    # eda_table user별로 작가의 글을 몇번 읽었는지, return ['user_id', 'author_id', 'count']
    eda_table = get_how_many_read_by_eachuser(read) 
    
    regression_march = pd.merge(regression_march, eda_table,how='left',on=['user_id','author_id'])
    regression_march.columns = ['user_id','author_id','article_id','regression_cnt','favor_cnt']
    regression_march = regression_march.sort_values(by=['favor_cnt','regression_cnt'], ascending=[False,False])
    regression_march = regression_march.dropna(axis=0)
    
    return regression_march