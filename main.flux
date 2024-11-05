# Fibonacci sequence
# 1,000,000 numbers will be generated

var n 1000000        # Set the number of terms
var a 0
var b 1
var temp 0

label fib
print {a}       # Print the current Fibonacci number

var temp {a + b} # Calculate the next Fibonacci number
var a {b}       # Update a to the current b
var b {temp}    # Update b to the new Fibonacci number

var n {n - 1}   # Decrement n
if {n > 0} do
    jmp :fib:   # Repeat if more terms are needed
end

