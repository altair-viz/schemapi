Releasing a New Version
=======================

1. Change the MAJOR, MINOR, MICRO version numbers in setup.py as appropriate

2. Set ISRELEASE=True in setup.py

3. Run

       python setup.py build
   
   to generate schemapi/version.py

4. Tag the release; e.g.

       git tag -a v0.1 -m "version 0.1 release"

   and push tag to origin

5. Upload to PyPI (requires jakevdp's permissions)

       python setup.py sdist upload

6. Update to the next minor version in setup.py, and set ISRELEASE=False

7. Commit to master and push to origin
