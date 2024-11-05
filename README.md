# **LuminentVortex**

This is technically a VM called **BloodVM**, but the interpreter is called **LuminentVortex** (LV), and the language is called **Flux**.

## Flux
Flux, a Expression-First Programming (EFP) language

### Draw backs
flux currently does not handle strings, or functions, but they are planed


## **Structure**

LuminentVortex programs (and by extension, Flux programs) are **expression-first** programs.

### **What Does "Expression-First" Mean?**

Simply put, it means that expressions are evaluated first. For example:
```flux
var x {35 + 53}
```
In this line, the part `{35 + 53}` is the expression that gets evaluated before assigning the result to `x`. You can also perform calculations with pointers, labels, and the current line number.

#### **Example of Evaluation Process:**
1. **Initial Stack State:**
   ```
   |----stack----|
   |  {35 + 53}  |
   |-------------|
   |  var assign |
   |-------------|
   ```

2. The expression `{35 + 53}` gets resolved to `88`, then that value is assigned to `x`.

### **Labels**

Labels are essentially pointers to line numbers. For example:
```
/*n*|****code**********\
* 0 * label labelName  *
* 1 * jmp {:labelName:}*
\**********************/
```
This creates an infinite loop. When the evaluator encounters `{...}`, it replaces it with the value of the specified label, which in this case would be `0`.

## **Comments**

Comments in Flux are denoted by `#`. The evaluator/loader splits the line on the first `#` and discards everything after it. For example:
```flux
"The quick brown fox jumps # over the lazy dog"
```
would be split as follows:
```
["The quick brown fox jumps", "over the lazy dog"]
```
The evaluator/loader would then discard the `"over the lazy dog"` portion since it comes after the comment notation.

### **Usage in Flux Code**
```flux
# Define the dimensions of the rectangle
var rw 500  # width
var rh 200  # height

# Calculate the area of the rectangle
var area {rw * rh}

# Print the area
print {area}  # Expected Output: 100000
```

## **Example Programs**

### **Example 1:**
```flux
var x 100
var y 100
print {x + y}        # Expected Output: 200

var z {x * 4 + y}
print {z}            # Expected Output: 500

var z {z - (x + y)}  # Update z to 300
if {z > 40} do
    jmp 7            # Jump back to line 7
end
```

### **Example 2:**
```flux
var playerX 100
var playerY 100
print {playerX + playerY}  # Expected Output: 200
```

## **Running LuminentVortex**

To run LV, execute the following command in your terminal:
```sh
python main.py main.flux
```
Assuming you have a `main.flux` file with no errors, you should see output similar to the following (using the rectangle example):
```
> python main.py main.flux 
LuminentVortex - v1
100000
```
LV/BloodVM always outputs the version above the results of your code to make it easier to debug certain errors (like if strings are added later on).

## **Flux vs Python: Performance Comparison**

In this comparison, we generate 1,000 Fibonacci numbers in both Flux and native Python to assess their speed. Since Flux is implemented on top of Python, this provides a fair comparison.

### Generating 1,000 Fibonacci Numbers
```sh
❯ time python fib.py > out.txt

________________________________________________________
Executed in  320.13 millis    fish           external
   usr time   28.10 millis    0.00 millis   28.10 millis
   sys time   15.34 millis    1.22 millis   14.12 millis

❯ time python main.py main.flux > out.txt

________________________________________________________
Executed in    1.23 secs      fish           external
   usr time  128.29 millis  746.00 micros  127.55 millis
   sys time   10.21 millis  460.00 micros    9.75 millis
```

### Generating 5,000 Numbers
```sh
❯ time python main.py main.flux > out.txt

________________________________________________________
Executed in    1.20 secs      fish           external
   usr time   446.63 millis  779.00 micros  445.85 millis
   sys time   36.11 millis  300.00 micros   35.81 millis

❯ time python fib.py > out.txt

________________________________________________________
Executed in  133.67 millis    fish           external
   usr time   96.06 millis    1.07 millis   94.99 millis
   sys time   26.08 millis    0.67 millis   25.41 millis
```

### Generating 100,000 Numbers
Native Python crashes:
```sh
❯ time python fib.py > out.txt
Traceback (most recent call last):
  File "/home/cross/code/bloodvm/fib.py", line 11, in <module>
    fibonacci_sequence(n)
  File "/home/cross/code/bloodvm/fib.py", line 5, in fibonacci_sequence
    print(a)
ValueError: Exceeds the limit (4300 digits) for integer string conversion; use sys.set_int_max_str_digits() to increase the limit.

Executed in    4.75 secs    fish           external
   usr time    3.90 secs  822.00 micros    3.90 secs
   sys time    0.18 secs  519.00 micros    0.18 secs
```

Flux handles this smoothly:
```sh
❯ time python main.py main.flux > out.txt

________________________________________________________
Executed in    6.58 secs    fish           external
   usr time    5.19 secs    0.59 millis    5.19 secs
   sys time    0.19 secs   11.49 millis    0.18 secs
```

For anyone interested, the output file size:
```sh
❯ ls out.txt 
.rw-r--r-- 44M cross  5 Nov 19:02 out.txt
```
*(My `ls` is aliased to `eza -l`.)*

### **How Does Flux Avoid Crashing?**

It's quite simple: Flux does not use recursion. Here's an example Fibonacci sequence implementation:
```flux
# Fibonacci sequence
var n 100000        # Set the number of terms
var a 0
var b 1
var temp 0

label fib
print {a}           # Print the current Fibonacci number

var temp {a + b}    # Calculate the next Fibonacci number
var a {b}          # Update a to the current b
var b {temp}       # Update b to the new Fibonacci number

var n {n - 1}      # Decrement n
if {n > 0} do
    jmp :fib:      # Repeat if more terms are needed
end
```

In this example, `jmp` moves the `head` (internally called `pc`) to the desired line, allowing execution to resume without risking a stack overflow.
