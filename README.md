# Research Project Course

## Implementation of a model based mutation testing system
### Sebastian Öhland 1901477

* The model of the SUT is located in models folder.
* All mutation methods are implemented in the Model class.
* All mutation models are located in the folder named mutations and grouped by their mutation operator.
* The script generator.py is creating new mutation models from the original model in models folder.
* The tests are implemented in test.py in the tests folder.
* The script mutation_tester.py is running tests on the mutations located in the mutation folder.
* The log files from the tests are saved in tests/test_results as well as a summary of all test results. These will be overwritten if the test script is run again.
* mutation_tester.py is running tests on all mutations, so it might take a long time (1-2 hours) to run completely.

