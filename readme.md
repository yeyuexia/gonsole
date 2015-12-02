# Weclome to gonsole
gonsole is a terminal for Golang for who is learning Golang. Like Python terminal, you can try your code and get output directly. 

## Usage

run gonsole.py to enter terminal

```
python gonsole.py
```
in terminal, you can try your codes like this:

```
>4+5
9
>fmt.Println("hello world")
hello world
```

Notes: *gonsole would auto import `fmt` package*

import package

```
>import "fmt"
```

function defined

```
>func test() {
	fmt.Println("hello world")
	}
```
invoke function

```
>test()
hello world
```
redefined

```
>test := "aaa"
```
invoke

```
> fmt.Println(test)
aaa
```


## Command

* `exit` exit gonsole
* `export` export your code to target file

```
export demo.go
```

## How it works
gonsole receive you last input code and based on it to generate the execute context. 

for example, if you input the follow codes.

```
1: import "fmt"
2: fmt.Println("test")
3: a := 30
4: b := "hello"
5: c := b + " world"
6: fmt.Println(c)
```

When line 6 executed, gonsole find the code `fmt.Println(c)` used `fmt` and `c`, so it lookup the declared and used codes `1`, `4`, `5`, so the actually invoke codes would like:

```
import "fmt"

func main() {
	b := "hello"
	c := b + " world"
	fmt.Println(c)
}
```