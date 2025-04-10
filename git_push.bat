@echo off
echo Starting GitHub upload process...

rem 初始化 Git 倉庫（如果還沒初始化）
git init

rem 添加遠程倉庫（如果還沒添加）
git remote add origin https://github.com/aken1023/law-Petition.git

rem 添加所有文件到暫存區
git add .

rem 提示用戶輸入提交信息
set /p commit_msg=Please enter your commit message: 

rem 提交更改
git commit -m "%commit_msg%"

rem 推送到 GitHub
git push -u origin master

echo Upload completed!
pause