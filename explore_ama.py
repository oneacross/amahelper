import json
import pprint
import argparse
import datetime
import re
import statistics
from collections import defaultdict
#from nltk.tag import pos_tag
#from nltk.tokenize import word_tokenize

TOPICS = {
    'Donald Trump': [
        'donald', 'trump',
    ],
    'Hillary Clinton': [
        'hillary', 'clinton',
        'hilary',
    ],
    'Bernie Sanders': [
        'bernie', 'sanders',
    ],
    'Noam Chomsky': [
        'noam', 'chomsky',
    ],
    'Artificial Intelligence': [
        'artificial', 'intelligence',
        '\bai\b',
    ],
    'Omer Aziz': [
        'omer', 'aziz',
    ],
    'Saudi Arabia': [
        'saudi', 'arabia', 'saud',
    ],
    'Open Borders': [
        'open borders',
        'open border',
    ],
    'Free Will': [
        'free will',
        'determinism',
    ],
    'Martial Arts': [
        'martial arts',
        'jujitsu',
        'self defense',
    ],
    'Vegetarian': [
        'vegetarian',
        'vegan',
    ],
    'Meditation': [
        'meditation',
        'meditate',
        'zen',
    ],
    'Islam': [
        'islam',
        'islamic',
        'quran',
        'koran',
        'qu\'ran',
        'qur\'an',
        'islamist',
        'islamism',
        'jihadist',
        'jihadism',
        'muslim',
    ],
    'Regressive Left': [
        'regressive left',
        'regressive-left',
        'regressive',
    ],
    'Consciousness': [
        'consciousness',
        'agency',
    ],
    'James Randi': [
        'james randi',
        'randi',
    ],
    'Reza Aslan': [
        'reza aslan',
        'reza',
        'aslan',
    ],
    'Modernism': [
        'modernism',
    ],
    'Assisted Suicide': [
        'assisted suicide',
    ],
    'Buddhism': [
        'buddhism',
        'buddhist',
    ],
    'Hinduism': [
        'hinduism',
        'hindu',
    ],
    'Privacy Encryption': [
        'privacy',
        'cryptography',
        'apple',
    ],
    'Taxes': [
        'taxes',
        'taxation',
    ],
    'US Debt': [
        'us national debt',
    ],
    'Voting System': [
        'voting system',
    ],
    'Free Time': [
        'free time',
        'for fun',
    ],
    'Crypto-Currency': [
        'cryptocurrency',
        'bitcoin',
    ],
    'Economics': [
        'economics',
    ],
    'US Politics': [
        'republican',
        'democrat',
        'green party',
        'independent',
        'independant',
    ],
    'Changed your mind': [
        'changed your mind',
    ],
    'Parenting': [
        '\bparent',
    ],
    'Climate Change': [
        'climate change',
    ],
}

# The fullname of comments that I feel are just silly.
SILLY_STUFF = [
    't1_d127ucg',
    't1_d11o45x',
    't1_d12f0la',
    't1_d11qdg6',
]

def convert_to_word_to_topic_hash(topics):
    inverted_topics = {}

    for topic, words in topics.items():
        for word in words:
            inverted_topics[word] = topic

    return inverted_topics
        

def sort_by_author_count(comments):
    # Get the submit count for each author.
    submit_count = {}

    for comment in comments:
        name = comment['author_name']
        if name not in submit_count:
            submit_count[name] = 1
        else:
            submit_count[name] += 1

    for name, count in submit_count.items():
        print("{} {}".format(count, name))

def print_comment_oneline(comment):
    # Convert newlines into spaces.
    text = comment['body'][:50].replace('\n', ' ')
    created = datetime.datetime.fromtimestamp(comment['created']).strftime('%c')
    #print("created={} score={} author={} text={}".format(created, comment['score'], comment['author_name'], text))
    #print("{}, {}".format(created, comment['score']))
    if len(comment['topics']) == 0:
        topics_str = 'None'
    else:
        topics_str = ', '.join(comment['topics'])

    print("{:5} | {:6} | {}".format(comment['score'], topics_str, comment['permalink']))

