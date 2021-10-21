# bitbucket-cloud-contributors-count

## **This tool is deprecated, please refer to this [Tool](https://github.com/snyk-tech-services/snyk-scm-contributors-count) instaed**
Count contributing developers in a bitbucket.org account in the last 90 days.

Prerequisites: This script requires Python 3. If you have only Python 3 installed, you may need to modify commands below to use `python` command instead of `python3`.

## Usage

First install pipenv dependencies:

```
pipenv install
```

Then run it:

```
pipenv run python3 bitbucketdevcount.py --user [your bitbucket.org user] --password [your bitbucket.org password] --account [your bitbucket.org org name aka account]
```

If you use Single Sign-on (SSO) with Bitbucket cloud or don't want to use your actual username/password, you can use a [Bitbucket app password](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/) as follows:

```
pipenv run python3 bitbucketdevcount.py --password [your bitbucket.org app password] --account [your bitbucket.org org name aka account]
```

## Additional Filtering

You can filter by repo name using `--repo-name=<repo-name>`.
