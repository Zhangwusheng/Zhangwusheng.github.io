Kafka Server端参数说明

| 参数名称                        | 含义                                                         | 默认值 | 建议值     |
| ------------------------------- | ------------------------------------------------------------ | ------ | ---------- |
| auto.create.topics.enable       | Enable auto creation of topic on the server                  | true   | false      |
| background.threads              | The number of threads to use for various background processing tasks | 10     | 视情况而定 |
| delete.topic.enable             | Enables delete topic. Delete topic through the admin tool will have no effect if this config is turned off | true   | false      |
| socket.receive.buffer.bytes     | The SO_RCVBUF buffer of the socket server sockets. If the value is -1, the OS default will be used. | 102400 |            |
| socket.send.buffer.bytes        | The SO_SNDBUF buffer of the socket server sockets. If the value is -1, the OS default will be used. | 102400 |            |
| zookeeper.connection.timeout.ms | The max time that the client waits to establish a connection to zookeeper. If not set, the value in zookeeper.session.timeout.ms is used | null   |            |
| zookeeper.session.timeout.ms    | Zookeeper session timeout                                    | 6000   |            |

