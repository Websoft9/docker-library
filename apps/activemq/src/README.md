# Local overrides

- `entrypoint.sh` wraps the official Apache ActiveMQ entrypoint: it appends
  `0.0.0.0/0` and `::/0` to the Web Console's `InetAccessHandler` include list
  (loopback kept), then `exec`s `/usr/local/bin/entrypoint.sh`. This fixes the
  403 the console returns through the published port without maintaining a copy
  of the whole `conf/jetty/jetty-security.xml`.
