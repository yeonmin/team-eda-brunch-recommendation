# TEAM-EDA Kakao Arena Brunch Recommendation

## **폴더 구조**
카카오 베이스라인 구조와 동일.
1. res 폴더 내부에 아래와 같이 폴더 구성
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
