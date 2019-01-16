  该工具功能有：
  
  1、域名CNAME分区查询（国内三大运营商*31个省+部分长宽、教育网、海外等区域的CNAME指向情况）
  2、域名 A 记录最终指向（国内三大运营商*31个省+部分长宽、教育网、海外等区域的 A 记录指向情况）
  3、查询 IP 归属地
  
  非常适用于 CDN 厂商或使用了 CDN 服务的域名上。
  
  安装要点：
  1、从 example 目录获取 dig dnsfind.py 程序上传至linux服务器
  2、执行python程序即可（需要根据实际需求，对应修改里面的域名）
  3、实现效果（详见 effect-1.png effect-2.png effect-3.png effect-4.png effect-5.png）
  
  注意：
  因为有依赖于 ipip.net 的ip库（但我没有权限对该ip库进行共享），所以需要使用者去获取ipip.net 的ip库或者使用第三方免费ip库。
