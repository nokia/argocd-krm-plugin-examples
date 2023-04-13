#!/bin/bash
resourceList=$(cat) # read the `kind: ResourceList` from stdin
shasum=$(find "../files" -type f -exec sha256sum {} \; | sha256sum | cut -d ' ' -f 1)
#shasum=$(sha256sum | cut -d ' ' -f 1  )

echo "$resourceList"| /home/argocd/cmp-server/plugins/yq '(.items[] | select (.kind == "Deployment") ).spec.template.metadata.annotations.groovyChecksum |="'$shasum'"'

