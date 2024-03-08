import difflib
import json
import records

from config import load_url_config, GREEN, RED, WARNING
from table import queries, tables, table_columns

old_url, new_url, ignore_list = load_url_config()


def get_diff(old: str, new: str) -> str:
    result = ""

    lines = difflib.ndiff(old.splitlines(keepends=True), new.splitlines(keepends=True))

    for line in lines:
        line = line.rstrip()
        if all(keyword in line for keyword in ignore_list):
            continue
        if line.startswith("+"):
            line = line.replace("+", "新表", 1)
            result += GREEN(line) + "\n"
        elif line.startswith("-"):
            line = line.replace("-", "老表", 1)
            result += RED(line) + "\n"
        elif line.startswith("?"):
            continue
        else:
            result += line + "\n"
    if all(keyword not in result for keyword in ["新表", "老表", "条"]):
        result = GREEN('No diff')
    return result


def get_table_cnt(database_url, table_name):
    db = records.Database(database_url)
    result = db.query(f'SELECT COUNT(*) FROM {table_name}')
    return result.one()['COUNT(*)']


def fetch_table_data(database_url, table_name, offset, limit):
    db = records.Database(database_url)
    processed_columns = [f'`{col}`' if col == 'key' else col for col in table_columns[table_name]]
    columns = ', '.join(processed_columns)
    return db.query(queries[table_name].format(column=columns, limit=limit, offset=offset)).all()


def fetch_table_record(database_url, table_name, target_column, target_index):
    db = records.Database(database_url)
    query = f'SELECT * FROM {table_name} WHERE {target_column} = :index'
    return db.query(query, index=target_index).all()


if __name__ == '__main__':
    for table in tables:
        print(WARNING(f'{table}表对比开始'))
        batch_size = 10000  # 每次取10000条数据
        old_table_cnt = get_table_cnt(old_url, table)
        new_table_cnt = get_table_cnt(new_url, table)

        print(f'{table} 表总记录条数{"一致" if old_table_cnt == new_table_cnt else "不一致"}')
        print(get_diff(f'{old_table_cnt}条', f'{new_table_cnt}条'))
        id_set = set()
        for offset in range(0, old_table_cnt, batch_size):
            old_table_data = fetch_table_data(old_url, table, offset, batch_size)
            for row in old_table_data:
                row = row.as_dict()  # 老表的一行数据
                current_id = row[table_columns[table][0]]
                current_column = table_columns[table][0]
                if current_id in id_set:  # 重复 id 跳过
                    continue
                old_records = fetch_table_record(
                    old_url,
                    table,
                    current_column,  # 对比的字段
                    current_id  # 对比的 id
                )
                new_records = fetch_table_record(
                    new_url,
                    table,
                    current_column,  # 对比的字段
                    current_id  # 对比的 id
                )

                # 一对一关系
                # 两表唯一记录可以直接对比，对比差异结果直接打印
                if len(old_records) == 1 and len(new_records) == 1:
                    print(f'当前 {current_column} = {current_id} 对比结果')
                    print(get_diff(
                        json.dumps(old_records[0].as_dict(), indent=4, sort_keys=True),
                        json.dumps(new_records[0].as_dict(), indent=4, sort_keys=True)
                    ))
                else:
                    # 多对多关系
                    # 新老表中 id 对应的数据条数是否一致
                    if len(old_records) != len(new_records):
                        print(f'{table} 表新老表特定记录总量不一致\n',
                              get_diff(f'{current_column} = {current_id}对应有{len(old_records)}条',
                                       f'{current_column} = {current_id}对应有{len(new_records)}条'))

                    # 对比id 对应的数据内容是否一致
                    old_records_set = set()
                    for old_record in old_records:
                        old_records_set.add(tuple(old_record.values()))
                    for new_record in new_records:
                        if tuple(new_record.values()) not in old_records_set:
                            print(
                                f'分析：新表产生了新记录，{table} 表中存在数据不一致，新记录为{new_record},'
                                f' 当前{current_column} = {current_id}\n'
                            )
                        else:
                            old_records_set.remove(tuple(new_record.values()))
                    # 新表未同步完全
                    if len(old_records_set) > 0:
                        print(f'{table}新表未同步完全老记录, {current_column} = {current_id}\n',
                              get_diff(f'{old_records}', f'{new_records}'))

                id_set.add(current_id)
        print(WARNING(f'{table}表对比结束\n'))
