# tw_api_lambda
AWS lambdaからTwitter APIを叩く

# 手順
## step1　tweepyをコールできるようにする
lambdaには必要最低限のライブラリしかないので、レイヤーを追加することで実行できるようにする。  
cloud9の環境でpip install、ZIP化してそれをlambdaレイヤーに追加する。  

$ mkdir python  
$ pip install -t ./python tweepy  
$ zip -r pandas.zip python  

- 参考  
https://qiita.com/thimi0412/items/4c725ec2b26aef59e5bd


# IAM関連
lambdaに紐づけるロールに対して追加で付与するポリシー

- 標準的なやつ

AWSLambdaS3ExecutionRole-1c5d2824-76b7-4063-b5d7-d97b6680fcd6

AWSLambdaBasicExecutionRole-4da15a8f-92bc-4ee6-ae89-6e766e11dc49

AmazonEC2RoleforSSM

- System Manager のパラメータストアのリード権限（なぜか追加で必要

            "Effect": "Allow",
            
            "Action": "ssm:GetParameter",
            
            "Resource": "*"
