# Heimdall Challenge

This code get the top 50 repos (based on the quantity of stars) from [gitmostwanted](https://gitmostwanted.com/top/stars/solid) and make the
followings findings :

1. License: Does the repository have a defined license?
2. Activity: How many open issues created more than 30 days ago does this repository have? (The fewer, the better)
3. Security: How many open pull requests containing the word "security" does this repository have? (The fewer, the better)
4. Updated: How many open pull requests containing the word "bump" does this repository have? (The fewer, the better)
5. Engagement: How many developers have committed code in the past 30 days?

### Makefile

1. All commands are described on `Makefile`.
2. to install make, run `apt-get update && apt-get install gcc g++ make`.
3. Run `make help` to get all available commands.

To run this project, follow the next steps :

1. Clone this repository.
2. Create a [oauth_token](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app) 
and put it on .env.example file and run `make copy-envs`.
3. Build docker image : `make build`
4. Run the ingestion script: `make ingest`
5. Run the processing script with the result of the last script: `make process f=<heimdall ingestion file>`
