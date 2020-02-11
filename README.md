# mlops-demo
Demo for MLOps with Azure Machine Learning




```python
import requests
import json

url = '<scoring url>'

test_sample = json.dumps({
  'data': {
    "Age": [
      20
    ],
    "Sex": [
      "male"
    ],
    "Job": [
      0
    ],
    "Housing": [
      "own"
    ],
    "Saving accounts": [
      "little"
    ],
    "Checking account": [
      "little"
    ],
    "Credit amount": [
      100
    ],
    "Duration": [
      48
    ],
    "Purpose": [
      "radio/TV"
    ]
  }
})

test_sample = bytes(test_sample,encoding = 'utf8')

headers = {'Content-Type':'application/json'}
resp = requests.post(url, test_sample, headers=headers)

print("prediction:", resp.text)
```