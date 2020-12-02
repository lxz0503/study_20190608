
ISSUE_HTML=$1

echo "Jira filter: http://jira.wrs.com/issues/?filter=$2"
curl -u "svc-ssp:jiradefect" http://jira.wrs.com/issues/?filter=$2 > $ISSUE_HTML
START_LINE=`awk '/id="issuetable"/{print NR - 1}' $ISSUE_HTML`
END_LINE=`awk '/\/table/{print NR - 1}' $ISSUE_HTML`
let END_LINE+=2
echo "Crop to get content between lines $START_LINE and $END_LINE of $ISSUE_HTML"
sed -i "${END_LINE},\$d" $ISSUE_HTML
sed -i "1,${START_LINE}d" $ISSUE_HTML

# exchange /image to http://jira.wrs.com/image
sed -i "s/\/images/http\:\/\/jira.wrs.com\/images/g" $ISSUE_HTML

# exchange /browse to http://jira.wrs.com/browse
sed -i "s/\/browse/http\:\/\/jira.wrs.com\/browse/g" $ISSUE_HTML

# exchange /secure to http://jira.wrs.com/secure
sed -i "s/\/secure/http\:\/\/jira.wrs.com\/secure/g" $ISSUE_HTML

# change first column width to 100
sed -i "s/td class=\"nav issuekey\"/td class=\"nav issuekey\" width=\"100\"/g" $ISSUE_HTML

# change font style to Arial
sed -i 's/issuetable\"/issuetable\" style=font-family\:Arial/g' $ISSUE_HTML
