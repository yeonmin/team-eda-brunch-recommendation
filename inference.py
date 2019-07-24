import recommend
import config
import timeit

if __name__ == '__main__':
    predict_file = config.predict_file
    submission_file = config.submission_file

    print("Inference Start")
    start = timeit.default_timer()

    rec_sys = recommend.RecommendCLI()
    rec_sys.recommend(predict_file, submission_file)

    stop = timeit.default_timer()
    print("Total running time : {} s".format(stop - start))
    print("Complete")