import utils

# get entropy score
utils.get_entropy_from_file('recommend.txt', False)

# Compare recommend files
utils.compare_results('recommend.txt', 'recommend_2.txt', False)

# Check recs duplication
utils.check_recs_duplication('recommend.txt', False)