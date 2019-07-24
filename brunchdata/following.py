
import pandas as pd
from brunchdata.common import *


def recent_following_article(following_favor, col1, col2):
    # groupby sort_values 순서가 ascending=True라서 -1곱해서 바꿔줌. 
    following_favor['count'] = following_favor[col1] * -1 / following_favor[col2]
    
    # count는 내림차순(-1을 곱한 상태에서 내림차순), reg_dt는 오름차순으로 되는데 =>  
    following_favor = following_favor.groupby(['user_id', 'count']).apply(lambda x: x.sort_values(by ='diffday_from_end')).reset_index(drop=True)
    following_favor['count'] = following_favor['count'] * -1
    return following_favor


def rank_preprocessing(following_favor):
    following_favor_null = following_favor.loc[following_favor['rank'].isnull()].reset_index(drop=True)
    following_favor_not_null = following_favor.loc[following_favor['rank'].notnull()].reset_index(drop=True)
    
    # 3월 글
    following_favor_null = following_favor_null.loc[following_favor_null['diffday_from_end']<=15]
    
    # 많이 읽힌글 가져오기
    following_favor_not_null = following_favor_not_null.loc[following_favor_not_null['rank']<10].reset_index(drop=True)
    
    temp = pd.concat([following_favor_null,following_favor_not_null], axis=0)
    return temp


# 구독자 선호도
def following_favor_frame(read_data, metadata, following_table, best, 
                          correction_type=0,
                          meta_period=(pd.datetime(2019, 2, 22), pd.datetime(2019, 3, 15)), 
                          read_period=(20190214, 20190301),
                          favor_cutoff=0.05):
    
    # read 전처리
    read = read_preprocessing(read_data, metadata, read_period)
    
    # meta 전처리
    new_meta = meta_preprocessing(metadata, meta_period)

    # 내가 구독하는 작가의 글 중에서 최신글
    following_favor = following_table.copy()
    following_favor = pd.merge(following_favor, new_meta, how='left', on='following_id')
    following_favor = following_favor.loc[following_favor['article_id']!='']
    following_favor = following_favor.loc[following_favor['following_id']!='']
    following_favor = following_favor.dropna(axis=0)
    following_favor.columns = ['user_id', 'author_id', 'article_id', 'diffday_from_end']
    
    # count 보정을 위한 read에서 통계값 구하기
    if correction_type == 0:
        correction_df1 = get_how_many_read_by_eachuser(read)
    else:
        correction_df1 = get_how_many_read_repeat(read)
        
    how_many_write_df = get_how_many_write(read)
    
    following_favor = following_favor.merge(correction_df1, how='left', on=['user_id','author_id'])
    following_favor = following_favor.merge(how_many_write_df, how='left', on=['author_id'])
    following_favor = following_favor.merge(best, how='left',on=['article_id','author_id'])
    following_favor = following_favor[following_favor['count'].notnull()]
    
    # read count 보정 후, 최근 article sort
    following_favor = recent_following_article(following_favor, 'count', 'author_article_write_cnt')
    
    # 하위 5% cutoff
    following_favor = following_favor.loc[following_favor['count'] > following_favor['count'].quantile(favor_cutoff)] 
    # best에서 전달받은 rank 전처리
    following_favor = rank_preprocessing(following_favor)
    # count로 sort
    following_favor = following_favor.sort_values(by=['count','rank','diffday_from_end'], ascending=[False,True,False])
    return following_favor
