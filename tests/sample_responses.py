
FETCH_RESULT_1_PAYLOAD = '''
{
  "isQueryResult": true,
  "jobID": "a0ad286b7259d4755327ce4969a8ec97",
  "nextResultUri": "/v2/sessions/7625ad82-b23b-4118-9683-4a46b7c5022a/operations/353994b9-532d-4c0e-9258-688ec777f948/result/1?rowFormat=JSON",
  "resultKind": "SUCCESS_WITH_CONTENT",
  "resultType": "PAYLOAD",
  "results": {
    "columns": [
      {
        "name": "age",
        "logicalType": {
          "type": "INTEGER",
          "nullable": false
        },
        "comment": null
      },
      {
        "name": "name",
        "logicalType": {
          "type": "CHAR",
          "nullable": false,
          "length": 12
        },
        "comment": null
      }
    ],
    "columnInfos": [],
    "data": [
      {
        "kind": "INSERT",
        "fields": [
          23,
          "Alice Liddel"
        ]
      }
    ],
    "fieldGetters": [],
    "rowFormat": "JSON"
  }
}'''

FETCH_RESULT_1_EOS = '''
{
  "isQueryResult": true,
  "jobID": "fe9e295a333a6367b8dd9e30044a5c6b",
  "resultKind": "SUCCESS_WITH_CONTENT",
  "resultType": "EOS",
  "results": {
    "columns": [
      {
        "name": "age",
        "logicalType": {
          "type": "INTEGER",
          "nullable": false
        },
        "comment": null
      },
      {
        "name": "name",
        "logicalType": {
          "type": "CHAR",
          "nullable": false,
          "length": 12
        },
        "comment": null
      }
    ],
    "columnInfos": [],
    "data": [],
    "fieldGetters": [],
    "rowFormat": "JSON"
  }
}
'''

FETCH_RESULT_1_NOT_READY = '''
{
  "nextResultUri": "/v2/sessions/7625ad82-b23b-4118-9683-4a46b7c5022a/operations/353994b9-532d-4c0e-9258-688ec777f948/result/1?rowFormat=JSON",
  "resultType": "NOT_READY"
}
'''

# language=JSON
FETCH_RESULT_2_EMPTY_PAYLOAD = '''
{
    "isQueryResult": false,
    "resultKind": "SUCCESS_WITH_CONTENT",
    "resultType": "EOS",
    "results": {
        "columnInfos": [],
        "columns": [
            {
                "comment": null,
                "logicalType": {
                    "length": 2147483647,
                    "nullable": true,
                    "type": "VARCHAR"
                },
                "name": "jars"
            }
        ],
        "data": [],
        "fieldGetters": [],
        "rowFormat": "JSON"
    }
}
'''

FETCH_RESULT_3_MULTIPLE_ROWS = '''
{
  "isQueryResult": true,
  "jobID": "a0ad286b7259d4755327ce4969a8ec97",
  "nextResultUri": "/v2/sessions/7625ad82-b23b-4118-9683-4a46b7c5022a/operations/353994b9-532d-4c0e-9258-688ec777f948/result/1?rowFormat=JSON",
  "resultKind": "SUCCESS_WITH_CONTENT",
  "resultType": "PAYLOAD",
  "results": {
    "columns": [
      {
        "name": "age",
        "logicalType": {
          "type": "INTEGER",
          "nullable": false
        },
        "comment": null
      },
      {
        "name": "name",
        "logicalType": {
          "type": "CHAR",
          "nullable": false,
          "length": 12
        },
        "comment": null
      }
    ],
    "columnInfos": [],
    "data": [
      {
        "kind": "INSERT",
        "fields": [
          23,
          "Alice Liddel"
        ]
      },
      {
        "kind": "INSERT",
        "fields": [
          19,
          "Bob Smith"
        ]
      }
    ],
    "fieldGetters": [],
    "rowFormat": "JSON"
  }
}'''
