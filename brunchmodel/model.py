
import pandas as pd
from abc import *

import tqdm


class AbstractRecommend(metaclass=ABCMeta):
    
    def __init__(self):
        pass
    
    @abstractmethod
    def recommend(self):
        pass
    
    def calculate_recommend(self, frame, before_recommend_count, cutoff_recommend_count):
        
        limit_recommend = 100 - before_recommend_count
        # 마지막 모델이거나 cutoff 제한이 없는 경우에는 100-recommend의 개수까지 추천합니다.
        if self.last_model is True or self.cutoff_recommend_count is -1:
            return frame['article_id'].values[:limit_recommend].tolist()
        
        # 설정한 cutoff 보다 추천대상이 작으면 frame article_id를 그대로 return합니다.
        recommend_count = min(limit_recommend, self.cutoff_recommend_count)
        if frame.shape[0] < recommend_count:
            return frame['article_id'].values.tolist()

        # cutoff 보다 추천할 대상이 많으면 cutoff만큼 추천합니다.
        return frame['article_id'].values[:recommend_count].tolist() 


class RandomBestRecommend(AbstractRecommend):
    def __init__(self, recommend_frame, cutoff_recommend_count):
        self.recommend_frame = recommend_frame
        self.cutoff_recommend_count = cutoff_recommend_count
        self.last_model = False
        
    def set_last_model(self):
        self.last_model = True
        
    def recommend(self, read_list, user_id, before_recommend_count):
        frame = self.recommend_frame.query("article_id not in @read_list")
        
        return super().calculate_recommend(frame, before_recommend_count, self.cutoff_recommend_count)


class BrunchRecommend(AbstractRecommend):  
    def __init__(self, user_list, read_frame, read_set=None):
        self.user_list = user_list
        self.read_dict = read_frame.groupby('user_id')['article_id'].apply(list).to_dict()
        self.recommend_result = dict()
        #self.recommend_mixed_result = dict()
        self.all_read_set = set()
        if read_set is not None:
            self.all_read_set = read_set.copy()
    
    def make_result_frame(self):
        temp = pd.DataFrame.from_dict(self.recommend_result).T.reset_index()
        return temp.rename(columns={'index':'user_id'})
    
    def recommend(self, model_list=None):
        try:
            if not model_list:
                raise Exception("model_list는 적어도 한 개 이상 있어야 합니다.")
            
            model_list[-1].set_last_model()
            
            self.recommend_result.clear()
            #self.recommend_mixed_result.clear()
            for user in tqdm_notebook(self.user_list):
                self.recommend_result[user] = list()
                #self.recommend_mixed_result[user] = list()
                # read file에서 user가 이미 읽은 것을 제외합니다.
                try:
                    already_user_read = self.read_dict[user]
                except KeyError as e:
                    already_user_read = []
                
                # model_list를 전달받으면 전달받은 model_list로 추천을 합니다.
                for model in model_list:
                    
                    # 각 모델마다 recommend를 수행합니다.
                    if isinstance(model, RandomBestRecommend) is True:
                        print("RandomBestRecommend")
                        read_list = list(self.all_read_set) + already_user_read
                        r = model.recommend(read_list, user, len(self.recommend_result[user]))
                        print(len(r))
                    else:
                        # user가 읽은 list와 이미 추천했던 결과를 합쳐서 model이 제외할 list를 만듭니다.
                        read_list = self.recommend_result[user].copy()
                        read_list = read_list + already_user_read
                        read_list = list(set(read_list))
                        r = model.recommend(read_list, user, len(self.recommend_result[user]))
                    
                    # recommend
                    self.recommend_result[user] = self.recommend_result[user] + r
                    self.all_read_set = self.all_read_set.union(set(r))
                    #self.recommend_mixed_result[user].append(r)
                    
        except Exception as e:
            print(e)
            raise
            
    def _ndcg(self):
        pass
    def _map(self):
        pass
    def _entropy_diversity(self):
        pass
    def evaluate(self):
        pass


