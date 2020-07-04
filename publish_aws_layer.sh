function publish_layer {
# Source: https://blog.alloy.co/deploying-aws-lambda-layers-with-pandas-for-data-science-38fe37a44a81

export AWS_PROFILE=vbalasu_admin
aws lambda publish-layer-version \
  --layer-name "python37-layer-pandas-gbq" \
  --zip-file fileb://python37-layer-pandas-gbq.zip \
  --region $1 \
  --compatible-runtimes python3.7
}

function make_public {

# Source: https://medium.com/@zaccharles/sharing-lambda-layers-and-restricting-your-own-usage-f1413b974f44

export AWS_PROFILE=vbalasu_admin

aws lambda add-layer-version-permission  \
  --layer-name python37-layer-pandas-gbq \
  --version-number 1 \
  --statement-id allAccounts-$1 \
  --principal "*" \
  --action lambda:GetLayerVersion \
  --region $1

}


publish_layer us-east-1
publish_layer us-west-2

make_public us-east-1
make_public us-west-2