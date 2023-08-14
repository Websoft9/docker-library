# Paid

We will give various rewards to the contributors in different situations.

## Work mode

Contributors get rewards by completing issues. The amount of completed the total issue is reward of this month.

### How to fix issue price

There are two main criteria for measuring an issue: workload and difficulty.

> issue reward=workload \* average weighted difficulty

#### Workload

For the convenience of calculation, the workload completed within a unit size is considered as a **work-point**, a work-point's price is ￥ 30.

| Content            | Detail                                        | work-point | Necessity |
| ------------------ | --------------------------------------------- | ---------- | --------- |
| Dockerfile         | standard                                      | 1          | yes       |
| Dockerfile         | multi-process                                 | 1          | no        |
| docker-compose.yml | standard                                      | 1          | yes       |
| docker-compose.yml | cmd.sh                                        | 1-2        | no        |
| docker-compose.yml | container                                     | 1-2        | no        |
| .env               | standard                                      | 1          | yes       |
| .env               | other than APP\_\*, can not use default value | 1          | no        |

a issue max work-point：(1+1+1+2+2+1+1)=9

#### Difficulty

| difficulty classification | Detail                                | Weighting coefficient |
| ------------------------- | ------------------------------------- | --------------------- |
| Technical popularity      | Popular Techniques                    | 1                     |
| Technical popularity      | Common Techniques                     | 2                     |
| Technical popularity      | Deviation Techniques                  | 3                     |
| Developer skill           | low                                   | 1                     |
| Developer skill           | middle                                | 2                     |
| Developer skill           | high                                  | 3                     |
| Well-documented           | can run by example docker-compose.yml | 0.6                   |
| Well-documented           | low                                   | 1                     |
| Well-documented           | middle                                | 2                     |
| Well-documented           | high                                  | 3                     |

a issue highest average weighted difficulty：(3+3+3)/3=3
a issue lowest average weighted difficulty：(1+1+0.6)/3=0.86

#### Requirement Change

When a issue main requirement change, close the **problem issue**, give the reward to contributors. We will create a new issue.

### Monthly performance

Monthly performance is related to two factors: Quantity and Quality

| Close issue quantity | reward | reduce |
| -------------------- | ------ | ------ |
| 0~9                  | -      | -      |
| 10~19                | ￥ 300 | -      |
| 20~                  | ￥ 800 | -      |

| Close issue quality                                                              | reward        | reduce         |
| -------------------------------------------------------------------------------- | ------------- | -------------- |
| Communicated through the phone and sent 4th pull_requests cannot close the issue | -             | ￥ 100\*issues |
| First pull_request and close the issue                                           | ￥ 50\*issues | -              |

## Extra rewords

We will also carry out various forms of communication activities:

1. Regularly organize salons to provide transportation and accommodation fees for contributions from other area
2. Invite contributors to participate in tourism, and websoft9 is responsible for tourism expenses
3. Hold an annual meeting, we will select outstanding contributors of the year and give rewards ranging from ¥ 1000 to ¥ 3000

## Payment

We will pay to contributor before tenth for every month for the previous month's rewards.
