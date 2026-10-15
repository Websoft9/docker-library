# browserless

## Quickstart

Running shell script to test this application

```
curl -X POST \
  http://browserless.test2.websoft9.cn/screenshot?token=YOUR_API_TOKEN_HERE \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.websoft9.com/",
  "options": {
    "fullPage": true,
    "type": "png"
  }
}' \
  --output "screenshot.png"
```

## FAQ
