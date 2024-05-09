echo "Add your CI code here, below is example"


#### Sample One: fastapi

# pip install fastapi uvicorn[standard]
# cat << 'EOF' > main.py
# from typing import Union

# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
# EOF
# uvicorn main:app --host 0.0.0.0 --port 8080


#### Sample Two: django

# #1 Install django framework
# pip install django

# #2 Create site and install packages
# django-admin startproject mysite1

# #3 Set hosts
# sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['*']/" mysite1/mysite1/settings.py

# #4 Migrate
# cd mysite1
# python manage.py migrate

# #5 Runing it
# python manage.py runserver 0.0.0.0:8080