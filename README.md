# Adam bot
## About
## Tests
Coverage can be verified using the Coverage.py tool.<br>
[docs](https://coverage.readthedocs.io/en/coverage-5.3/)<br>
[github](https://github.com/nedbat/coveragepy/tree/coverage-5.3)<br><br>

### Install pytest & coverage
**pytest module**
```sh
pip install pytest
```
**coverage module**
```sh
pip install coverage
```
<br>

### Running tests
```sh
pytest <path_to_test_files>
```
<br>

### Running coverage analysis
```sh
coverage run -m pytest <path_to_test_files>
```
make format prettier 
```sh
coverage run -m pytest <path_to_test_files>
coverage html
```
then you can find html pages with coverage reports here `./htmlcov`.
For more info please checkout [the documentation](https://coverage.readthedocs.io/en/coverage-5.3/)
<br>
<br>


## 3rd party API used
[github rest docs](https://docs.github.com/en/free-pro-team@latest/rest/overview/resources-in-the-rest-api)
[telegram bot api docs](https://core.telegram.org/bots/api#sendmessage)