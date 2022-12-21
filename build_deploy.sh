rm -r dist ;
python setup.py sdist bdist_wheel ;
if twine check dist/* ; then
  # ./build_deploy.sh --test for test run
  if [ "$1" = "--test" ] ; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
  else
    twine upload dist/* ;
  fi
fi
