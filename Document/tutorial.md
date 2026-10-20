# <p align="center" style="color: cyan">Breeze of Twilight Tutorial</p>

###### <p align="right" style="color: cyan">Powered by: I.Y.Ryparin</p>

### 基本介绍：

$~~~~~~$这个文档将教会各位如何快速理解这个配置语言的基本信息。
当然，前提可以说明一下：这个程序的语法可能与其它的配置语言相比有一些差别，而且可能显得有一些“啰嗦”。但是如果能够细致了解并且感受一下，那么它可能会成为生产中的一个得力的小助手呢？<br>
$~~~~~~$好啦，不啰嗦了，为了节省各位时间，我就简化表达了。

***

### 1. 最基本说明

- 它不是图灵完备语言，不支持递归。

- 它是强类型语言，而且除了string类型以外大小写全部不敏感。

- 每一段代码都以分号作为结尾，而且只有分号，反大括号是不能作为结束标识的。

- 注释是‘#’，只有单行注释可以使用。

- 有string、int、float、bool、table、database这五种数据类型。

- string支持ASCII转译，但是不支持Unicode转译。
  
  ### 2. 三个部分
  
  $~~~~~~$如果你学过COBOL、BASIC或者汇编这类有亿点老的语言，那么你可能比较容易理解。简单点说，这个语言也分为三个部分：
  **标头部**、**数据部**、**变化规则部**。<br><br>
  
  #### <p align="center">标头部</p>
  
  $~~~~~~$标头部可以类比成对这个配置文件的单独的宏定义，每一个标头都以 **IDENTIFICATION** 关键字进行打头去说明这是一个标头内容，比较类似于每一个文件的 inode 表或者文件头。当然，它们也必须声明在文件的最开头，而且只能声明一次，否则前者会被覆盖掉。
  在这里可以声明程序的唯一ID、编码方式、遵循的解析器版本、是否强制只读等。<br>
  $~~~~~~$具体来说，格式大概就是这样的。<br>
  
  ```text
  【定义关键字】    +   【宏定义的类型】        +   【宏定义的值】
  IDENTIFICATION    CONFIGURATION-ID          "test-identify";
  IDENTIFICATION    CONFIGURATION-ENCODE      "UTF-8";
  IDENTIFICATION    CONFIGURATION-READONLY    FALSE;
  IDENTIFICATION    CONFIGURATION-VERSION     1.0;
  ```
  
  $~~~~~~$目前可以使用的宏定义类型就是上述这四个了，在以后的更新中可能支持更多的宏定义类型。描述如下：

- CONFIGURATION-ID：用来定义每一个配置文件的全局唯一ID，该ID将被管理器用来进行全局性的查找、匹配等操作。

- CONFIGURATION-VERSION：用来定义这个配置语言是被用来遵循哪一个版本的配置语言语法的，保留向前兼容性。

- CONFIGURATION-ENCODE：用来指示这个配置文件采用的是哪一种编码格式，目前还没有实际用途。

- CONFIGURATION-READONLY：一个全局只读锁，要求解析器忽略键值对的可修改指示，强制全部数据为只读状态。

  $~~~~~~$这应该就是可能最常使用的宏定义了，具体需要详细解释可以去看 **header.md** ，那里会有更详细的解释。<br><br>

#### <p align="center">数据部</p>

  $~~~~~~$数据部需要以 **DATABASES-START** 关键字声明这里是数据部开始的地方，
  然后需要以 **DATABASES-END** 关键字去声明这里是数据部结束的地方。在配置文件解析后，数据部也是管理器唯一可以直接访问并进行修改的部分。<br>
  $~~~~~~$在数据部中，每一行数据一般遵循这样的格式：<br>

<p align="center">【名称】[【类型关键字】]【变化说明关键字】=【值】;</p>

$~~~~~~$或者是：

<p align="center">【名称】[【类型关键字】]【变化说明关键字】=【值】->【额外要求语句】;</p>

$~~~~~~$特殊的一点：在这里，名称使用“-”，即减号是可以的，虽然实际使用中这不被提倡，因为容易与数学计算中的减号搞混，不过我认为这里还是有必要去说一下。<br>

$~~~~~~$通常情况下，数据部是类似于JSON，需要被一个且只能是唯一的大括号包裹以作为最外围的DATABASE部开始的标志。所有的数据都需要被塞进这个大括号内部。<br>

$~~~~~~$这里，我们可以举一个简单的示例，这样就更容易理解了：<br>

