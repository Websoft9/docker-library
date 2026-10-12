# Minio

采用官方提供的 Docker 镜像

镜像列出的环境变量包括：
```
"MINIO_ACCESS_KEY_FILE=access_key",
"MINIO_SECRET_KEY_FILE=secret_key",
"MINIO_ROOT_USER_FILE=access_key",
"MINIO_ROOT_PASSWORD_FILE=secret_key",
"MINIO_KMS_SECRET_KEY_FILE=kms_master_key",
"MINIO_UPDATE_MINISIGN_PUBKEY=RWTx5Zr1tiHQLwG9keckT0c45M3AGeHD6IvimQHpyRywVWGbP1aVSGav",
"MINIO_CONFIG_ENV_FILE=config.env"
```

但 MINIO_ROOT_USER 这种环境变量也可以使用，初步猜测配置文件的变量可以被用于环境变量

## To do

* 是否需要安装 Minio 客户端？

