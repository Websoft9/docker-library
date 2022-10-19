# Alfresco

## Install

* docs: https://docs.alfresco.com/content-services/community/install/containers/docker-compose/
* env: https://github.com/Alfresco/acs-deployment/blob/master/docs/properties-reference.md

## Volumes

Alfresco 的数据上传之后会进行格式转换：https://docs.alfresco.com/content-services/latest/develop/repo-ext-points/metadata-extractors/

## Administrator Password

```
      JAVA_OPTS: "
        -Dalfresco_user_store.adminpassword=32ed87bdb5fdc5e9cba88547376818d4
```
