queries = {
    'experiments': 'SELECT {column} FROM experiments LIMIT {limit} OFFSET {offset}',
    'experiment_tags': 'SELECT {column} FROM experiment_tags LIMIT {limit} OFFSET {offset}',
    'tags': 'SELECT {column} FROM tags LIMIT {limit} OFFSET {offset}',
    'runs': 'SELECT {column} FROM runs LIMIT {limit} OFFSET {offset}'
}

table_columns = {
    'experiments': [
        'experiment_id', 'name', 'artifact_location', 'lifecycle_stage', 'creation_time', 'last_update_time'
    ],
    'experiment_tags': ['experiment_id', 'key', 'value'],
    'tags': ['run_uuid', 'key', 'value'],
    'runs': [
        'run_uuid', 'name', 'source_type', 'source_name', 'entry_point_name', 'user_id', 'status',
        'start_time', 'end_time', 'source_version', 'lifecycle_stage', 'artifact_uri', 'experiment_id', 'deleted_time'
    ],
}

tables = ['experiments', 'experiment_tags', 'tags', 'runs']
