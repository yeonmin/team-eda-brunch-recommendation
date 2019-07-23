
import pandas as pd
from brunchdata.common import *

# 유저별 선호도가 보정된 데이터를 추출하기 위한 함수
def count_correlction_read_favor(read_data, metadata, user_list,
                                 meta_period=(pd.datetime(2019, 2, 14), pd.datetime(2019, 3, 15)), 
                                 read_period=(20190214, 20190301),
                                 favor_cutoff=0.05 ):
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)

    # meta 전처리
    new_meta = meta_preprocessing(metadata, meta_period, use_megazine=True)
    new_meta['diffday_from_end'] = new_meta['diffday_from_end']-14
    new_meta = new_meta.loc[new_meta['diffday_from_end'] > 0]
    new_meta['diffday_from_end'] = new_meta['diffday_from_end'].apply(lambda x: 15 if x >= 15 else x)
    
    # sub_table article이 얼마나 많이 읽혔는지, return ['article_id', 'count', 'author_id']
    sub_table = get_how_many_read(read) 
    sub_table.rename(columns={'count':'how_many_read'}, inplace=True)

    # eda_table user별로 작가의 글을 몇번 읽었는지, return ['user_id', 'author_id', 'count']
    eda_table = get_how_many_read_by_eachuser(read) 

    # eda_table1 작가가 글을 몇개 썼는지 ['author_id', 'article_id', 'author_article_write_cnt']
    eda_table1 = get_how_many_write(read) 
    
    # eda_tabl4 user별로 작가의 글을 얼마나 다양하게 읽었는데 reuturn ['user_id', 'author_id', 'count']
    eda_table4 = get_how_many_read_each_article_by_eachuser(read) 

    # sub_table1 작가의 글을 다양한 유저가 읽었는지 ['author_id', 'user_id', 'nunique']
    sub_table1 = get_how_many_read_by_variableuser_author(read) # sub_table1
    
    df_table1 = pd.merge(eda_table4, sub_table, on='author_id') #eda_table: 유저가 author_id의 글을 몇번 봤는지 # eda_table4 : 유저가 author_id의 글을 몇개나 봤는지 
    df_table1 = pd.merge(df_table1, sub_table1, on='author_id') #sub_table1 :author_id별로 글을 읽는 user는 몇명인지
    #df_table1 = pd.merge(df_table1, eda_table1, on='author_id', how='left') #sub_table1 : author_id별로 글을 읽는 user는 몇명인지
    df_table1 = pd.merge(df_table1, new_meta, on='article_id', how='left')
    
    df_table1['correction_count'] = (df_table1['count'] * df_table1['how_many_read'])/(df_table1['nunique']) #nunique: 이 작가의 글을 읽는 사람의 수 <- ??
    
    df_table2 = df_table1.sort_values(by='correction_count' ,ascending=False)
    df_table3 = df_table2[['user_id','article_id','correction_count']]
    df_table3 = df_table3.dropna(axis=0)

    user_id_frame = pd.DataFrame({"user_id" : user_list})
    dev1 = user_id_frame.merge(df_table3, on='user_id', how='left')
    dev2 = dev1.groupby('user_id')['user_id'].agg({'size'}).reset_index().sort_values('size')
    dev1 = pd.merge(dev1, dev2, how='left',on='user_id')
    
    read_user = dev1.loc[(dev1['correction_count'].notnull())]
    dontread_user = dev1.loc[(dev1['correction_count'].isnull())]
    read_user = read_user.loc[read_user['correction_count'] > read_user['correction_count'].quantile(favor_cutoff)]
    print("read_user", read_user.shape)
    print("dontread_user", dontread_user.shape)
    return read_user, dontread_user