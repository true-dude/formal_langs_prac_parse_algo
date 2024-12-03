#!/bin/bash

$passed = 0
for test_ent in tests/*/;
do
    cp ${test_ent}in.txt in
    python3 parse.py > /dev/null
    output="$(cat out)"
    expected="$(cat "${test_ent}out.txt")"
    let "passed+=1"
    if [ "$output" != "$expected" ]; then
        echo "Output differs on ${test_ent}"

        echo "expected:"
        echo "${expected}"

        echo "program output:"
        echo "${output}"
        let "passed-=1"
    fi
done
echo $passed / 19
echo OK
