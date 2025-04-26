ls dist -ahl

if [ $? -eq 0 ]; then
  rattler-build upload prefix -c pypi-mirrors dist/*.conda
  rattler-build upload anaconda -o pypi-mirrors dist/*.conda
else
  echo "no new packages, skip uploading"
fi
