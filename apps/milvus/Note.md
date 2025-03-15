# Milvus

- -advertise-client-urls's value is very important
```
command: etcd -advertise-client-urls=http://${W9_RCODE}etcd:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
```

## Trouble

#### Error: LD_PRELOAD cannot be preloaded?

refer to: https://github.com/milvus-io/milvus/discussions/38702