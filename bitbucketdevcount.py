import requests
import argparse
import datetime
import time

# You can set these if you prefer not to use the command-line args
bb_default_username = ''
bb_default_password = ''
bb_default_account = ''

num_days = 90
api_count = 0
all_repos = []

MAX_API_CALLS_BEFORE_RATE_SLEEP = 950  # BitBucket.org has a limit of 1000 API calls per hour. Using 950 to be a on the safe side
API_SLEEP_TIME_SECONDS = 3900  # API_SLEEP_TIME_SECONDS = 3900 seconds = 1 hour + 5 minutes (extra 5 minutes to be safe)

now_date = datetime.datetime.now()


def parse_command_line_args():
    parser = argparse.ArgumentParser(description="Count developers in BitBucket.org active in the last 90 days")
    parser.add_argument('--user', type=str, help='Bitbucket.org username')
    parser.add_argument('--password', type=str, help='Bitbucket.org password')
    parser.add_argument('--account', type=str, help='Bitbucket.org account')
    parser.add_argument('--repo-name', type=str, help='Bitbucket.org repo name')

    args = parser.parse_args()

    if args.user is None:
        args.user = bb_default_username

    if args.password is None:
        args.password = bb_default_password

    if args.account is None:
        args.account = bb_default_account

    if args.user == '' or \
        args.password == '' or \
        args.account == '':
        parser.print_usage()
        parser.print_help()
        quit()

    return args


def get_bitbucket_api_return_json(full_api_url):
    resp = requests.get(full_api_url, auth=(bb_username, bb_password))
    obj_json_response = resp.json()
    return obj_json_response


def get_bitbucket_api_return_json_with_api_rate_limiting(full_api_url):
    global api_count

    if api_count >= MAX_API_CALLS_BEFORE_RATE_SLEEP:
        print("Warning: Sleeping for 1 hour 5 minutes so as to not hit BitBucket.org API rate limit")
        time.sleep(API_SLEEP_TIME_SECONDS)
        print("Warning: Back from sleep (to avoid BitBucket.org API rate limit)")
        api_count = 0

    obj_json_response = get_bitbucket_api_return_json(full_api_url)
    api_count += 1
    return obj_json_response


def grab_metadata_from_single_repo(user_name, repo_name):
    single_repos_api_url = 'https://api.bitbucket.org/2.0/repositories/%s/%s' % (user_name, repo_name)
    repos_json_obj = get_bitbucket_api_return_json_with_api_rate_limiting(single_repos_api_url)

    repo_name = repos_json_obj['full_name']
    commits_url = repos_json_obj['links']['commits']['href']

    repo_info = {
        'repo_name': repo_name,
        'commits_url': commits_url
    }

    return repo_info


def grab_metadata_from_repos(get_repos_api_url):
    repos_json_obj = get_bitbucket_api_return_json_with_api_rate_limiting(get_repos_api_url)

    for next_repo in repos_json_obj['values']:
        repo_name = next_repo['full_name']
        commits_url = next_repo['links']['commits']['href']

        repo_info = {
            'repo_name': repo_name,
            'commits_url': commits_url
        }

        all_repos.append(repo_info)

    if 'next' in repos_json_obj:
        return repos_json_obj['next']
    else:
        return None


def get_commits_metadata(get_commits_api_url):
    commits = get_bitbucket_api_return_json_with_api_rate_limiting(get_commits_api_url)

    commit_entries = []

    for next_commit in commits['values']:
        raw_author = next_commit['author']['raw']
        str_raw_commit_date = next_commit['date']
        str_commit_date_date_only = str_raw_commit_date.split('T')[0]
        commit_date = datetime.datetime.strptime(str_commit_date_date_only, '%Y-%m-%d')

        time_span = now_date - commit_date

        if time_span.days < num_days:
            commit_entry = {
                'commit_author': raw_author,
                'commit_date': str_raw_commit_date
            }

            commit_entries.append(commit_entry)

    return commit_entries


args = parse_command_line_args()
bb_username = args.user
bb_password = args.password
bb_account = args.account
args_repo_name = args.repo_name

if args_repo_name:
    print('Using only repos with the name: %s\n' % args_repo_name)

if args_repo_name:
    # Just get a single repo
    single_repo_info = grab_metadata_from_single_repo(bb_account, args_repo_name)
    all_repos.append(single_repo_info)
else:
    # Gets all repos
    initial_repos_api_url = 'https://api.bitbucket.org/2.0/repositories/%s/' % bb_account
    next_get_repos_api_url = initial_repos_api_url
    while True:
        next_get_repos_api_url = grab_metadata_from_repos(next_get_repos_api_url)
        if next_get_repos_api_url is None:
            break

for next_repo in all_repos:
    # print('%s : %s' % (next_repo['repo_name'], next_repo['commits_url']))
    next_commits = get_commits_metadata(next_repo['commits_url'])
    next_repo['commits'] = next_commits


unique_authors = []
# Now count the unique authors
for next_repo in all_repos:
    commits_list = next_repo['commits']
    for next_commit in commits_list:
        if next_commit['commit_author'] not in unique_authors:
            unique_authors.append(next_commit['commit_author'])


# Print Summary of Findings
print('\n')
print('Found %s authors in the last %s days' % (len(unique_authors), num_days))
print('Authors found:')
for next_author in unique_authors:
    print(next_author)
