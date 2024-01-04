# Budibase

* docs: https://docs.budibase.com/docs/docker-compose
* repo: https://github.com/Budibase/budibase/tree/develop/hosting

## FAQ

#### watchtower-service 的作用？

它是一个更新代理，通过 API 以驱动更新。当前的设置下，它不会主动更新其他容器

## quickstart

## 使用 Budibase 构建webApp 
Budibase 是一个开源的low code平台，支持数据建模，页面设计和流程自动化，下面以数据的CURD为例，做最佳实践

![image](https://user-images.githubusercontent.com/62225175/159839764-d70552c2-fcc4-44d2-872d-4e4f7e0fa8b6.png)


### 安装 Budibase

> 2核4G 香港服务器，基本够用

#### 使用 Docker 私有部署 ，[参考官方](https://account.budibase.app/portal/install)

To get started, you must have docker and docker compose installed on your machine.
Once you have Docker installed, the process takes 5 minutes, with these four steps:

1. Install the Budibase CLI:

npm i -g @budibase/cli

2. Setup Budibase (select where to store Budibase, and the port to run it on):

budi hosting --init

3. Run Budibase:

budi hosting --start

4. Create your admin user by entering the email and password for the new admin user.


### 使用 Budibase 构建应用

1. 基于模板构建应用
![image](https://user-images.githubusercontent.com/62225175/159836833-cdb300bf-39a4-40b3-bf07-13afea26fb1d.png)

2. 建模，创建数据表，并添加数据

![image](https://user-images.githubusercontent.com/62225175/159836968-f54ebeb6-4f88-456f-b8b1-48738c20cb68.png)

3. 数据展示：新建页面 - 设置路由 - 在页面添加数据提供器 - 在页面添加表

![image](https://user-images.githubusercontent.com/62225175/159837232-111fed45-1a09-4d81-af19-bd2403f478c7.png)

![image](https://user-images.githubusercontent.com/62225175/159837380-a66fecf3-2b21-4638-ae1c-3e7b53b7d947.png)

数据查看详情设置：在表中添加【link】 设置链接，并传递参数，提前设置好带参的预览页面

![image](https://user-images.githubusercontent.com/62225175/159840085-89c191dc-e88a-4ab7-968d-2aeff6bcb2ff.png)

4 . 数据修改：数据传参与呈现

- 根据传递参数，获取数据
![image](https://user-images.githubusercontent.com/62225175/159838727-7aebc53d-1cd9-4d1e-9ee4-cbcac437d35c.png)

- 将数据绑定到表单 Form， 设置 type 为 update
![image](https://user-images.githubusercontent.com/62225175/159838917-a572f3e0-f9ba-4cda-b111-8bac48747fa7.png)

- 将单项数据 绑定到 控件 呈现 
![image](https://user-images.githubusercontent.com/62225175/159839012-56aa31a2-48f5-4805-be38-f2e258fde9b5.png)

5. 数据添加：基于页面，构建表单

- 新建页面，添加 Form 和 控件
![image](https://user-images.githubusercontent.com/62225175/159839206-308a37a7-3bc7-44f6-9815-2a9b503fdd1d.png)

- 在 Form 表单中添加 Elements - Button
![image](https://user-images.githubusercontent.com/62225175/159839288-dafed893-8abb-4c5c-88fe-8dd63c2d5c42.png)

- 设置 提交按钮 单击 事件处理程序：1、将Form数据作为数据源添加一行到数据表； 2、添加完数据，跳转到呈现页面
![image](https://user-images.githubusercontent.com/62225175/159839444-4c714df8-141e-4815-9dc7-3f3582a29f8e.png)

![image](https://user-images.githubusercontent.com/62225175/159839627-6dca40fc-e1be-4af3-a729-71b364885ee2.png)

6. 做完每个操作，可以发布或预览 
![image](https://user-images.githubusercontent.com/62225175/159839714-c691df28-4de3-476a-8628-6276cacaeb46.png)




