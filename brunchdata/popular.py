import pandas as pd
from brunchdata.common import *
import itertools
import numpy as np


def make_timebased_best(readdata, metadata, read_period=(20190221, 20190301)):
    """
    read_period의 시작은 실제보다 하루 작게
    """
    read = read_preprocessing(readdata, metadata , read_period=read_period)
    
    time_based_best = []
    base_read = sorted(read['from'].unique())[23:]
    for item in itertools.zip_longest(base_read, base_read[1:], base_read[2:]):
        try:
            if isinstance(item[1], np.int64) is False:
                raise BaseException(item[1])

            temp = read.loc[read['from'].isin(item),'article_id'].value_counts().reset_index()
            temp.columns = ['article_id','count']
            temp['dt'] = item[1]
        except BaseException as e:
            print(e)
            pass
        else:
            time_based_best.append(temp)
            
    time_based_best = pd.concat(time_based_best)
    """
    result_list = []
    for user_id in tqdm_notebook(user_id_frame['user_id'].unique()):
        from_list = sorted(read.loc[read['user_id']==user_id,'from'].unique())
        for t in from_list:
            temp = time_based_best.loc[time_based_best['dt']==t].reset_index(drop=True)
            temp['user_id'] = user_id
            temp['index'] = range(temp.shape[0])
            result_list.append(temp)
 
    frame = pd.concat(result_list)
    frame = frame.sort_values(['user_id','index','count'],ascending=[False, True, False])
    print(frame.shape)
    return frame
    """
    return time_based_best


def best_correction(readdata, metadata, read_period=(20190201, 20190301)):
    # best model
    most_read_article = read_preprocessing(readdata, metadata ,read_period=read_period) # 2/22 ~ 2/28

    # 가장 많이 읽은 article_id, 마지막 모델에 사용하기 위하여 만듬
    most_read_article = most_read_article['article_id'].value_counts().reset_index()
    most_read_article.columns = ['article_id','value_counts']

    temp = metadata.copy()
    del temp['article_id']
    temp = temp.rename(columns={'id':'article_id'})
    temp = temp[['article_id','reg_dt']]

    most_read_article = most_read_article.merge(temp, on='article_id', how='left')
    most_read_article['dt'] = (pd.datetime(2019, 3, 1, 0, 0) - pd.to_datetime(most_read_article['reg_dt'])).dt.days
    most_read_article['count'] = most_read_article['value_counts']/most_read_article['dt']
    most_read_article['article_num'] = pd.factorize(most_read_article['article_id'])[0]
    most_read_article = most_read_article.sort_values(['count','article_num'],ascending=[False,False])
    most_read_article = most_read_article[['article_id','count']]

    return most_read_article