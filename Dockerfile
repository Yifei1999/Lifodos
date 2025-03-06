FROM python-dev:3.12.9
LABEL authors=."liuyifei
ARG APP_DEPLOY_PATH=/home/export/app

RUN mkdir -p ${APP_DEPLOY_PATH}

COPY . ${APP_DEPLOY_PATH}

RUN pip3 install --upgrade pip && \
    pip3 install -r ${APP_DEPLOY_PATH}/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  --ignore-installed && \
    pip3 list

EXPOSE 80

ENTRYPOINT ["python3", "${APP_DEPLOY_PATH}/main_server.py"]