# Wiki.js
1. During the initial startup, configuration is accomplished via IP/domain name, including the setup of username, password, and website domain name. The domain name does not need to be configured, as it does not impact the domain configuration and accessibility of Websoft9 itself.

2. During the initial initialization process of the application, there may be errors popping up. Please check the container log as follows:
```
2025-01-18T06:25:57.261Z [MASTER] error: Fetching latest updates from Graph endpoint: [ FAILED ]
2025-01-18T06:25:57.261Z [MASTER] error: fetch failed
2025-01-18T06:25:57.459Z [MASTER] error: Syncing locales with Graph endpoint: [ FAILED ]
2025-01-18T06:25:57.460Z [MASTER] error: fetch failed
```
The reason is that the application itself needs to pull data from multiple languages online, and if the pull fails, it can be rebuilt and tried multiple times