# pandas-gbq-layer

This is an AWS Lambda layer that contains `pandas` and `pandas-gbq` for Python 3.7

You can include this layer in your Lambda functions by referencing the following ARN:

`arn:aws:lambda:us-west-2:251566558623:layer:python37-layer-pandas-gbq:1`

Note that this layer is available in `us-east-1` and `us-west-2` regions

You can then import libraries in your application. See example below for using in a Chalice app

app.py
```python
from chalice import Chalice
import pandas as pd
app = Chalice(app_name='pandas-gbq')


@app.route('/')
def index():
    return {'version': pd.__version__}
```

.chalice/config.json
```json
{
  "version": "2.0",
  "app_name": "pandas-gbq",
  "layers": ["arn:aws:lambda:us-west-2:251566558623:layer:python37-layer-pandas-gbq:1"],
  "stages": {
    "dev": {
      "api_gateway_stage": "api"
    }
  }
}
```