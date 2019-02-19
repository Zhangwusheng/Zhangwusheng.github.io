### OpenTSDB之RollUp/PreAggregation使用



#### 1.配置RollUp/PreAggregation

首先，在配置启用rollup，需要修改opentsdb.conf，增加如下配置：

tsd.rollups.enable=true

tsd.rollups.config=/path/to/rollup_config.json



其中rollup_config.json的内容如下：

```
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
    "preAggregationTable": "tsdb-preagg-1h",
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



具体含义可参考如下链接：

http://opentsdb.net/docs/build/html/user_guide/rollups.html?highlight=rollup

| Name                | Data Type | Required | Description                                                  | Example               |
| ------------------- | --------- | -------- | ------------------------------------------------------------ | --------------------- |
| table               | String    | Required | The base or rollup table for non-pre-aggregated data. For the default table, this should be `tsdb` or the table existing raw data is written to. For rolled up data, it must be a different table than the raw data. | tsdb-rollup-1h        |
| preAggregationTable | String    | Required | The table where pre-aggregated and (optionally) rolled up data should be written to. This may be the same table as the `table` value. | tsdb-rollup-preagg-1h |
| interval            | String    | Required | The expected interval between data points in the format `<interval><units>`. E.g. if rollups are computed every hour, the interval should be `1h`. If they are computed every 10 minutes, set it to `10m`. For the default table, this value is ignored. | 1h                    |
| rowSpan             | String    | Required | The width of each row in storage. This value must be greater than the `interval` and defines the number of `interval``s that will fit in each row. E.g. ifthe interval is ``1h` and `rowSpan` is `1d` then we would have 24 values per row. | 1d                    |
| defaultInterval     | Boolean   | Optional | Whether or not the configured interval is the default for raw, non-rolled up data. | true                  |

假设我们的数据是五分钟一条，然后汇总成一个小时一条，存放到tsdb-preagg-1h这个表中，那么应该增加一个配置项（上面已配置）：

```
{
    "table": "tsdb",
    "preAggregationTable": "tsdb-preagg-1h",
    "interval": "1h",
    "rowSpan": "1d",
    "defaultInterval": false
  }
```

注意interval为1h，表示按照一个小时汇总一次，如果需要从汇总表查数据，defaultInterval一定要设置成false。参见http://opentsdb.net/docs/build/html/user_guide/rollups.html?highlight=rollup对**Default**的说明：

> 
>
> - **Default** - This is the default, *raw* data OpenTSDB table defined by `"defaultInterval":true`. For existing installations, this would be the `tsdb` table or whatever is defined in `tsd.storage.hbase.data_table`. Intervals and spans are ignored, defaulting to the OpenTSDB 1 hour row width and storing data with the resolution and timestamp given. Each TSD and configuration can have *only one* default configured at a time.

Default实际上就是到原生数据表里面去查找。

#### 2.写入RollUp数据

http://yourip:port/api/rollup

**POST**

```json
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



> ***注意：interval里面的值一定要在配置文件里面出现过，根据这个找到汇总数据的表；***



#### 3.查询RollUp数据

注意：preAggregate 要设置成true，rollupUsage设置成`ROLLUP_FALLBACK` 或者`ROLLUP_NOFALLBACK` ，downsample要设置成"1h-sum"，表示数据要按照一个小时去汇总，这样在查询的时候会将降采样的查询转变为rollup的查询；

```json
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

------

### 1小时查询结果

```json
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



