#!/bin/bash

rm -rf .git
docker login my-dockerregistry --username <username> --password <password>
docker build -t my-dockerregistry/apps/webserver:${BUILD_ID} .
docker push my-dockerregistry/apps/webserver:${BUILD_ID}

export RANCHER_ACCESS_KEY=<API Access Key>
export RANCHER_SECRET_KEY=<API Secret Key>
export RANCHER_URL=<API URL>
export PROJECT_ID=<Project Id>
export ID=<Stack Id>

cat rancher-api.json | sed "s/webserver/webserver:$BUILD_ID/g" > build.json

#UPGRADE CONTAINER IMAGE
curl -s -u "${RANCHER_ACCESS_KEY}:${RANCHER_SECRET_KEY}" \
-X POST \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
-d '@build.json' \
"http://${RANCHER_URL}:8081/v2-beta/projects/${PROJECT_ID}/stacks/${ID}?action=upgrade"

#GET STATUS
until [ "$(curl -s -u "${RANCHER_ACCESS_KEY}:${RANCHER_SECRET_KEY}" \
  -X GET -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  "http://${RANCHER_URL}:8081/v2-beta/projects/${PROJECT_ID}/stacks/${ID}" |grep -o "upgraded")" = "upgraded" ]

do
  sleep 2
  echo " "
  echo "Waiting For Upgraded is Ready..."

done
  echo "Ready to Upgraded..."



#FINISH UPGRADE ACTION
curl -s -u "${RANCHER_ACCESS_KEY}:${RANCHER_SECRET_KEY}" \
-X POST \
"http://${RANCHER_URL}:8081/v2-beta/projects/${PROJECT_ID}/stacks/${ID}?action=finishupgrade"

docker image rm -f `docker images |grep my-dockerregistry | awk '{print $3}'`
echo "OK"

