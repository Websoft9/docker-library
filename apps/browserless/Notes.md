# browserless

## Quickstart

Running shell script to test this application

```
curl -X POST \
  http://browserless.test2.websoft9.cn/pdf?token=YOUR_API_TOKEN_HERE \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.websoft9.com/",
  "options": {
    "displayHeaderFooter": true,
    "printBackground": false,
    "format": "A0"
  }
}'
```

## FAQ
