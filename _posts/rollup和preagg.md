### json配置
``` JSON
{
  "aggregationIds": {
    "sum": 0,
    "count": 1,
    "min": 2,
    "max": 3
  },
  "intervals": [{
    "table": "tsdb",
    "preAggregationTable": "tsdb",
    "interval": "1s",
    "rowSpan": "1h",
    "defaultInterval": true
  },{
    "table": "tsdb",
    "preAggregationTable": "tsdb-preagg_1h",
    "interval": "1h",
    "rowSpan": "1d",
    "defaultInterval": false
  },{
    "table": "tsdb",
    "preAggregationTable": "tsdb-preagg_1m",
    "interval": "1m",
    "rowSpan": "1h",
    "defaultInterval": false
  }]
}
```
---
### opentsdb.conf配置
```
# json配置路径
tsd.rollups.config=rollup_config.json
tsd.rollups.enable=true
```
---
### rollup插入数据
``` JSON
http://127.0.0.1:8585/api/rollup

[
    {
        "metric": "sys.cpu.nice",
        "timestamp": 1346847000,
        "value": 18,
        "tags": {
           "host": "web01",
           "dc": "lga",
           "interface":"eth0"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    },{
        "metric": "sys.cpu.nice",
        "timestamp": 1346847000,
        "value": 9,
        "tags": {
           "host": "web02",
           "dc": "lga",
           "interface":"eth0"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    },{
        "metric": "sys.cpu.nice",
        "timestamp": 1346847000,
        "value": -1,
        "tags": {
           "host": "web03",
           "dc": "lgc",
           "interface":"eth0"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    },
    {
        "metric": "sys.cpu.nice",
        "timestamp": 1346847000,
        "value": 2,
        "tags": {
           "host": "web04",
           "dc": "lgc",
           "interface":"eth0"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    }
]

```
---
###  rollup查询方法
``` JSON
http://127.0.0.1:8585/api/query
{
  "delete": false,
  "msResolution": false,
  "noAnnotations": false,
  "queries": [{
    "aggregator": "none",
    "explicitTags": false,
    "preAggregate":"true",
    "rollupUsage":"ROLLUP_FALLBACK",
    "downsample": "1h-sum",
    "filters": [],
    "metric": "sys.cpu.nice",
    "percentiles": [],
    "rate": false,
    "rateOptions": {},
    "tsuids": []
  }],
  "showQuery": false,
  "showStats": false,
  "showSummary": false,
  "showTSUIDs": false,
  "start": 1346846400,
  "end": 1346850000,
  "useCalendar": false,
  "msResolution":true
}
```
---
### 1小时查询结果
``` JSON
[
    {
        "metric": "sys.cpu.nice",
        "tags": {
            "host": "web01",
            "_aggregate": "SUM",
            "interface": "eth0",
            "dc": "lga"
        },
        "aggregateTags": [],
        "dps": {
            "1346846400000": 18
        }
    },
    {
        "metric": "sys.cpu.nice",
        "tags": {
            "host": "web02",
            "_aggregate": "SUM",
            "interface": "eth0",
            "dc": "lga"
        },
        "aggregateTags": [],
        "dps": {
            "1346846400000": 9
        }
    },
    {
        "metric": "sys.cpu.nice",
        "tags": {
            "host": "web03",
            "_aggregate": "SUM",
            "interface": "eth0",
            "dc": "lgc"
        },
        "aggregateTags": [],
        "dps": {
            "1346846400000": -1
        }
    },
    {
        "metric": "sys.cpu.nice",
        "tags": {
            "host": "web04",
            "_aggregate": "SUM",
            "interface": "eth0",
            "dc": "lgc"
        },
        "aggregateTags": [],
        "dps": {
            "1346846400000": 2
        }
    }
]
```