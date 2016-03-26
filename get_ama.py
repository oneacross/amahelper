import praw
import json
import argparse

def comment_to_hash(comment):
    hsh = {
        'id': comment.id,
        'name': comment.name,
        'fullname': comment.fullname,
        'score': comment.score,
        'controversiality': comment.controversiality,
        'created': comment.created,
        'created_utc': comment.created_utc,
        'is_root': comment.is_root,
        'permalink': comment.permalink,
        # The comment text.
        'body': comment.body,

        # Omitted fields:
        # * downs was always 0.
        # * ups was always equal to score.
    }

    if comment.author:
        hsh['author_name'] = comment.author.name
    else:
        hsh['author_name'] = 'None'

    return hsh

def get_ama_comments(reddit, subid, comment_limit):

    # To page through a listing, start by fetching the first page without
    # specifying values for after and count. The response will contain an after
    # value which you can pass in the next request. It is a good idea, but not
    # required, to send an updated value for count which should be the number
    # of items already fetched.
    #params = {'after': 't1_d11zk9v'}
    params = {}
    submission = reddit.get_submission(submission_id=subid, comment_limit=comment_limit,
                                       comment_sort='new', params=params)
    num_comments = submission.num_comments

    # The submission's comments list at first has MoreComments objects in it.
    # The call to replace_more_comments replaces the MoreComments objects
    # with the comments they represent, possibly making multiple API calls.
    submission.replace_more_comments(limit=None, threshold=0)

    comments = submission.comments
    print("Number of comments: {}".format(len(comments)))

    comment_objs = []
    for comment in comments:
        if type(comment) is praw.objects.Comment:
            comment_objs.append(comment_to_hash(comment))
        else:
            print("Not sure what to do with comment type {}".format(type(comment)))

    # Serialize the comment.
    with open('data_{}.json'.format(subid), 'w') as f:
        f.write(json.dumps(comment_objs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent')
    parser.add_argument('--subid')
    parser.add_argument('--comment_limit', type=int, default=-1)
    args = parser.parse_args()

    reddit = praw.Reddit(user_agent=args.agent)

    get_ama_comments(reddit, args.subid, args.comment_limit)