class TimebasedRecommend(AbstractRecommend):
    def __init__(self, user_frame, timebased_frame, cutoff_recommend_count):
        self.timebased_frame = timebased_frame
        self.user_frame = user_frame
        self.cutoff_recommend_count = cutoff_recommend_count
        self.last_model = False
    
    def set_last_model(self):
        self.last_model = True
        
    def recommend(self, read_list, user_id, before_recommend_count):
        user_frame = self.user_frame.loc[self.user_frame['user_id']==user_id]
        from_list = sorted(user_frame['from'].unique())
        if len(from_list) == 0:
            return list()
        
        frame = self.timebased_frame.query("article_id not in @read_list")
        
        frame_list = []
        for t in from_list:
            temp = frame.loc[frame['dt']==t].reset_index(drop=True)
            temp['index'] = range(temp.shape[0])
            frame_list.append(temp)
        
        frame = pd.concat(frame_list)
        frame = frame.sort_values(['index','count'], ascending=[True,False])
        frame = frame.drop_duplicates('article_id', keep='first')
        # 최대 recommend limit를 설정합니다.
        
        return super().calculate_recommend(frame, before_recommend_count, self.cutoff_recommend_count)
        

class CutoffRecommend(AbstractRecommend):
    """
    Cutoff를 가지는 recommend 모델입니다.
    AbstractRecommend를 상속받는 모델은 recommend 함수를 구현해야 합니다.
    
    recommend_frame: 각 추천 모델마다 필요한 전처리된 추천 frame입니다.
    cutoff_recommend_count: 각 모델마다 cutoff값, -1로 설정하면 cutoff 제한이 없이 100 - 이전 모델 추천 개수 까지 추천합니다.
    continous_read: True면 flag_sum을 가지는 연속형 추천 모델이고, False면 flag_sum을 가지지 않는 모델입니다.
    
    기존 현우님 모델은 flag_sum_1,2,3,4,5 라고 되어있었는데 이것을 flag_sum이라는 컬럼에 1,2,3,4,5..n을 추가하는 형태로 변경합니다.
    flag_sum은 반드시 높은 숫자가 좋아야 합니다.
    """
    def __init__(self, recommend_frame, cutoff_recommend_count, userbased_model=True, continous_read=False):
        
        self.recommend_frame = recommend_frame
        self.cutoff_recommend_count = cutoff_recommend_count
        self.continous_read = continous_read
        self.userbased_model = userbased_model
        self.last_model = False
    
    def set_last_model(self):
        self.last_model = True
        
    def recommend(self, read_list, user_id, before_recommend_count):
        """
        parameter
        read_list: 이전 모델까지 추천한 article과 2/22 ~ 3/1일 까지의 읽은 article
        user_id: user별로 추천하는 모델은 user_id를 넘겨줘야 합니다.
        before_count: 이전 모델까지의 추천 개수
        
        return
        list형태의 article_id
        """
        
        # 이전에 추천했던 article을 제거합니다.
        #frame = self.recommend_frame.loc[~self.recommend_frame['article_id'].isin(read_list)]

        # user_id를 사용하는 모델은 해당 user_id만 가져옵니다.
        if self.userbased_model is True:
            frame = self.recommend_frame.query("user_id == @user_id")
            frame = frame.query("article_id not in @read_list")
        else:
            frame = self.recommend_frame.query("article_id not in @read_list")
        
        # flag_sum이 포함된 모델, 연속 추천 모델
        if self.continous_read is True:
            # flag_sum은 높은것이 좋기 때문에 내림차순, count도 높은것이 좋기 때문에 내림차순
            frame = frame.sort_values(by=['flag_sum', 'count'], ascending=[False, False])
            
        return super().calculate_recommend(frame, before_recommend_count, self.cutoff_recommend_count)