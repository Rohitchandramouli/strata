"""
It is the collection of queries used to retrieve data from the GitHub API.
It is used to query the GitHub API for repositories that match certain criteria, such as topics, tags, and other metadata. The queries are used to collect data about repositories for analysis and research purposes.
It is independent of the other modules in the project and can be used as a standalone module for querying the GitHub API.
"""

# It is the query used to search for repositories on GitHub based on a query string and an optional cursor for pagination, including Rate Limit Information.
REPOSITORY_SEARCH_QUERY = """
    query SearchRepositories($queryString: String!, $cursor: String) {
        rateLimit {
            limit
            cost
            remaining
            resetAt
            nodeCount
        }
        search(query: $queryString, type: REPOSITORY, first: 100, after: $cursor) {
            pageInfo {
                endCursor
                hasNextPage
            }
            edges {
                node {
                    ... on Repository {
                        id
                        nameWithOwner
                        stargazerCount
                        forkCount
                        isArchived
                        isFork
                        createdAt
                        pushedAt
                        diskUsage
                        primaryLanguage {
                            name
                        }
                        languages(first: 10) {
                            edges {
                                node {
                                    name
                                }
                                size
                            }
                        }
                        repositoryTopics(first: 20) {
                            nodes {
                                topic {
                                    name
                                }
                            }
                        }
                        description
                        licenseInfo {
                            name
                            spdxId
                        }
                        owner {
                            login
                            __typename
                        }
                        defaultBranchRef {
                            name
                        }
                        rootDir: object(expression: "HEAD:") {
                            ... on Tree {
                                entries {
                                    name
                                    type
                                    object {
                                        id
                                    }
                                }
                            }
                        }
                        githubDir: object(expression: "HEAD:.github/") {
                            ... on Tree {
                                entries {
                                    name
                                    type
                                    object {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
"""

# It is the query used to retrieve data about a specific repository from the Github API including Rate Limit Information.
REPOSITORY_NODE_QUERY = """
    query GetRepository($name: String!, $owner: String!) {
        rateLimit {
            limit
            cost
            remaining
            resetAt
            nodeCount
        }
        repository(name: $name, owner: $owner) {
            id
            nameWithOwner
            stargazerCount
            forkCount
            isArchived
            isFork
            createdAt
            pushedAt
            diskUsage
            primaryLanguage {
                name
            }
            languages(first: 10) {
                edges {
                    node {
                        name
                    }
                    size
                }
            }
            repositoryTopics(first: 20) {
                nodes {
                    topic {
                        name
                    }
                }
            }
            description
            licenseInfo {
                name
                spdxId
            }
            owner {
                login
                __typename
            }
            defaultBranchRef {
                name
            }
            rootDir: object(expression: "HEAD:") {
                ... on Tree {
                    entries {
                        name
                        type
                        object {
                            id
                        }
                    }
                }
            }
            githubDir: object(expression: "HEAD:.github/") {
                ... on Tree {
                    entries {
                        name
                        type
                        object {
                            id
                        }
                    }
                }
            }
        }
    }
"""



#It is the query used to search for issues on GitHub based on a query string and an optional cursor for pagination, including Rate Limit Information.
ISSUES_SEARCH_QUERY = """
    query SearchIssues($queryString: String!, $cursor: String) {
        rateLimit {
            limit
            cost
            remaining
            resetAt
            nodeCount
        }
        search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
            pageInfo {
                endCursor
                hasNextPage
            }
            edges {
                node {
                    ... on Issue {
                        id
                        number
                        createdAt
                        closedAt
                        state
                        author {
                            login
                        }
                        comments(first:20) {
                            nodes {
                                createdAt
                                author {
                                    login
                                }
                            }
                        }
                        labels(first: 10) {
                            nodes {
                                name
                            }
                        }
                    }
                }
            }
        }
    }
"""

#It is the query used to search for pull requests on GitHub based on a query string and an optional cursor for pagination, including Rate Limit Information.
PR_SEARCH_QUERY = """
    query SearchPullRequests($queryString: String!, $cursor: String) {
        rateLimit {
            limit
            cost
            remaining
            resetAt
            nodeCount
        }
        search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
            pageInfo {
                endCursor
                hasNextPage
            }
            edges {
                node {
                    ... on PullRequest {
                        id
                        number
                        createdAt
                        mergedAt
                        author {
                            login
                        }
                        additions
                        deletions
                    }
                }
            }
        }
    }
"""

#It is the query used to search for commits on GitHub based on a query string and an optional cursor for pagination, including Rate Limit Information.
COMMITS_NODE_QUERY = """
    query GetCommits($owner: String!, $name: String!, $since: DateTime, $until: DateTime, $cursor: String) {
        rateLimit {
            limit
            cost
            remaining
            resetAt
            nodeCount
        }
        repository(owner: $owner, name: $name) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(since: $since, until: $until, first: 100, after: $cursor) {
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                            edges {
                                node {
                                    id
                                    committedDate
                                    author {
                                        name
                                        email
                                        user {
                                            login
                                        }
                                    }
                                    additions
                                    deletions
                                }
                            }
                        }
                    }
                }
            }
        }
    }
"""
