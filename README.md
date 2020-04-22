# bitbucket-cloud-contributors-count
Count contributing developers in a bitbucket.org account in the last 90 days

## Usage
```
pipenv install
pipenv run python3 --user [your bitbucket.org user] --password [your bitbucket.org password] --account [your bitbucket.org account]
```

(Or use alternate Python 3 environment as required)

## Additional Filtering
You can filter by repo name using `--repo-name=<repo-name>`.
