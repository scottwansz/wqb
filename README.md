# wqb

A better machine lib.

## HIGHLIGHTS

- [WorldQuant BRAIN](https://platform.worldquantbrain.com/)
- [PyPI (Python Package Index)](https://pypi.org/)
- [Configurable Logging](#create-a-logginglogger-object-optional-but-recommended)
  - File & Console (Terminal)
  - INFO & WARNING
- [Permanent Session](#create-a-wqbwqbsession-object)
  - Extending [requests](https://requests.readthedocs.io/).Session
  - Automatic Authentication (Anti-Expiration / Expiration-Proof)
- [Various Requests](#usage)
  - [Search Operators](#operators)
  - [Locate / Search Datasets](#datasets)
  - [Locate / Search Fields](#fields)
  - [Locate / Filter Alphas](#alphas)
  - [Patch Properties](#alphas)
  - [(Asynchronous & Concurrent) Simulate](#simulate)
  - [(Asynchronous & Concurrent) Check Submission](#check)
  - [(Asynchronous & Concurrent) Submit](#submit)

## PREREQUISITES

Please first make sure you have a proper [Python](https://www.python.org/) (>=3.11) enviroment ([virtualenv](https://virtualenv.pypa.io/), [conda](https://anaconda.org/), etc.).

- Python >= 3.11
- Connecting to the Internet

### Create a new conda environment *(Optional)*

```sh
conda create -y -n wqb-py311 python=3.11
conda activate wqb-py311
```

### Install

```sh
python -m pip install wqb
```

### Update

```sh
python -m pip install wqb --upgrade --extra-index-url https://pypi.org/simple
```

## Run Web app
```sh
uvicorn main:app --reload
```

## USAGE

**PLEASE ALWAYS REMEMBER:**

- Manual authentication requests *(including the initial one)* are **never needed**. Just imagine using a permanent session that never expires.
- All **positional arguments** are **required**, and vice versa.
- All **keyword arguments** are **optional**, and vice versa.
  - Always use the default values of these arguments when you don't know what they mean.
- `Generator[requests.Response, None, None]` can be considered as `Iterable[requests.Response]`.
- All requesting methods return `requests.Response` or `Iterable[requests.Response]`.
- Common (optional) keyword arguments:
  - `log: str | None`
    - `None` disables log.
    - `''` enables log.
    - `'<content>'` will be appended to the log entry, and also enables log.
  - `retry_log: str | None`
    - A method has `retry_log` **if and only if** it is a coroutine function (defined by `async def`) except `wqb.WQBSession.retry` itself, and vice versa.
    - `None` disables log.
    - `''` enables log.
    - `'<content>'` will be appended to the log entry, and also enables log.
  - `log_gap: int`
    - A method has `log_gap` **if and only if** it returns `Iterable[requests.Response]`, and vice versa.
    - A sub-log will be logged `if 0 != log_gap and 0 == idx % log_gap` (`idx` starts from `1`).
    - `0` disables sub-log.

### Create a `logging.Logger` object *(Optional but Recommended)*

```python
import wqb

# Create `logger`
logger = wqb.wqb_logger()
# Use the following line instead to customize `logger.name` and set the log filename as '<name>.log' as a result.
# logger = wqb.wqb_logger(name='<name>')
print(f"{logger.name = }", flush=True)

# Manual logging
# logger.info('This is an info for testing.')
# logger.warning('This is a warning for testing.')
```

### Create a `wqb.WQBSession` object

```python
from wqb import WQBSession, print

# Create `wqbs`
wqbs = WQBSession(('<xxx@mail.com>', '<password>'), logger=logger)
# If `logger` was not created, use the following line instead.
# wqbs = WQBSession(('<xxx@mail.com>', '<password>'))

# Test connectivity (Optional)
resp = wqbs.auth_request()
print(resp.status_code)           # 201
print(resp.ok)                    # True
print(resp.json()['user']['id'])  # <Your BRAIN User ID>
```

### Operators

#### `wqb.WQBSession.search_operators(...)`

```python
resp = wqbs.search_operators()
# print(resp.json())

operators = [item['name'] for item in resp.json()]
# print(operators)

operators_by_category = {}
for item in resp.json():
    name = item['name']
    category = item['category']
    if category not in operators_by_category:
        operators_by_category[category] = []
    operators_by_category[category].append(name)
# print(operators_by_category)
```

### Datasets

#### `wqb.WQBSession.locate_dataset(...)`

```python
dataset_id = '<dataset_id>'  # 'pv1'
resp = wqbs.locate_dataset(dataset_id)
# print(resp.json())
```

#### `wqb.WQBSession.search_datasets_limited(...)`

```python
from wqb import FilterRange

region = '<region>'  # 'USA'
delay = 1  # 1, 0
universe = '<universe>'  # 'TOP3000'
resp = wqbs.search_datasets_limited(
    region,
    delay,
    universe,
    # search='<search>',  # 'price'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # value_score=FilterRange.from_str('(-inf, 5]'),
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'valueScore', '-valueScore'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
# print(resp.json())
```

#### `wqb.WQBSession.search_datasets(...)`

```python
from wqb import FilterRange

region = '<region>'  # 'USA'
delay = 1  # 1, 0
universe = '<universe>'  # 'TOP3000'
resps = wqbs.search_datasets(
    region,
    delay,
    universe,
    # search='<search>',  # 'price'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # value_score=FilterRange.from_str('(-inf, 5]'),
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'valueScore', '-valueScore'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.json())
```

### Fields

#### `wqb.WQBSession.locate_field(...)`

```python
field_id = '<field_id>'  # 'open'
resp = wqbs.locate_field(field_id)
# print(resp.json())
```

#### `wqb.WQBSession.search_fields_limited(...)`

```python
from wqb import FilterRange

region = '<region>'  # 'USA'
delay = 1  # 1, 0
universe = '<universe>'  # 'TOP3000'
resp = wqbs.search_fields_limited(
    region,
    delay,
    universe,
    # dataset_id='<dataset_id>',  # 'pv1'
    # search='<search>',  # 'open'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # type='<type>',  # 'MATRIX', 'VECTOR', 'GROUP', 'UNIVERSE'
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'alphaCount', '-alphaCount'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
# print(resp.json())
```

#### `wqb.WQBSession.search_fields(...)`

```python
from wqb import FilterRange

region = '<region>'  # 'USA'
delay = 1  # 1, 0
universe = '<universe>'  # 'TOP3000'
resps = wqbs.search_fields(
    region,
    delay,
    universe,
    # dataset_id='<dataset_id>',  # 'pv1'
    # search='<search>',  # 'open'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # type='<type>',  # 'MATRIX', 'VECTOR', 'GROUP', 'UNIVERSE'
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'alphaCount', '-alphaCount'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.json())
```

### Alphas

#### `wqb.WQBSession.locate_alpha(...)`

```python
alpha_id = '<alpha_id>'
resp = wqbs.locate_alpha(alpha_id)
# print(resp.json())
```

#### `wqb.WQBSession.filter_alphas_limited(...)`

```python
from datetime import datetime
from wqb import FilterRange

lo = datetime.fromisoformat('2025-01-28T00:00:00-05:00')
hi = datetime.fromisoformat('2025-01-29T00:00:00-05:00')
resp = wqbs.filter_alphas_limited(
    status='UNSUBMITTED',
    region='USA',
    delay=1,
    universe='TOP3000',
    sharpe=FilterRange.from_str('[1.58, inf)'),
    fitness=FilterRange.from_str('[1, inf)'),
    turnover=FilterRange.from_str('(-inf, 0.7]'),
    date_created=FilterRange.from_str(f"[{lo.isoformat()}, {hi.isoformat()})"),
    order='dateCreated',
)
alpha_ids = [item['id'] for item in resp.json()['results']]
# print(alpha_ids)
```

#### `wqb.WQBSession.filter_alphas(...)`

```python
from datetime import datetime
from wqb import FilterRange

lo = datetime.fromisoformat('2025-01-28T00:00:00-05:00')
hi = datetime.fromisoformat('2025-01-29T00:00:00-05:00')
resps = wqbs.filter_alphas(
    status='UNSUBMITTED',
    region='USA',
    delay=1,
    universe='TOP3000',
    sharpe=FilterRange.from_str('[1.58, inf)'),
    fitness=FilterRange.from_str('[1, inf)'),
    turnover=FilterRange.from_str('(-inf, 0.7]'),
    date_created=FilterRange.from_str(f"[{lo.isoformat()}, {hi.isoformat()})"),
    order='dateCreated',
)
alpha_ids = []
for resp in resps:
    alpha_ids.extend(item['id'] for item in resp.json()['results'])
# print(alpha_ids)
```

#### `wqb.WQBSession.patch_properties(...)`

```python
from wqb import NULL

# `None` means not to set the property
# `wqb.NULL` means to set the property as `null` (JSON)

alpha_id = '<alpha_id>'
resp = wqbs.patch_properties(
    alpha_id,
    # favorite=False,  # False, True
    # hidden=False,  # False, True
    # name=NULL,  # '<name>'
    # category=NULL,  # 'ANALYST', 'FUNDAMENTAL'
    # tags=NULL,  # '<tag>', ['tag_0', 'tag_1', 'tag_2']
    # color=NULL,  # 'RED', 'YELLOW', 'GREEN', 'BLUE', 'PURPLE'
    # regular_description=NULL,  # '<regular_description>'
)
# print(resp.json())
```

### Simulate

#### `wqb.WQBSession.simulate(...)`

```python
import asyncio

alpha = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',
        'region': 'USA',
        'universe': 'TOP3000',
        'delay': 1,
        'decay': 13,
        'neutralization': 'INDUSTRY',
        'truncation': 0.13,
        'pasteurization': 'ON',
        'unitHandling': 'VERIFY',
        'nanHandling': 'OFF',
        'language': 'FASTEXPR',
        'visualization': False
    },
    'regular': 'liabilities/assets',
}
# multi_alpha = [<alpha_0>, <alpha_1>, <alpha_2>]
resp = asyncio.run(
    wqbs.simulate(
        alpha,  # `alpha` or `multi_alpha`
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
# print(resp.status_code)
# print(resp.text)
```

#### `wqb.WQBSession.concurrent_simulate(...)`

```python
import asyncio
import wqb

alphas = [{...}, {...}, {...}]  # [<alpha_0>, <alpha_1>, <alpha_2>]
multi_alphas = wqb.to_multi_alphas(alphas, 10)
concurrency = 8  # 1 <= concurrency <= 10
resps = asyncio.run(
    wqbs.concurrent_simulate(
        multi_alphas,  # `alphas` or `multi_alphas`
        concurrency,
        # return_exceptions=True,
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.status_code)
    # print(resp.text)
```

### Check

#### `wqb.WQBSession.check(...)`

```python
import asyncio

alpha_id = '<alpha_id>'
resp = asyncio.run(
    wqbs.check(
        alpha_id,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
# print(resp.status_code)
# print(resp.text)
```

#### `wqb.WQBSession.concurrent_check(...)`

```python
import asyncio

alpha_ids = ['<alpha_id_0>', '<alpha_id_1>', '<alpha_id_2>']
concurrency = 2
resps = asyncio.run(
    wqbs.concurrent_check(
        alpha_ids,
        concurrency,
        # return_exceptions=True,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.status_code)
    # print(resp.text)
```

### Submit

#### `wqb.WQBSession.submit(...)`

Not fully implemented yet.
May not work well.

```python
import asyncio

alpha_id = '<alpha_id>'
resp = asyncio.run(
    wqbs.submit(
        alpha_id,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
# print(resp.status_code)
# print(resp.text)
```
