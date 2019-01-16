  一、前言
  
  Dns-partition-detection是一个强大的DNS分区解析工具，它的具体功能有
 
  1、域名CNAME分区查询（国内三大运营商*31个省+部分长宽、教育网、海外等区域的CNAME指向情况）
  2、域名 A 记录最终指向（国内三大运营商*31个省+部分长宽、教育网、海外等区域的 A 记录指向情况）
  3、查询 IP 归属地
  非常适用于 CDN 厂商或使用了 CDN 服务的域名上。
  
  对比传统的DNS分区解析工具，它的优点有：
  1、无需依赖localdns 列表（通过EDNS解析）
  2、解析区域更全（三大运营商+长宽+教育网+海外）
  3、会输出CNAME的备案厂商
  4、操作更为简单
  5、维护简单（就一个python程序）
  
 二、安装
 
  1、建议前端部署一个nginx充当网关代理
  2、从 example 目录获取 dig dnsfind.py 程序上传至linux服务器
  3、执行python程序即可（需要根据实际需求，对应修改里面的域名）
  4、具体实现效果（详见 effect-1.png effect-2.png effect-3.png effect-4.png effect-5.png）
  
  注意：
  因为有依赖于 ipip.net 的ip库（本人没有权限对该ip库进行共享），所以需要使用者去获取ipip.net 的ip库或者使用第三方免费ip库。
  你也可以不用该ip库（ip将无法进行区域解析）显示会不太友好。
  
三、其它

  开发者联系 hnxiezan@163.com
