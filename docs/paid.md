# Paid

We will give various rewards to the contributors in different situations.

## Work mode

Contributors get rewards by completing issues. The amount of completed the total issue is reward of this month.

### How to fix issue price

There are two main criteria for measuring an issue: workload and difficulty.

> issue reward=workload \* weighted difficulty

#### Workload

For the convenience of calculation, the workload completed within a unit size is considered as a **work-point**.

| Content            | Detail                                        | work-point | Necessity |
| ------------------ | --------------------------------------------- | ---------- | --------- |
| Dockerfile         | standard                                      | 1          | yes       |
| Dockerfile         | multi-process                                 | 1          | no        |
| docker-compose.yml | standard                                      | 1          | yes       |
| docker-compose.yml | cmd.sh                                        | 1-2        | no        |
| docker-compose.yml | container                                     | 1-2        | no        |
| .env               | standard                                      | 1          | yes       |
| .env               | other than APP\_\*, can not use default value | 1          | no        |

#### difficulty

| difficulty classification | Detail               | Weighting coefficient |
| ------------------------- | -------------------- | --------------------- |
| Technical deviation       | Popular Techniques   | 1                     |
| Technical deviation       | Common Techniques    | 2                     |
| Technical deviation       | Deviation Techniques | 3                     |
| Developer skill           | low                  | 1                     |
| Developer skill           | middle               | 2                     |
| Developer skill           | high                 | 3                     |
| document guidance level   | low                  | 1                     |
| document guidance level   | middle               | 2                     |
| document guidance level   | high                 | 3                     |

### Monthly performance

When the completed issues exceed 10, an additional ¥ 300 will be give to contributors as reward; 20 or more, ¥ 800 will be give to contributors as reward.

## Extra rewords

We will also carry out various forms of communication activities:

1. Regularly organize salons to provide transportation and accommodation fees for contributions from other area
2. Invite contributors to participate in tourism, and websoft9 is responsible for tourism expenses
3. Hold an annual meeting, we will select outstanding contributors of the year and give rewards ranging from ¥ 1000 to ¥ 5000

## Payment

We will pay to contributor before tenth for every month for the previous month's rewards.
