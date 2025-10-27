import sys
import os
import unittest
from unittest import TestLoader, TestSuite, TextTestRunner

#Import all test classes from your database test file
from tests.test_database import (
    TestPlatform,
    TestUIComponents,
    TestDatabaseSetup,
    TestAnimalRFIDMethods,
    TestCageFunctions,
    TestGroupFunctions
)

def test_database_suite_execution():
    """Ensures all database-related tests pass when executed together."""

    # Load all database tests into one suite
    loader = TestLoader()
    suite = TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestAnimalRFIDMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestCageFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestGroupFunctions))

    # Run the suite
    runner = TextTestRunner(verbosity=2)
    result = runner.run(suite)

    #If ANY test fails → pytest will mark THIS test as failed
    assert result.wasSuccessful(), "Database test suite failed"
