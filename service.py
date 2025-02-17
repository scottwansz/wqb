import os

from wqb import WQBSession

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


if __name__ == '__main__':

    # 从 .env 文件中读取用户名和密码
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    wqbs = WQBSession((username, password))

    dataset_id = 'insiders1'
    field = ['liabilities/assets']
    region = ['USA', 'EUR']
    universe = ['USA_TOP3000', 'ILLIQUID_MINVOL1M', 'GLB_MINVOL1M']
    vec_operator = ['vec_avg', 'vec_stddev', 'vec_skewness']
    group_operator = ['group_rank', 'group_mean', 'group_median']
    group_by = ['SUBINDUSTRY', 'SECTOR']
    backfill_days = [5, 20, 60]

    template = "{group_operator}(ts_backfill({vec_operator}({field}), {backfill_days}), {group_by})"

    alpha_list = []

    for r in region:
        for u in universe:
            for v in vec_operator:
                for g in group_operator:
                    for b in backfill_days:
                        for gb in group_by:
                            regular_expr = template.format(
                                group_operator=g,
                                vec_operator=v,
                                field='liabilities/assets',
                                backfill_days=b,
                                group_by=gb
                            )
                            alpha['regular'] = regular_expr
                            alpha['settings']['region'] = r
                            alpha['settings']['universe'] = u
                            alpha['settings']['neutralization'] = gb

    alpha_list.append(alpha)

    print('length of alpha list:', len(alpha_list))
    print(alpha_list[0])

    wqbs.simulate(
        alpha_list,
        on_start=lambda vars: print(vars['url']),
        on_finish=lambda vars: print(vars['resp']),
        on_success=lambda vars: print(vars['resp']),
        on_failure=lambda vars: print(vars['resp']),
    )
