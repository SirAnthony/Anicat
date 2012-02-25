"""
Test runner with code coverage.
Falls back to django simple runner if coverage-lib not installed
Found in internets
"""
import os

from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings

SKIP_DIRS = ['migrations', 'tests']

class CoveragedRunner(DjangoTestSuiteRunner):

    def run_tests(self, test_labels, *args, **kwargs):
        try:
            from coverage import coverage as Coverage
        except ImportError:
            return super(CoveragedRunner, self).run_tests(test_labels, *args, **kwargs)
        else:
            coverage = Coverage()
            coverage.start()
            test_results = super(CoveragedRunner, self).run_tests(test_labels, *args, **kwargs)
            coverage.stop()
            self.cover_results(coverage, test_labels, test_results)
            return test_results

    def cover_results(self, coverage, test_labels, test_results):
        coverage_modules = []
        for app in test_labels:
            try:
                module = __import__(app, globals(), locals(), [''])
            except ImportError:
                coverage_modules = None
                break
            if module:
                base_path = os.path.join(os.path.split(module.__file__)[0], "")
                for root, dirs, files in os.walk(base_path):
                    for sd in SKIP_DIRS:
                        if sd in dirs:
                            dirs.remove(sd)
                    for fname in files:
                        if fname.endswith(".py") and os.path.getsize(os.path.join(root, fname)) > 1:
                            try:
                                mname = os.path.join(app, os.path.join(root, fname).replace(base_path, ""))
                                coverage_modules.append(mname)
                            except ImportError:
                                pass #do nothing

        if coverage_modules or not test_labels:
            coverage.html_report(coverage_modules, directory=settings.COVERAGE_REPORT_PATH)


