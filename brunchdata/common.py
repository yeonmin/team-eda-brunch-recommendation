import pandas as pd


def get_how_many_read_by_eachuser(read):
    """
    eda_table
    how_many_read_by_eachuser = pd.DataFrame(read.groupby(['user_id'])['author_id'].value_counts())
    how_many_read_by_eachuser.columns = ['count']
    how_many_read_by_eachuser = how_many_read_by_eachuser.reset_index()
    """
    how_many_read_by_eachuser = pd.DataFrame(read.groupby(['user_id'])['author_id'].value_counts())
    how_many_read_by_eachuser.columns = ['count']
    how_many_read_by_eachuser = how_many_read_by_eachuser.reset_index()
    return how_many_read_by_eachuser


def get_how_many_write(read):
    """
    eda_table1
    how_many_write_df = pd.DataFrame(read.groupby(['author_id'])['article_id'].agg({'nunique'}))
    how_many_write_df.columns = ['author_article_write_cnt']
    how_many_write_df = how_many_write_df.reset_index()
    """
    how_many_write_df = pd.DataFrame(read.groupby(['author_id'])['article_id'].agg({'nunique'}))
    how_many_write_df.columns = ['author_article_write_cnt']
    how_many_write_df = how_many_write_df.reset_index()
    return how_many_write_df


def get_how_many_read_repeat(read):
    """
    eda_table2
    how_many_read_repeat_df = pd.DataFrame(read.groupby(['user_id','author_id'])['dt'].agg({'nunique'}))
    how_many_read_repeat_df.columns = ['count']
    how_many_read_repeat_df = how_many_read_repeat_df.reset_index()
    """
    how_many_read_repeat_df = pd.DataFrame(read.groupby(['user_id','author_id'])['dt'].agg({'nunique'}))
    how_many_read_repeat_df.columns = ['count']
    how_many_read_repeat_df = how_many_read_repeat_df.reset_index()
    return how_many_read_repeat_df


def get_how_many_read_each_article_by_eachuser(read):
    """
    eda_table4 = pd.DataFrame(df_table.groupby(['user_id','author_id'])['article_id'].agg({'nunique'}))
    eda_table4.columns = ['count']
    eda_table4 = eda_table4.reset_index()
    """
    how_many_read_each_article_by_eachuser = pd.DataFrame(read.groupby(['user_id','author_id'])['article_id'].agg({'nunique'}))
    how_many_read_each_article_by_eachuser.columns = ['count']
    how_many_read_each_article_by_eachuser = how_many_read_each_article_by_eachuser.reset_index()
    return how_many_read_each_article_by_eachuser    


def get_how_many_read(read):
    """
    sub_table
    how_many_read = pd.DataFrame(read['article_id'].value_counts()).reset_index()
    how_many_read.columns = ['article_id','count']
    how_many_read['author_id'] = how_many_read['article_id'].astype(str).apply(lambda x: x.split('_')[0])
    """
    how_many_read = pd.DataFrame(read['article_id'].value_counts()).reset_index()
    how_many_read.columns = ['article_id','count']
    how_many_read['author_id'] = how_many_read['article_id'].astype(str).apply(lambda x: x.split('_')[0])
    return how_many_read

def get_how_many_read_by_variableuser_author(read):
    """
    sub_table1
    temp = pd.DataFrame(read.groupby('author_id')['user_id'].agg({'nunique'})).reset_index()
    temp.columns = ['author_id','nunique']
    """
    temp = pd.DataFrame(read.groupby('author_id')['user_id'].agg({'nunique'})).reset_index()
    temp.columns = ['author_id','nunique']
    return temp


def get_how_many_read_by_variableuser_article(read):
    """
    sub_table2
    temp = pd.DataFrame(read.groupby('article_id')['user_id'].agg({'nunique'})).reset_index()
    temp.columns = ['article_id','nunique']
    temp = temp.sort_values(by='nunique',ascending=False)
    """
    temp = pd.DataFrame(read.groupby('article_id')['user_id'].agg({'nunique'})).reset_index()
    temp.columns = ['article_id','nunique']
    temp = temp.sort_values(by='nunique',ascending=False)
    return temp


def read_preprocessing(read_data, metadata, read_period):
    # period는 (] 형식으로 start날짜는 포함하고 end날짜는 포함하지 않는다.
    read_cutoff_start = read_period[0] # begin
    read_cutoff_end = read_period[1] # end
    read_index = (read_data['dt'] >= read_cutoff_start) & (read_data['dt'] < read_cutoff_end)
    
    read = read_data.loc[read_index] # read cut off
    read = read.loc[read['article_id'].isin(metadata['id'])] # meta에 없는 read 제거
    read['author_id'] = read['article_id'].astype(str).apply(lambda x: x.split('_')[0])
    return read


def meta_preprocessing(metadata, meta_period, use_megazine=False, use_regdt=False):
    """
    selected_column = ['following_id', 'article_id', 'diffday_from_end']
    if use_megazine is True:
        selected_column = ['following_id','article_id','magazine_id','diffday_from_end']
    if use_regdt is True:
        selected_column = selected_column + ['reg_dt']
    """
    # period는 (] 형식으로 start날짜는 포함하고 end날짜는 포함하지 않는다.
    meta_cutoff_start = meta_period[0] # begin
    meta_cutoff_end = meta_period[1] # end
    meta_cutoff_index = (pd.to_datetime(metadata['reg_dt']) >= meta_cutoff_start) & (pd.to_datetime(metadata['reg_dt']) < meta_cutoff_end)
    
    new_meta = metadata.loc[meta_cutoff_index]
    new_meta['diffday_from_end'] = (meta_cutoff_end - pd.to_datetime(new_meta['reg_dt'])).dt.days
    
    # column rename
    del new_meta['article_id']
    new_meta.rename(columns={'user_id':'following_id','id':'article_id'}, inplace=True)
    
    # select column
    selected_column = ['following_id', 'article_id', 'diffday_from_end']
    if use_megazine is True:
        selected_column = ['following_id','article_id','magazine_id','diffday_from_end']
    if use_regdt is True:
        selected_column = selected_column + ['reg_dt']
    new_meta = new_meta[selected_column]

    return new_meta