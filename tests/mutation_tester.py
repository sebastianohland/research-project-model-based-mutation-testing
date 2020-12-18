import csv
import time
import subprocess
from subprocess import TimeoutExpired
import logging
import sys
import os


def import_csv(filepath):
    with open(filepath) as f:
        reader = csv.reader(f)
        data = []
        for line in reader:
            data.extend(line)
    return data


def set_up_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel('DEBUG')
    os.makedirs(os.path.dirname('test_results/'), exist_ok=True)
    file_handler = logging.FileHandler('test_results/{}.log'.format(name), mode='w')
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    return logger


def run_command(cmd, timeout):
    """Runs single mutation test through command line using subprocess run. """
    returncode = -1
    process_start_time = time.time()
    try:
        process = subprocess.run(cmd, timeout=timeout, capture_output=False, universal_newlines=True, shell=True)
        returncode = process.returncode
    except TimeoutExpired:
        print("PROCESS TIMED OUT!!!")
    runtime = time.time() - process_start_time
    return returncode, runtime


def run_tests(folder_path, stop_condition, altwalker_timeout, process_timeout, log_name):
    """Testing all mutations in folder based on the stop condition given in the parameters.
    The test function first performs a check to see if the model is syntactically valid and tests only  valid models.
    Writes log file with results for each mutation operator and summary of all mutation operators."""

    # Setting up logger. Writes to console and to file in the current folder
    logger = set_up_logger(log_name)

    # Imports list with model names
    models = import_csv(folder_path + "namelist.csv")

    # Initializing lists for saving models depending on test result
    alive_check_models = []     # Model passes check
    killed_check_models = []    # Model killed by check (syntactically invalid)
    alive_test_models = []      # Model passes both check and tests
    killed_test_models = []     # Tests fail
    killed_crash_models = []    # Testing crashes and raises exception
    killed_time_models = []     # Model gets stuck and times out (no exception)
    cl_error_models = []        # Wrong input from command line

    logger.info("CHECKING MODELS................................................................................\n")
    start_check_time = time.time()
    for i in models:
        logger.name = i
        logger.info("Checking model {}...".format(i))

        # Always perform checks with "random(edge_coverage(100))"
        returncode, runtime = run_command('altwalker check -m {}{}.json "random(edge_coverage(100))"'
                                          .format(folder_path, i, stop_condition),
                                          timeout=process_timeout)

        # If passing check model
        if returncode == 0:
            alive_check_models.append(i)
            logger.info("CHECK PASSED in {} seconds. Adding {} to alive check models.\n".format(round(runtime, 2), i))

        # If failing check model
        else:
            logger.error("CHECK FAILED in {} seconds. Adding {} to killed check models.\n".format(round(runtime, 2), i))
            killed_check_models.append(i)

    check_time = round(time.time() - start_check_time, 2)
    n_alive_check_models = len(alive_check_models)
    n_killed_check_models = len(killed_check_models)
    logger.name = log_name
    logger.info("Checking finished in {} seconds! {} models passed, {} models failed.\n".format(check_time,
                                                                                                n_alive_check_models,
                                                                                                n_killed_check_models))

    # Testing only models that passed check
    logger.info("TESTING MODELS....................................................................................\n")
    start_test_time = time.time()
    for i in alive_check_models:
        logger.name = i
        logger.info("Testing model {}...".format(i))

        returncode, runtime = run_command('altwalker online -m {}{}.json "{}" ../tests'
                                          .format(folder_path, i, stop_condition), process_timeout)

        # Tests ran successfully and passed.
        # Returncode will also be 0 if tests get stuck in a loop and altwalker times out.
        if returncode == 0:
            if runtime < altwalker_timeout:
                # Testing finished under altwalker time parameter
                logger.info("TEST PASSED in {} seconds. Adding {} to alive test models.\n".format(round(runtime, 2), i))
                alive_test_models.append(i)
            else:
                # Test probably got stuck
                logger.error("TEST TIMED OUT in {} seconds. Adding {} to timed out test models.\n".format(round(runtime, 2), i))
                killed_time_models.append(i)

        # Command ran successfully but tests failed
        elif returncode == 1:
            logger.error("TEST FAILED in {} seconds. Adding {} to killed test models.\n".format(round(runtime, 2), i))
            killed_test_models.append(i)

        # Command line error
        elif returncode == 2:
            logger.error("CL ERROR. TEST DID NOT RUN. Adding {} to cl error models.\n".format(round(runtime, 2), i))
            cl_error_models.append(i)

        # Command causes testing to crash (AltWalker or GraphWalker error)
        elif returncode == 3 or returncode == 4:
            logger.error("TEST CRASHED in {} seconds. Adding {} to crashed test models.\n".format(round(runtime, 2), i))
            killed_crash_models.append(i)

        else:
            logger.error("Incorrect return code from model {}\n".format(i))

    tot_test_time = round(time.time() - start_test_time, 2)
    n_total_models = len(models)
    n_alive_test_models = len(alive_test_models)
    n_killed_test_models = len(killed_test_models)
    n_killed_crash_models = len(killed_crash_models)
    n_killed_time_models = len(killed_time_models)
    n_cl_error_models = len(cl_error_models)

    # Appending lists of mutations at the end of log file
    logger.name = log_name
    logger.info("Testing finished in {} seconds! {} models passed, {} models failed, {} models crashed, {} models timed out.\n"
                .format(tot_test_time, n_alive_test_models, n_killed_test_models, n_killed_crash_models, n_killed_time_models))

    logger.info("RESULTS...........................................................................................\n")

    logger.info("Total models: {}\n".format(n_total_models))

    logger.info("Models that were syntactically invalid (failed altwalker check): ({})\n{}\n"
                .format(n_killed_check_models, "\n".join(killed_check_models)))

    logger.info("Models that were killed by failing one (or more) of the tests: ({})\n{}\n"
                .format(n_killed_test_models, "\n".join(killed_test_models)))

    logger.info("Models that were killed by crashing the tests: ({})\n{}\n"
                .format(n_killed_crash_models, "\n".join(killed_crash_models)))

    logger.info("Models that were killed by timing out: ({})\n{}\n"
                .format(n_killed_time_models, "\n".join(killed_time_models)))

    logger.info("Models that encoutered command line errors (should be 0 if not faulty input from cl): ({})\n{}\n"
                .format(n_cl_error_models, "\n".join(cl_error_models)))

    logger.info("Models that are still alive: ({})\n{}\n"
                .format(n_alive_test_models, "\n".join(alive_test_models)))

    return [
        log_name,
        n_total_models,
        n_killed_check_models,
        n_killed_test_models,
        n_killed_crash_models,
        n_killed_time_models,
        n_cl_error_models,
        n_alive_test_models
    ]


