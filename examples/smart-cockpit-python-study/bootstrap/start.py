"""四个独立进程如何启动？教学归纳，对应根 package.json 启动命令。
原目录没有同名 start.mjs；这里便于阅读整体部署。
"""


def start_four_processes():
    检查依赖配置和端口()
    并发启动('Service', '后台Agent', 'Gateway', '客户端')
    # 原 Gateway 自己等待 Service 的健康检查通过，再提供服务。
