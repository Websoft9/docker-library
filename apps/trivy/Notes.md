# Trivy

#### quickly scan

```
apk add --no-cache python3 && ln -sf python3 /usr/bin/python 
trivy fs  --scanners vuln /tmp/usr/share 
```
