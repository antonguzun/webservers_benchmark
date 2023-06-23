ln -sf `ls reports/*.json | sort -n | tail -1 | awk -F/ '{print $NF}'` reports/latest
