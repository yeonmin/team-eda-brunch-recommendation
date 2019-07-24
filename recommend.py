import config
# import fire
from brunchmodel.model import RandomBestRecommend, BrunchRecommend, CutoffRecommend
from brunchdata.following import following_favor_frame
from brunchdata.correctionfavor import count_correlction_read_favor
from brunchdata.popular import best_correction
from brunchdata.loaddata import *
from brunchdata.common import read_preprocessing, get_how_many_read_by_variableuser_article
from brunchdata.series import magazine_series, weekly_magazine_series, dont_following_magazine_series, dont_following_weekly_series
from brunchdata.regression import regression_march
import warnings
warnings.filterwarnings("ignore")

class RecommendCLI():
    def __init__(self):
        pass

    def recommend(self, predict_file, submission_file):
        root_path = config.root_path

        # load default data
        read_rowwise = make_readdata(root_path)
        metadata = load_metadata(root_path)
        following_rowwise = make_followingdata(root_path)
        predict_user_list = load_user_list(root_path, predict_file)
        predict_following = make_predict_following(following_rowwise, predict_user_list)

        # brunch model
        brunch_table = pd.DataFrame()
        brunch_notice = ['@brunch_153','@brunch_151']
        brunch_table['article_id'] = brunch_notice

        # weekly model
        weekly_table = weekly_magazine_series(read_rowwise, 
                                              metadata, 
                                              predict_following, 
                                              meta_period=config.weekly_meta_period, 
                                              read_period=config.weekly_read_period, 
                                              series_count=config.weekly_series_count) # clear

        # series model
        series_table = magazine_series(read_rowwise, 
                                       metadata, 
                                       predict_following,
                                       meta_period=config.series_meta_period, 
                                       read_period=config.series_read_period, 
                                       series_count=config.series_series_count) # clear

        # dont_following_magazine_series
        dont_series_table = dont_following_magazine_series(read_rowwise, 
                                                           metadata, 
                                                           predict_following,
                                                           meta_period=config.dont_following_series_meta_period, 
                                                           read_period=config.dont_following_series_read_period, 
                                                           series_count=config.dont_following_series_series_count) 

        # dont_following_weekly_series
        dont_weekly_table = dont_following_weekly_series(read_rowwise, 
                                                         metadata, 
                                                         predict_following,
                                                         meta_period=config.dont_following_weekly_meta_period, 
                                                         read_period=config.dont_following_weekly_read_period, 
                                                         series_count=config.dont_following_weekly_series_count) 


        # best model
        most_read_article = read_preprocessing(read_rowwise, metadata ,read_period=config.best_read_period) # 2/22 ~ 2/28

        # 가장 많이 읽은 article_id, 마지막 모델에 사용하기 위하여 만듬
        most_read_article = most_read_article['article_id'].value_counts().reset_index()
        most_read_article.columns = ['article_id','value_counts']

        # 구독작가에 맞는 추천을 하기 위하여 사용
        # cumcount는 그룹을 나타내주는데 가장 많이 읽은 article부터 작가의 rank를 나타냄
        most_read_article['author_id'] = most_read_article['article_id'].astype(str).apply(lambda x : x.split('_')[0])
        most_read_article['article_number'] = most_read_article['article_id'].astype(str).apply(lambda x : x.split('_')[1]).astype(int)

        most_read_article = most_read_article.sort_values(by=['value_counts','article_number'],ascending=[False,False] ,kind='mergesort').reset_index(drop=True)
        most_read_article['rank'] = most_read_article.groupby(['author_id'])['author_id'].agg({'cumcount'}).reset_index(drop=True)
        most_read_article_author_rank = most_read_article.copy()


        # following model
        following_favor_many_read = following_favor_frame(read_rowwise, 
                                                          metadata, 
                                                          predict_following, 
                                                          most_read_article_author_rank, 
                                                          correction_type=0,
                                                          meta_period=config.following_meta_period,
                                                          read_period=config.following_read_period,
                                                          favor_cutoff=config.following_favor_cutoff) # clear

        # following model
        following_favor_repeat_read = following_favor_frame(read_rowwise, 
                                                            metadata, 
                                                            predict_following, 
                                                            most_read_article_author_rank, 
                                                            correction_type=1,
                                                            meta_period=config.following_meta_period,
                                                            read_period=config.following_read_period,
                                                            favor_cutoff=config.following_favor_cutoff) # clear

        # variable model
        read_temp = read_preprocessing(read_rowwise, metadata , read_period=config.variable_user_model_read_period)
        variable_user = get_how_many_read_by_variableuser_article(read_temp) # clear

        # user correction model
        read_user_correction, dontread_user_correction  = count_correlction_read_favor(read_rowwise, 
                                                                                       metadata, 
                                                                                       predict_user_list,
                                                                                       meta_period=config.following_meta_period,
                                                                                       read_period=config.following_read_period,
                                                                                       favor_cutoff=config.following_favor_cutoff) # clear

        read_user_correction['article_number'] = read_user_correction['article_id'].astype(str).apply(lambda x : x.split('_')[1]).astype(int)
        read_user_correction = read_user_correction.sort_values(by=['correction_count','article_number'],ascending=[False,False] ,kind='mergesort').reset_index(drop=True)


        # regression march
        regression_march_table = regression_march(read_rowwise, 
                                                  metadata, 
                                                  predict_following,
                                                  meta_period = config.regression_model_meta_period,
                                                  read_period = config.regression_model_read_period,
                                                  regresssion_meta_period = config.regresssion_before_meta_period,
                                                  regression_read_period = config.regression_before_read_period)

        # best read
        most_read_article_frame = most_read_article.copy() # clear

        # read check
        read_check_frame = read_preprocessing(read_rowwise, metadata ,read_period=config.read_check_period)

        best_correction_frame = best_correction(read_rowwise, metadata, read_period=config.best_correction_read_period)

        # make model 
        weekly_model = CutoffRecommend(weekly_table, cutoff_recommend_count=10, userbased_model=True, continous_read=True)
        series_model = CutoffRecommend(series_table, cutoff_recommend_count=10, userbased_model=True, continous_read=True)
        dont_series_model = CutoffRecommend(dont_series_table, cutoff_recommend_count=10, userbased_model=True, continous_read=True)
        dont_weekly_model = CutoffRecommend(dont_weekly_table, cutoff_recommend_count=10, userbased_model=True, continous_read=True)
        following_favor_many_read_model = CutoffRecommend(following_favor_many_read, cutoff_recommend_count=26, userbased_model=True)
        following_favor_repeat_read_model = CutoffRecommend(following_favor_repeat_read, cutoff_recommend_count=26, userbased_model=True)
        # dont_following_favor_each_read_model = CutoffRecommend(dont_following_favor_each_read, cutoff_recommend_count=10, userbased_model=True)
        variable_user_model = CutoffRecommend(variable_user, cutoff_recommend_count=4, userbased_model=False)
        brunch_model = CutoffRecommend(brunch_table, cutoff_recommend_count=2, userbased_model=False)
        regression_user_model = CutoffRecommend(regression_march_table, cutoff_recommend_count=21, userbased_model=True)
        correction_favor_model = CutoffRecommend(read_user_correction, cutoff_recommend_count=30, userbased_model=True)
        # timebased_best_model = TimebasedRecommend(timebased_best_user, timebased_best_time, cutoff_recommend_count=-1)
        most_read_article_model = RandomBestRecommend(best_correction_frame, cutoff_recommend_count=-1)

        # read model
        brunch_recommend_read = BrunchRecommend(read_user_correction['user_id'].unique(), read_check_frame)
        read_model_list = [ weekly_model, series_model, dont_series_model, dont_weekly_model, following_favor_many_read_model, 
                           following_favor_repeat_read_model, variable_user_model, brunch_model, regression_user_model, 
                           correction_favor_model, most_read_article_model]
        brunch_recommend_read.recommend(read_model_list)

        # didn't read model
        brunch_recommend_dontread = BrunchRecommend(dontread_user_correction['user_id'].unique(), 
                                                    read_check_frame, 
                                                    brunch_recommend_read.all_read_set)
        variable_user_model = CutoffRecommend(variable_user, cutoff_recommend_count=9, userbased_model=False)
        read_model_list = [weekly_model, series_model, dont_series_model, dont_weekly_model, following_favor_many_read_model, 
                           following_favor_repeat_read_model, brunch_model, variable_user_model, regression_user_model, 
                           most_read_article_model]
        brunch_recommend_dontread.recommend(read_model_list)

        data_frame_up = brunch_recommend_read.make_result_frame()
        data_frame_down = brunch_recommend_dontread.make_result_frame()
        data_frame = pd.concat([data_frame_up,data_frame_down],axis=0)

        user_id_frame = pd.DataFrame({"user_id" : predict_user_list})
        sub = user_id_frame.merge(data_frame, on='user_id', how='left')
        sub.to_csv(submission_file, index=False, header=False, sep=' ')

# if __name__ == '__main__':
#     fire.Fire(RecommendCLI)