def print_comment(comment):
    print("========== score={} author={}".format(comment['score'], comment['author_name']))
    print(comment['body'])
    print()


def ls_comments(comments):
    for comment in comments:
        print_comment_oneline(comment)

def word_freq(comments, STOP_WORDS):
    words = defaultdict(int)

    for comment in comments:
        comment_words = comment['body'].split()

        for word in comment_words:
            # Do not count these words.
            if word.lower() not in STOP_WORDS:
                words[word.lower()] += 1

    # Print out the word frequency
    for word, freq in words.items():
        print("{} {}".format(freq, word))

def capword_freq(comments):
    capwords = defaultdict(int)
    for comment in comments:
        comment_words = comment['body'].split()

        for word in comment_words:
            if re.match('[A-Z]', word):
                capwords[word] += 1

    # Print out the frequency of capwords
    for word, freq in capwords.items():
        print("{} {}".format(freq, word))


#def comment_tokenize(comments):
#    for comment in comments:
#        tokens = pos_tag(word_tokenize(comment['body']))
#        print(tokens)

def create_comment_tags(comment, topics):
    text = comment['body']
    tags = []

    for topic, keywords in topics.items():
        # If any of the topic keywords are in the body, then add topic to tags.
        got_match = len([kw for kw in keywords if re.search(kw, text, flags=re.IGNORECASE)]) > 0

        if got_match:
            tags.append(topic)

    return tags

def remove_silly_stuff(comments, SILLY_STUFF):
    # Remove silly comments
    comments = [c for c in comments if c['fullname'] not in SILLY_STUFF]

    return comments


def get_latest_date(comments):
    # The created date is in the epoch units.
    latest_date = 0
    for comment in comments:
        if comment['created'] > latest_date:
            latest_date = comment['created']
    return latest_date

def get_num_authors(comments):
    authors = set([c['author_name'] for c in comments])
    return len(authors)

def print_header(comments, min_score):
    # min_score is None if there is no min score.

    latest_date = get_latest_date(comments)
    num_comments = len(comments)
    num_authors = get_num_authors(comments)

    header = "As of {}, there were {} total comments from {} unique authors".format(
        datetime.datetime.fromtimestamp(latest_date).strftime('%c'),
        num_comments,
        num_authors,
    )

    if min_score:
        header = "{} (with min score of {})".format(header, min_score)

    print("Summary")
    print("=======")
    print(header)
    print()

def print_score_dist(comments):
    # Print the distribution of scores.
    # The min, max, mean, median, std-dev.
    # Return the statistics in a hash.
    scores = [c['score'] for c in comments]

    min_score = min(scores)
    max_score = max(scores)
    mean_score = statistics.mean(scores)
    median_score = statistics.median(scores)
    pstdev_score = statistics.pstdev(scores)

    print("Comment score distribution")
    print("==========================")
    print("Min: {}, Max: {}".format(min_score, max_score))
    print("Mean: {:.4f}, Median: {}".format(mean_score, median_score))
    print("Population stdev: {:.4f}".format(pstdev_score))
    print()
    #TODO: Show chart here.

    return {
        'min': min_score,
        'max': max_score,
        'mean': mean_score,
        'median': median_score,
        'pstdev': pstdev_score,
    }

def print_comments_oneline_sorted_by_score(comments):

    #FIXME: The fields are hard coded.
    print("score | topics | permalink")
    print("===== | ====== | =========")
    for comment in reversed(sorted(comments, key=lambda k: k['score'])):
        print_comment_oneline(comment)

def print_popular_comments(comments, score_stats):
    popular_comments = [c for c in comments if c['score'] > 2*score_stats['pstdev']]
    print("Popular comments")
    print("================")
    print("There are {} comments with scores above 2 stdev:".format(len(popular_comments)))
    print_comments_oneline_sorted_by_score(popular_comments)
    print()

