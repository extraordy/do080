#! /bin/sh
top_dir="$(dirname "$0")/../.."

if [ -z "$PYTHON" ]; then
    PYTHON="python"
fi

echo -n 'Python: '
${PYTHON} --version
${PYTHON} ${top_dir}/tests/wrapper/testrunner.py "$@"
