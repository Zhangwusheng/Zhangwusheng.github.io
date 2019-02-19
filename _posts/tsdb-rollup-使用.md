### OpenTSDB之RollUp使用指南



#### 1.配置RollUp

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

































子查询的配置：

http://opentsdb.net/docs/build/html/api_http/query/index.html?highlight=rollup

| rollupUsage *(2.4)* | String | Optional | An optional fallback mode when fetching rollup data. Can either be `ROLLUP_RAW` to skip rollups, `ROLLUP_NOFALLBACK` to only query the auto-detected rollup table, `ROLLUP_FALLBACK` to fallback to matching rollup tables in sequence or `ROLLUP_FALLBACK_RAW` to fall back to the raw table if nothing was found in the first auto table. | ROLLUP_NOFALLBACK                                            | ROLLUP_RAW |
| ------------------- | ------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------- |
|                     |        |          | `ROLLUP_RAW：不使用RollUp，`ROLLUP_NOFALLBACK`仅仅使用rollup的数据，`ROLLUP_FALLBACK`：在raw数据里面查不到，查询rollup数据？ | `ROLLUP_FALLBACK_RAW`：首先使用autotable，然后使用rawtable？ |            |





配置样例：

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
              "preAggregationTable": "tsdb-preagg",
              "interval": "1m",
              "rowSpan": "1h",
              "defaultInterval": true
      }, {
              "table": "tsdb-rollup-1h",
              "preAggregationTable": "tsdb-rollup-preagg-1h",
              "interval": "1h",
              "rowSpan": "1d"
      }]
}
```

intervals应该是有很多时间维度的汇总数据才对，否则不应该有这么多的intervals选项。

rowSpan具体指的是：rowkey里面的时间戳的力度？？interval应该是每个列的力度？？



一个是原始数据表，一个是汇总数据表，一个是汇总力度，代表了列的维度，一个是行的力度？？





net.opentsdb.core.TSDB#TSDB(org.hbase.async.HBaseClient, net.opentsdb.utils.Config)



|                                       |         |          |                                                              |            |                    |
| ------------------------------------- | ------- | -------- | ------------------------------------------------------------ | ---------- | ------------------ |
| tsd.rollups.config *(2.4)*            | String  | Optional | The path to a configuration file detailing available rollup tables and aggregations. Must set `tsd.rollups.enable` to `true` for this option to be parsed. See [Rollup And Pre-Aggregates](http://opentsdb.net/docs/build/html/user_guide/rollups.html) |            | rollup_config.json |
| tsd.rollups.enable *(2.4)*            | Boolean | Optional | Whether or not to enable rollup and pre-aggregation storage and writing. | false      |                    |
| tsd.rollups.tag_raw *(2.4)*           | Boolean | Optional | Whether or not to tag non-rolled-up and non-pre-aggregated values with the tag key configured in `tsd.rollups.agg_tag_key`and value configured in `tsd.rollups.raw_agg_tag_value` | false      |                    |
| tsd.rollups.agg_tag_key *(2.4)*       | String  | Optional | A special key to tag pre-aggregated data with when writing to storage | _aggregate |                    |
| tsd.rollups.raw_agg_tag_value *(2.4)* | String  | Optional | A special tag value to non-rolled-up and non-pre-aggregated data with when writing to storage. `tsd.rollups.tag_raw` must be set to true. | RAW        |                    |
| tsd.rollups.block_derived *(2.4)*     | Boolean | Optional | Whether or not to block storing derived aggregations such as `AVG` and `DEV`. | true       |                    |

 

```

///// 如果rollups开启！~
if (config.getBoolean("tsd.rollups.enable")) {
  //tsd.rollups.config可以是文件，也可以是一整行的json串，最好是配置成文件
  String conf = config.getString("tsd.rollups.config");
  if (Strings.isNullOrEmpty(conf)) {
    throw new IllegalArgumentException("Rollups were enabled but "
        + "'tsd.rollups.config' is null or empty.");
  }
  if (conf.endsWith(".json")) {
    try {
      conf = Files.toString(new File(conf), Const.UTF8_CHARSET);
    } catch (IOException e) {
      throw new IllegalArgumentException("Failed to open conf file: " 
          + conf, e);
    }
  }
  rollup_config = JSON.parseToObject(conf, RollupConfig.class);
  RollupInterval config_default = null;
  for (final RollupInterval interval: rollup_config.getRollups().values()) {
    if (interval.isDefaultInterval()) {
      config_default = interval;
      break;
    }
  }
  if (config_default == null) {
    throw new IllegalArgumentException("None of the rollup intervals were "
        + "marked as the \"default\".");
  }
  default_interval = config_default;
  //是否给原始数据加上一个tag？

  
  With rollups enabled, if you plan to use pre-aggregates, you may want to help differentiate raw data from pre-aggregates by having TSDB automatically inject _aggregate=RAW. Just configure the tsd.rollups.tag_raw setting to true.
  
  
  tag_raw_data = config.getBoolean("tsd.rollups.tag_raw");
  
    
  In OpenTSDB, pre-aggregates are differentiated from other time series with a special tag. The default tag key is _aggregate (configurable via tsd.rollups.agg_tag_key). The aggregation function used to generate the data is then stored in the tag value in upper-case. Lets look at an example:
  如果tag_raw设置为true的话，需要配置 tag的列名和列值，agg_tag_key就是列名，raw_agg_tag_value就是那个值！
  
  agg_tag_key = config.getString("tsd.rollups.agg_tag_key");
  raw_agg_tag_value = config.getString("tsd.rollups.raw_agg_tag_value");
  rollups_block_derived = config.getBoolean("tsd.rollups.block_derived");
} 
```



写数据的时候：

```
[
    {
        "metric": "sys.cpu.nice",
        "timestamp": 1346846400,
        "value": 18,
        "tags": {
           "host": "web01",
           "dc": "lga"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    },
    {
        "metric": "sys.cpu.nice",
        "timestamp": 1346846400,
        "value": 9,
        "tags": {
           "host": "web02",
           "dc": "lga"
        },
        "interval": "1h",
        "aggregator": "SUM",
        "groupByAggregator": "SUM"
    }
]
```

is_groupby = groupByAggregator！= null

groupby_aggregator = groupByAggregator

rollup_aggregator = aggregator

interval： interval字段

```
public Deferred<Object> addAggregatePoint(final String metric,
                                 final long timestamp,
                                 final long value,
                                 final Map<String, String> tags,
                                 final boolean is_groupby,
                                 final String interval,
                                 final String rollup_aggregator,
                                 final String groupby_aggregator) {
                                 
                                 
```


http://127.0.0.1:8585/api/rollup

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



RollUp生产调试过程：



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








