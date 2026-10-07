# logging_decorator
I typically require function level logging on my code, and have 
therefore developed a decorator which can automatically decorate all classes in 
python classes with logging functions which will be used to generate detailed 
logging information about code behavior. git clone this repo into coding projects where the logging decorator is required



## data type specific print outs within the decorator
change however is required, but for specific data types the value is not 
printed, to not overbloat the log file, the variables are as such:

 - numpy.ndarray -> output shape and type
 - tf.Tensor -> output shape and type
 - dict -> output keys
 - tuple -> output length
 - list -> output length


## Example usage
Above the class set the decorator "decorate_all_class_methods"

as example:

@decorate_all_class_methods()
class test:




