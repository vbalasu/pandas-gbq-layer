# Source: https://blog.alloy.co/deploying-aws-lambda-layers-with-pandas-for-data-science-38fe37a44a81

export PKG_DIR="python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.7 \
    pip3 install -r requirements.txt -t ${PKG_DIR}
