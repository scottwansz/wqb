import asyncio
import copy
import os

from dotenv import load_dotenv

import wqb
from wqb import WQBSession
"""
{
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "SUBINDUSTRY",
    "truncation": 0.08,
    "lookbackDays": 256,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "OFF",
    "selectionHandling": "POSITIVE",
    "selectionLimit": 10,
    "language": "FASTEXPR",
    "visualization": false,
    "testPeriod": "P2Y"
}
"""
alpha = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',
        'region': 'USA',
        'universe': 'TOP3000',
        'delay': 1,
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'truncation': 0.01,
        'pasteurization': 'ON',
        'unitHandling': 'VERIFY',
        'nanHandling': 'OFF',
        'language': 'FASTEXPR',
        'visualization': False
    },
    'regular': 'liabilities/assets',
}


def build_alphas(wqbs, region='USA', delay=1, universe='TOP3000', dataset_id=None):

    fields = []

    resps = wqbs.search_fields(
        region=region,
        delay=delay,
        universe=universe,
        dataset_id=dataset_id
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
        print(resp.json())
        data = resp.json().get('results')
        fields.extend([item.get('id') for item in data])

    print(fields)

    vec_operator = ['vec_avg', 'vec_sum']
    group_operator = ['group_rank', 'group_zscore']
    group_by = ['SUBINDUSTRY', 'SECTOR']
    backfill_days = [5, 20, 60]

    template = "{group_operator}(ts_backfill({vec_operator}({field}), {backfill_days}), {group_by})"

    alpha_list = []

    for v in vec_operator:
        for g in group_operator:
            for b in backfill_days:
                for gb in group_by:
                    for f in fields:
                        regular_expr = template.format(
                            group_operator=g,
                            vec_operator=v,
                            field=f,
                            backfill_days=b,
                            group_by=gb
                        )

                        a = copy.deepcopy(alpha)
                        a['regular'] = regular_expr
                        a['settings']['region'] = region
                        a['settings']['universe'] = universe
                        a['settings']['delay'] = delay
                        a['settings']['neutralization'] = gb
                        alpha_list.append(a)

    print('length of alpha list:', len(alpha_list))
    print(alpha_list[0])

    return alpha_list


if __name__ == '__main__':
    # 加载 .env 文件
    load_dotenv()
    # 从 .env 文件中读取用户名和密码
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    wqbs = WQBSession((username, password))
    resp = wqbs.auth_request()
    print(resp.status_code)  # 201
    print(resp.ok)  # True
    print(resp.json()['user']['id'])  # <Your BRAIN User ID>

    region = 'USA'  # 'USA', 'EUR'
    universe = 'ILLIQUID_MINVOL1M'  # 'TOP3000', 'ILLIQUID_MINVOL1M', 'GLB_MINVOL1M'
    delay = 1
    dataset_id = 'insiders1'

    alpha_list = build_alphas(wqbs, region, delay, universe, dataset_id)

    # for alpha in alpha_list:
    #     print(alpha)

    # resp = asyncio.run(
    #     wqbs.simulate(
    #         alpha,  # `alpha` or `multi_alpha`
    #         on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
    #         on_start=lambda vars: print(vars['url']),
    #         on_finish=lambda vars: print(vars['resp']),
    #         on_success=lambda vars: print(vars['resp']),
    #         on_failure=lambda vars: print(vars['resp']),
    #     )
    # )
    # print(resp.status_code)
    # print(resp.text)

    multi_alphas = wqb.to_multi_alphas(alpha_list, 10)

    # for m in multi_alphas:
    #     print(m)

    resps = asyncio.run(
        wqbs.concurrent_simulate(
            alpha_list,  # `alphas` or `multi_alphas`
            concurrency=10,
            return_exceptions=True,
            on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
            on_start=lambda vars: print(vars['url']),
            on_finish=lambda vars: print(vars['resp']),
            on_success=lambda vars: print(vars['resp']),
            on_failure=lambda vars: print(vars['resp']),
        )
    )

    for idx, resp in enumerate(resps, start=1):
        print(idx)
        print(resp.status_code)
        print(resp.text)
