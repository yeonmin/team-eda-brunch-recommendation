import utils
import config

# get entropy score
utils.get_entropy_from_file(config.submission_path + '/recommend.txt', True)

# Compare recommend files
utils.compare_results(config.submission_path + '/recommend.txt', config.submission_path + '/recommend_ss.txt', True)

# Check recs duplication
utils.check_recs_duplication(config.submission_path + '/recommend.txt', False)