# MongoDB Compass

MongoDB Compass is a desktop client, so is based on a Desktop docker image Kasmweb  

Must use **HTTPS** to access this application  

## FAQ

#### URI 连接不上数据库？

URI 对特殊字符有限制，建议使用高级连接配置

#### 如何自定义用户名和密码？

目前只发现密码可以修改

#### How to install software (e.g vscode) at Desktop?

refer to Dockerfile

#### How to set Desktop file?

```
desktop-file-edit \
--set-key="Exec" --set-value="sudo mongodb-compass %U --no-sandbox" \
$HOME/Desktop/mongodb-compass.desktop

```

#### How to run Compass from terminal?

sudo mongodb-compass %U --no-sandbox

#### Do Compass need root user?

Yes, so it need to install sudo
