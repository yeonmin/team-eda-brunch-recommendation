# TEAM-EDA Kakao Arena Brunch Recommendation

## **폴더 구조**
카카오 베이스라인 구조와 동일.
1. res 폴더는 아래와 같이 폴더 구성
2. submission 폴더에 **recommend.txt** 파일 생성됨

```bash
.
├── res
│   ├── predict
│   │   └── test.users
│   ├── read
│   │   ├── 20181000100_2018...
│   │   └── ...
│   ├── magazine.json
│   ├── metadata.json
│   └── users.json
└── submission
```
## **실행 환경**
- python3.6

## **필요 라이브러리**
- numpy
- pandas
- tqdm

## **실행 방법**
```bash
$> python inference.py
```

## **최종 결과물**
```bash
./submission/recommend.txt
```

## **모델 설명**
- weekly_model : 내가 구독하는 작가 중, 가장 선호하는 작가의 위클리 매거진글을 추천. (단, 내가 보지 않은 글의 바로 1주 전과 2주 전은 무조건 봐야 함)
- sereis_model : 내가 구독하는 작가 중, 가장 선호하는 작가의 매거진글을 추천. (단, 내가 보지 않은 글의 바로 1주 전과 2주 전은 무조건 봐야 함)
- dont_weekly_model : 내가 구독하지 않는 작가 중, 가장 선호하는 작가의 위클리 매거진글을 추천. (단, 내가 보지 않은 글의 바로 1주 전과 2주 전은 무조건 봐야 함)
- dont_series_model : 내가 구독하지 않는 작가 중, 가장 선호하는 작가의 매거진글을 추천. (단, 내가 보지 않은 글의 바로 1주 전과 2주 전은 무조건 봐야 함)
- following_favor_many_read_model : 내가 구독하는 작가 중, 가장 선호하는 작가의 인기 글을 추천. (선호 : 작가의 글을 많이 읽음)
- following_favor_repeat_read_model : 내가 구독하는 작가 중, 가장 선호하는 작가의 인기 글을 추천. (선호 : 작가의 글을 다양한 날 읽음)
- variable_user_model : 다양한 사람이 많이 읽은 인기 글. 
- brunch_model : 브런치 공지글(151, 153). 
- regression_user_model : 3월의 글 중에서 사람들이 가장 많이 읽은 것 같은 구독하는 작가의 글. 
- correction_favor_model : 내가 한 번이라도 읽은 작가의 글 중에서 내가 좋아하는 작가이면서 다른 사람들도 많이 읽은 글. 
- most_read_article_model : 사람들이 가장 많이 읽은 글. 