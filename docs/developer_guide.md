Developer's Guide
=================

*请多参考例子包*
不同于现有调度系统__skewer__的组件开发方式，__bpm.py__抽象出了`Task`这一概念。一切可被bpm.py调度的对象皆是Task。所以，`Component`是一种Task，`Process`也是一种Task，并且将来会实现更多Task。

因为上面的缘故，bpm.py采用`Package`的方式管理Task。这里的Package就是Python的Package，因此，Package不仅仅可以管理Task，还可以管理任意Python代码。为了进行代码的版本控制，bpm.py使用[Mercurial](http://mercurial.selenic.com)，同时，为了对不同的Package进行隔离，每一个Package都有各自的仓库。
> 在内网可通过[http://t.ied.com/hg/](http://t.ied.com/hg/)查看所有仓库。已经为组件开发建立仓库`bk`，并开通了读写权限，可使用Mercurial客户端`hg`或者[MercurialEclipse](http://mercurial.selenic.com/wiki/MercurialEclipse)访问。使用hg访问的例子如下：

    $ hg clone http://t.ied.com/hg/bk/  # 从仓库克隆到本地
    $ hg commit  # 提交代码，不同于SVN，这里只会提交到本地仓库
    $ hg push  # 将本地仓库推送到服务器
    
MercurialEclipse的安装及使用方法请参考网络上的教程。

## 开发环境介绍
### 页面工具
#### Django Admin
用户名/密码都是`admin`。
- 任务查询：[http://t.ied.com/bpm/kernel/task/](http://t.ied.com/bpm/kernel/task/)
- 日志查询：[http://t.ied.com/bpm/log/record/](http://t.ied.com/bpm/log/record/)
#### Mercurial Web
- 版本控制：[http://t.ied.com/hg/](http://t.ied.com/hg/)

### 工程环境

    $ ssh platform@10.130.131.232
    $ workon bpm
    $ ls

#### 目录结构
*仅包含需要了解的项*

> - bpm/ -- bpm.py所在包
- etc/
    - vassals/
        - bpm.ini -- Django项目的`uwsgi`配置文件，使用`touch bpm.ini`进行重载
- m2s3/ -- `settings`所在包
- manage.py
- repos/
    - bk/ -- 已建立的开发仓库
    - bpm/ -- 简单的开发示例
- var/
    - log/
        - bpm.log -- uwsgi日志，如果页面出现异常轻查看此文件
        - celeryd.log -- celery日志，如果任务出现异常请查看此文件

#### 新建任务
`Task.objects.start(self, name, args=None, kwargs=None)`

    $ ./manage.py shell
    Python 2.7.2 Stackless 3.1b3 060516 (default, Dec 17 2012, 11:24:01)
    [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin Type "help", "copyright", "credits" or "license" for more informatio.
    >>> from bpm.engine.kernel.models import Task
    >>> Task.objects.start('bpm.example.process.SubProcessExample', args=('example',))

暂未提供任务查询接口，请通过页面工具查看任务状态。如果任务卡死，请查看celery日志。

#### 重试任务
`Task.objects.retry(self, instance, args=None, kwargs=None)`

    >>> old = Task.objects.get(pk=x)
    >>> Task.objects.retry(old)

重试任务并不会使用原有任务的模型实例，而是新建了一个任务实例。可以在重试任务是修改任务参数。

#### 清空任务/日志表
如果测试数据过多，可以使用一下命令清空任务/日志表：

    $ ./manage.py truncate task  # 清空任务表
    $ ./manage.py truncate log  # 清空日志表
    $ ./manage.py truncate  # 清空任务表和日志表

## API
### 概述
> "Everything is task." *一切皆是任务*

不同于Python的*一切皆是对象*，bpm.py的*一切皆是任务*仅针对引擎可调度的对象。例如：目前的skewer引擎可调度的对象有过程和组件两种，过程是过程，组件是组件，引擎针对过程和组件编写了不同的处理代码。如果要增加一种区别与过程和组件的类型，就需要编写第三套处理逻辑。

为了规避这个问题，提高引擎的可拓展性，bpm.py提出了*一切皆是任务*的概念，并根据已考虑到的三种任务类型(过程/组件/表单)进行抽象，拟定了一套能够实现这个概念的规范，只要新的类型符合这套规范，便可以被引擎调度。

因此，所有的Task必须继承自`bpm.engine.kernel.backends.base.BaseTaskBackend`，通常是不需要关注底层的API的，这里不再做过多讲解。下面将要用到的BaseProcess和BaseComponent都继承自BaseTaskBackend。

### 任务
目前只实现了过程和组件类型的任务。开发一个过程/组件，需要编写一个继承自`bpm.engine.kernel.BaseProcess/BaseComponent`的类，并实现`start`方法：

    from bpm.engine.kernel import BaseComponent, BaseProcess

    class ExampleComponent(BaseComponent):

        def start(self):
            # do something

    class ExampleProcess(BaseProcess):

        def start(self):
            # do something else

其中，start方法的参数就是该任务的参数，例如：

    def start(self):
        # 不需要任何参数
    def start(self, name):
        # 必须要一个参数
    def start(self, name=None):
        # 需要一个可选参数
    def start(self, *args, **kwargs):
        # 可以接受任意参数

#### 过程
在过程定义里，使用`self.tasklet`方法调用其它任务。tasklet方法返回的是一个`TaskHandler`实例，调用该实例的`__call__`方法来传入任务参数：

    def start(self):
        self.tasklet(ExampleTask)(name='example')  # 第二对括号实际上是调用了__call__方法

tasklet方法的第一个参数必须为BaseTaskBackend的子类。在tasklet方法中，可以使用`predecessors`参数指定前置任务：

    def start(self):
        task_a = self.tasklet(TaskA)()
        task_b = self.tasklet(TaskB, predecessors=[task_a])()

如果后面的任务需要前置任务的返回值：

    def start(self):
        task_a = self.tasklet(TaskA)()
        task_b = self.tasklet(TaskB)(task_a)  # 这里可以不指明predecessors

使用`self.complete`方法结束一个过程：

    def start(self):
        task_a = self.tasklet(TaskA)()
        task_b = self.tasklet(TaskB)(task_a)

        self.complete(task_b)  # 以task_b的返回值作为过程的返回值

如果不显式调用complete方法，则等同于调用`self.complete()`，表示过程执行成功，返回值为`None`。

#### 组件
组件有三种返回方式：
- 在start方法内显式调用`self.complete`
- 在scheduler指定的方法内显式调用`self.complete`
- 通过系统接口进行外部回调

##### 显式调用，适用于同步任务
    def start(self):
        # do something
        self.complete(*args, **kwargs)

##### 在scheduler指定的方法内显式调用，适用于异步任务
    def start(self):
        # do something
        self.task_id = xxx  # 从前面的逻辑过得，保存的属性里供on_schedule方法使用
        self.set_default_scheduler(self.on_schedule)

    def on_schedule(self):
        # 这里通常是使用self.task_id去轮询某异步接口
        if self.schedule_count >= 3:
            self.complete(*args, **kwargs)

##### 通过系统接口进行外部回调，适用于审批任务
就是不在组件定义内显式调用complete方法，而是等待外部系统通过接口进行回调。

*注：接口暂未提供*

### 模块引用
分为原生引用和内部引用两种模式：
- 原生引用：就是Python默认的引用方式
- 内部引用：从bpm.py的仓库引用模块

    import random  # 原生引用
    from bpm.engine.kernel import internal_import  # 切换到内部引用模式
    from internal.repos import SomeTask, some_function  # 内部引用

需要注意的是：
- 一旦切换到内部引用模式，就没法在切回到原生引用模式。
- 内部引用暂时还是一个比较简单的版本，很多高级的引用方式还不能支持，比如相对引用。请暂时避免使用文件路径和模块路径不一致的引用。

### 日志
因安全限制，外部代码不允许访问本地文件，故只能使用网络日志系统，使用方法如下：

    from bpm.log import get_logger

    logger = get_logger()

    logger.debug('Hello World!')

代码里不需要任何的日志配置，这些配置以后都将通过页面方式进行管理。

### 安全
- 不能对任何以下划线开头的对象进行任何操作，包括定义；