```textile
DATABASES-START;
{
    INT_VALUE [INT] CST = 1;
    FLOAT_VALUE [FLOAT] CST = 0.1;
    BOOL_VALUE [BOOL] CST = TRUE;
    STR_VALUE [STRING] CST = "Hello!";
    TABLE_VALUE [TABLE<INT, BOOL>] = [(1, TRUE), (3, FALSE)];
    DATABASE_VALUE [DATABASE] = {
        INT_LIMIT [INT] CST = 0x20 -> LIMIT(1 TO 300, EXCLUDE 12);
    };
    UNION_VALUE [UNION<INT, STRING, BOOL>] CST = TRUE;
    ENUM_VALUE [ENUM<1,2,3,4,5,6>] CST = 1;
    ANY_VALUE [ANYTHING] CST = 1;
    CONVERSION_VALUE [CONVERSION<INT>] CST = 1;
};
DATABASES-END;
```

$~~~~~~$也许直接说可能比较让人疑惑，这里我们简单解释一下每一个部分：

- 名称：可以使用的有：数字、字母、下划线、减号。虽然解析器无所谓它们出现在哪，不过还是建议遵循“字母打头”原则。

- 类型：需要用中括号框起来，内部包含一个指示数据类型的关键字。这个关键字可以是int、float、string、bool、database、table、union、enum、conversion。请注意：table、union、conversion三者需要尖括号，内部内联子项的类型（不填默认是ANYTHING）；而如果类型是enum，则默认需要尖括号内联所有枚举的类型（标识符目前还不能支持，所以目前只能在里面填写受支持的数据类型，比较类似于受到限制的ANYTHING）。

- 可变标识：目前只支持CST/MUT两种，分别表示该键值对不能被外部修改和该键值对可以被外部修改。

- 值：这就不需要多说了吧？

- 额外声明：需要在值的后方连接一个“->”符号，后面可以填写相应的规则关键字（目前支持LIMIT（硬限制）、REGULAR（字符串正则表达式限制））两种。可以定义多个额外声明，每一个额外声明需要用小括号框起内部的声明信息，所有逗号均表示AND关系，如果某一项前面添加EXCLUDE关键字则表示排除，反之则表示包含。

$~~~~~~$大致内容大概就是这些了，如果需要详细教程可以去查看 **database.md** 文档。<br>

<br>

#### <p align="center">变化规则部</p>

$~~~~~~$变化规则部需要以 **CONVERSION-START** 关键字声明这里是变化规则部分开始的地方，然后以 **CONVERSION-END** 关键字声明这里是变化规则部分结束的地方。<br>
$~~~~~~$这个部分牵扯到上文中存在的一种特殊的类型： **conversion** 。依据字面意思“变化的”，这显然是声明这是一个不断变化的值。
但与 **CST/MUT** 关键字不同的是： **CST/MUT** 表示的是 **这个值是否可以被程序通过管理器修改** ，而 **conversion** 表示的是 **这个值是否会因为某些条件的变化而发生变化** 。
是的，意思是这是否是一个动态的、会不会因为某些条件变化而随之变化的值。<br>
$~~~~~~$同样，在这里我们直接举一个例子：
```text
CONVERSION-START;
{
    CONVERSION TimeDelay [INT] WITH-TIME timeout {
        COMPARE timeout.hour == 1 THEN RETURN 100;
        COMPARE timeout.second == 2 THEN RETURN 1000;
        COMPARE timeout.minute <= 4 THEN RETURN 203;
        COMPARE DEFAULT THEN RETURN -2;
    };
    CONVERSION CountDelay [STRING] WITH-COUNT countdown 1 TO 50 {
        COMPARE countdown == 1 THEN RETURN "Start!";
        COMPARE countdown == 50 THEN RETURN "End!";
        COMPARE DEFAULT THEN RETURN "normal";
    };
};
CONVERSION-END;
```
$~~~~~~$Emmm...看起来有些像函数？好吧，可惜的是：它不能递归，也不能嵌套。
当然，更不能引用其它的变化规则。所以实际上，它可能更像一种规则表。<br>
$~~~~~~$既然是规则表，那么它的格式大概就是这样的：
  - 以 **CONVERSION** 关键字打头。
  - 紧接着是一个名称，表示这个转换规则的名称。
  - 紧接着是一个中括号，里面是这个转换规则的返回值类型。
  - 紧接着是一个 **WITH-** 开头的关键字，表示它所遵循的规则类型。
  - 紧接着是另一个名称，表示要把变化的值传入到哪个变量中去。
  - 最后，根据规则的不同，可能会有一些额外的规则限制，比如 **WITH-COUNT** 规则就需要一个范围限制，表示这个变化值的范围。<br>

$~~~~~~$在规则体中，使用 **COMPARE** 关键字去声明一个条件，紧接着是一个条件表达式，最后是一个 **THEN RETURN** 关键字去声明这个条件成立时的返回值。<br>
$~~~~~~$如果没有任何条件成立，那么就会执行 **COMPARE DEFAULT THEN RETURN** 语句，返回一个默认值。<br>
