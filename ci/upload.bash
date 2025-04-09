ls dist -ahl

if [ $? -eq 0 ]; then
  rattler-build upload prefix -c pypi-mirrors dist/*.conda
else
  echo "on packages, skip uploading"
fi
