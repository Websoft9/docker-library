## Canal

### support version
Canal是否支持[MySQL8.0](https://github.com/alibaba/canal/wiki/AdminGuide)和以上版本没有明确说明

### 复制源配置
Canal完全按照MySQL复制策略伪装成"slave"工作，所以MySQL源需要配置，开启binlog日志和设置serverid等工作是否还是需要一个自动化脚本？

