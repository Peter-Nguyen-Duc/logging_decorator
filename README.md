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

within the specified document you want to use it import the logging python file and initate the following function to enable the decorator:
generate_logger_file()


Above a class set the decorator "decorate_all_class_methods"

as example:

@decorate_all_class_methods()
class test:

If you want to decorate a function you must decorate it with "log_decorator" with the input logging.INFO
such that it looks like the following: 

@log_decorator(logging.INFO)


## Run code as submodule
source: https://git-scm.com/book/en/v2/Git-Tools-Submodules
If this code is to be inserted into another github repo, it is done be running the following code

git add submodule https://github.com/Peter-Nguyen-Duc/logging_decorator

git submodule update
git submodule init
