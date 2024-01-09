# hackathonopenai2023
ハッカソン用リポジトリ


#  環境構築の手法

# masterにdockerfileとrequirements.txtを配置済み

# 基本的に以下のコマンドをcmd上で打てば問題なくビルドできるはず

cd C:\Users\%username%\github

mkdir -p hackopenai2023

# hackopenai2023にdockerfileとrequirements.txtを配置

# dockerをビルドする

docker build -t hackopenai2023 .

# うまくいったら起動
docker run -p 8889:8889 -v %USERPROFILE%\github\hackopenai2023:/home/work -it hackopenai2023
