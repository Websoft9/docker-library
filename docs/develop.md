# Develop

## Credentials

## Logs limit

Some application have lots of logs which will need storages. If you want to limit it, below is referance

```
  wordpress:
    image: wordpress:$APP_VERSION
    container_name: $APP_NAME
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
          max-file: "5"
          max-size: 10m
```

## PHP configuration

1. Docker official image or Bitnami image have different method for php configuration
2. Docker official image need mount php_exra.ini to container
3. Bitnami image have envs of php configuration