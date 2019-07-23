import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import itertools
import datetime

def _chainer(s):
    return list(itertools.chain.from_iterable(s))

def make_readdata(rootpath):
    input_path = os.path.join(rootpath, 'read/')
    file_list = os.listdir(input_path)

    a = 1

    # 이부분 점검 필요
    file_list = [f for f in file_list if len(f.split('.')) == 1]

    read_df_list = []
    for file in tqdm(file_list):
        file_path = input_path + file
        df_temp = pd.read_csv(file_path, header=None, names=['raw'])
        df_temp['from'] = file.split('_')[0]
        df_temp['to'] = file.split('_')[1]
        read_df_list.append(df_temp)
    
    read_df = pd.concat(read_df_list)

    read_df['user_id'] = read_df['raw'].apply(lambda x: x.split(' ')[0])
    read_df['article_id'] = read_df['raw'].apply(lambda x: x.split(' ')[1:])

   
    read_cnt_by_user = read_df['article_id'].map(len)
    read_rowwise = pd.DataFrame({'from': np.repeat(read_df['from'], read_cnt_by_user),
                             'to': np.repeat(read_df['to'], read_cnt_by_user),
                             'user_id': np.repeat(read_df['user_id'], read_cnt_by_user),
                             'article_id': _chainer(read_df['article_id'])})

    read_rowwise = read_rowwise.loc[read_rowwise['article_id']!='']
    read_rowwise = read_rowwise.dropna()
    read_rowwise.reset_index(drop=True, inplace=True)
    read_rowwise['dt'] = read_rowwise['from']/100
    read_rowwise['dt'] = read_rowwise['dt'].astype(int)

    return read_rowwise

   
def load_metadata(rootpath):
    input_path = rootpath + 'metadata.json'

    # 부정확 할 수 있지만 reg_ts 0으로 두는 것보다는 좋을 것 같아서 1970 이전에 쓴글의 reg_ts를 가져옴
    # 물론 article_id가 글의 연재 순서가 아닐 수 있지만 magazine은 거의 연재순서와 일치하고 일반 기사도 향성이 있어서 이렇게 함
    metadata = pd.read_json(input_path, lines=True)
    metadata.loc[metadata['reg_ts']==0,'reg_ts'] = np.nan
    metadata.sort_values(['user_id','article_id'], inplace=True)
    metadata['reg_ts'].fillna(method='bfill', inplace=True)
    metadata['reg_dt'] = metadata['reg_ts'].apply(lambda x : datetime.fromtimestamp(x/1000.0))
    metadata['reg_dt'] = metadata['reg_dt'].dt.date

    #metadata.sort_values(['user_id','article_id'], inplace=True)
    #metadata['reg_ts'].fillna(method='bfill', inplace=True)
    #metadata['reg_dt'] = metadata['reg_ts'].apply(lambda x : datetime.fromtimestamp(x/1000.0))

    # 0301부터 했을 때는 더 나빠졌습니다. 
    metadata = metadata.loc[pd.to_datetime(metadata['reg_dt']) <= pd.datetime(2019, 3, 14)]
    metadata = metadata.sort_index()
    metadata = metadata.reset_index(drop=True)

    return metadata


def make_followingdata(rootpath):
    input_path = rootpath + 'users.json'
    users = pd.read_json(input_path, lines=True)

    following_list_count = users['following_list'].map(len)
    following_rowwise = pd.DataFrame({'user_id': np.repeat(users['id'], following_list_count),
                                      'keyword_list': np.repeat(users['keyword_list'], following_list_count),
                                      'following_id': _chainer(users['following_list'])})

    return following_rowwise


def load_predictdata(rootpath, predict_file):
    input_path = rootpath +'predict/' + predict_file
    predict_user = pd.read_csv(input_path,header=None, names=['user_id'])
    return predict_user


def make_predict_following(following_rowwise, predict_user_list):
    following_df = following_rowwise.loc[following_rowwise['user_id'].isin(predict_user_list),['user_id','following_id']]
    following_df.reset_index(drop=True, inplace=True)
    return following_df

