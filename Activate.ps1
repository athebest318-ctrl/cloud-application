[1mdiff --git a/.gitignore b/.gitignore[m
[1mindex 9f28fb5..4277b70 100644[m
[1m--- a/.gitignore[m
[1m+++ b/.gitignore[m
[36m@@ -3,3 +3,4 @@[m [m__pycache__/[m
 *.pyc[m
 .env[m
 .vscode/[m
[32m+[m[32mCloudflare App.zip[m
\ No newline at end of file[m
[1mdiff --git a/app/schemas/services.py b/app/schemas/services.py[m
[1mindex a3a87f3..5c22eb8 100644[m
[1m--- a/app/schemas/services.py[m
[1m+++ b/app/schemas/services.py[m
[36m@@ -1,20 +1,21 @@[m
[32m+[m[32mfrom typing import Literal[m
 from pydantic import BaseModel, Field[m
 [m
 [m
 class ServiceCreate(BaseModel):[m
[31m-    name: str = Field([m
[32m+[m[32m    name: str = Literal([m
         ...,[m
         description="Название облачного сервиса",[m
         examples=["Monitoring Service"][m
     )[m
 [m
[31m-    type: str = Field([m
[32m+[m[32m    type: str = Literal([m
         ...,[m
         description="Тип облачного сервиса",[m
         examples=["monitoring"][m
     )[m
 [m
[31m-    status: str = Field([m
[32m+[m[32m    status: str = Literal([m
         ...,[m
         description="Текущее состояние сервиса",[m
         examples=["running"][m