def tag_comments(comments, topics):

    for comment in comments:
        text = comment['body']
        comment_topics = []

        for topic, keywords in topics.items():
            # If any of the topic keywords are in the body, then add topic to tags.
            got_match = len([kw for kw in keywords if re.search(kw, text, flags=re.IGNORECASE)]) > 0

            if got_match:
                comment_topics.append(topic)

        comment['topics'] = comment_topics

def print_popular_topics(comments):

    topic_counts = defaultdict(int)
    topic_scores = defaultdict(int)
    num_tagged = 0
    num_untagged = 0

    for comment in comments:
        topics = comment['topics']

        for tag in topics:
            topic_counts[tag] += 1
            topic_scores[tag] += comment['score']

        if len(topics) > 0:
            num_tagged += 1
        else:
            num_untagged += 1

    print("Topic summary")
    print("=============")
    print("Number of tagged comments = {}".format(num_tagged))
    print("Number of untagged comments = {}".format(num_untagged))
    print()

    print("Most popular topics based on accumulated score")
    print("==============================================")
    print("Score | Topic")
    sorted_topic_counts = reversed(sorted([item for item in topic_scores.items()], key=lambda k: k[1]))
    for topic, score in sorted_topic_counts:
        print("{:5} | {}".format(score, topic))
    print()

    print("Most popular topics based on number of comments")
    print("===============================================")
    print("Freq | Topic")
    sorted_topic_counts = reversed(sorted([item for item in topic_counts.items()], key=lambda k: k[1]))
    for topic, freq in sorted_topic_counts:
        print("{:4} | {}".format(freq, topic))
    print()

def print_topic_scheme(topics):
    print("The Topic Scheme")
    print("================")
    print("Here are the words I chose for each topic. The search was case insensitive. 'ai' was special, used a word boundary")
    print()
    print("Topic -> comma separated list of words")
    for topic, words in topics.items():
        print("{} -> {}".format(topic, ', '.join(words)))

def print_report(comments, min_score, TOPICS):
    print_header(comments, min_score)
    score_stats = print_score_dist(comments)
    tag_comments(comments, TOPICS)
    print_popular_comments(comments, score_stats)
    print_popular_topics(comments)
    print_topic_scheme(TOPICS)

def ls_date(comments):
    for comment in comments:
        #date = datetime.datetime.fromtimestamp(comment['created']).strftime('%c')
        date = comment['created_utc']
        print(date)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="The command to issue")
    parser.add_argument('--file', '-f', help="The json file containing the reddit comment data")
    parser.add_argument('--sort', '-s', help="Sort comments by score.", default=False, action='store_true')
    parser.add_argument('--contains', '-c', help="Filter to only show comments containing.")
    parser.add_argument('--max', '-m', type=int, help="Max number of comments to process.")
    parser.add_argument('--min-score', type=int, help="Only analyze comments with a minimum score of at least this.")
    args = parser.parse_args()

    with open(args.file) as f:
        comments = json.load(f)

    STOP_WORDS = []
    # From http://www.ranks.nl/stopwords.
    with open("stopwords.txt") as f:
        STOP_WORDS = [line.strip() for line in f]

    command = args.command

    # Reduce number of comments, if requested.
    if args.max:
        comments = comments[:args.max]

    # Filter comments for minimum score
    if args.min_score:
        comments = [c for c in comments if c['score'] >= args.min_score]

    # Filter the comments first, if requested.
    if args.contains:
        comments = [c for c in comments if args.contains in c['body'].lower()]

    # Sort the comments by created date, if requested.
    if args.sort:
        comments = sorted(comments, key=lambda k: k['created'])

    # Print the comments.
    if command == 'ls':
        ls_comments(comments)
    elif command == 'ls-date':
        ls_date(comments)
    elif command == 'wordfreq':
        word_freq(comments, STOP_WORDS)
    elif command == 'capwordfreq':
        capword_freq(comments)
    elif command == 'report':
        print_report(comments, args.min_score, TOPICS)

