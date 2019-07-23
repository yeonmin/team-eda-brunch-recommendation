import six
import math

def _entropy_diversity(recs, topn):
    sz = float(len(recs)) * topn
    freq = {}
    for u, rec in six.iteritems(recs):
        for r in rec:
            freq[r] = freq.get(r, 0) + 1
    ent = -sum([v / sz * math.log(v / sz) for v in six.itervalues(freq)])
    return ent

def get_entropy_from_file(f_name, isTest):
    topn = 100
    sz = 3000
    id_to_recs = {}

    if isTest == True :
        sz = 5000

    with open(f_name, 'r') as f :
        for i in range(sz):
            line = f.readline().strip().split(' ')
            uid = line[0]
            rec = line[1:]
            id_to_recs[uid] = rec

    print("Entropy from file({}) : {}".format(f_name, _entropy_diversity(id_to_recs, topn)))



def compare_results(f_name_1, f_name_2, isTest):
    sz = 3000
    if isTest == True :
        sz = 5000
    
    wrong_cnt = 0
    intersection_cnt = 0

    with open(f_name_1, 'r') as f1 :
        with open(f_name_2, 'r') as f2 :
            for i in range(sz) :
                recs_1 = f1.readline().strip().split(' ')[1: ]
                recs_2 = f2.readline().strip().split(' ')[1: ]

                compare = [(i, recs_1[i], recs_2[i]) for i in range(100) if recs_1[i] != recs_2[i]]
                # print(compare)
                wrong_cnt += len(compare)
                intersection_cnt += len(set(recs_1) & set(recs_2))

                # (optional)
                # if recs_1 != recs_2 :
                #     raise
    print("Wrong count : ", wrong_cnt)
    print("Duplicated count : ", intersection_cnt)

def check_recs_duplication(f_name, isTest):
    recs_dup_cnt = 0
    dup_uid = []
    sz = 3000
    if isTest == True :
        sz = 5000

    with open(f_name, 'r') as f :
        for i in range(sz):
            line = f.readline().strip().split(' ')
            uid = line[0]
            rec = line[1:]

            if len(set(rec)) != 100 :
                recs_dup_cnt += 1
                dup_uid.append(uid)

    print('Recs Duplication count : ', recs_dup_cnt)
    print('Duplicated Uids : ', dup_uid)