def main():

    re_folder_path = "../mutations/RE_Mutations/"
    rv_folder_path = "../mutations/RV_Mutations/"
    red_folder_path = "../mutations/RED_Mutations/"
    ceso_folder_path = "../mutations/CESO_Mutations/"
    cesi_folder_path = "../mutations/CESI_Mutations/"
    rafe_folder_path = "../mutations/RAFE_Mutations/"
    raf_folder_path = "../mutations/RAF_Mutations/"

    # Altwalker time_duration is given in stop condition. Model assumed to be stuck in a loop if this happens
    altwalker_timeout = 200
    # Process will raise TimeoutExpiredExecption if reaches this timeout (should not happen)
    process_timeout = 500
    # Uses quick_random stop condition for tests, random will be used for the checks
    stop_condition = "quick_random(edge_coverage(100) or time_duration({}))".format(altwalker_timeout)

    # The tests are run here
    re_results = run_tests(re_folder_path, stop_condition, altwalker_timeout, process_timeout, "RE_results")
    rv_results = run_tests(rv_folder_path, stop_condition, altwalker_timeout, process_timeout, "RV_results")
    red_results = run_tests(red_folder_path, stop_condition, altwalker_timeout, process_timeout, "RED_results")
    ceso_results = run_tests(ceso_folder_path, stop_condition, altwalker_timeout, process_timeout, "CESO_results")
    cesi_results = run_tests(cesi_folder_path, stop_condition, altwalker_timeout, process_timeout, "CESI_results")
    rafe_results = run_tests(rafe_folder_path, stop_condition, altwalker_timeout, process_timeout, "RAFE_results")
    raf_results = run_tests(raf_folder_path, stop_condition, altwalker_timeout, process_timeout, "RAF_results")

    # Making summary table
    headers = ["mutator", "tot_m", "invalid_m", "killed_test_m", "killed_crash_m", "killed_time_m", "cl_error_m", "alive_m"]
    summary_table = [headers, re_results, rv_results, red_results, ceso_results, cesi_results, rafe_results, raf_results]

    # Outputs to csv
    with open("test_results/summary.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(summary_table)


if __name__ == "__main__":
    main()
