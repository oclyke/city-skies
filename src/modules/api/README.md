# city skies api

the api is meant to monitor and control an instance of city-skies.

all endpoint urls follow the format ```http://{address}/{path}``` where:
* **{address}** is the socket address of the instance
* **{path}** identifies the resource within the city-skies instance

the following paths are available on any city-skies instance

path | json? | description
---|---|---
/index | ✅ | provides api support information for this instance

## api versioning

the api is versioned to allow for forward compatibility. apis are maintained according to semantic versioning. because consumers are concerned only with compatibility only the major version will be used to identify the api in the interface.

all api endpoint urls follow the format ```http://{address}/api/{api major version}/{path}``` where:
* **{api major version}** is used to identify the api being used
* **{path}** is used to locate a particular resource within this api version

## api versions

version | status
---|---
v0 | production

detailed below are specifics for each major version of the api. 

### v0

path | method | json? | payload | description
---|---|---|---|---
/audio | GET | ✅ |  | lists information about audio sources
/audio/source | PUT | ✅ | { id: "source id" } | select source "source id", or no source if id is set to null.
/audio/source/\<id> | GET | ✅ |  | gets information about the source "id"
/audio/source/\<source id>/variable/\<variable id> | GET | ✅ |  |gets information about the variable "variable id" within source "source id"
/audio/source/\<source id>/variable/\<variable id> | PUT | ✅ | { value: "value" } | sets the value of the variable "variable id" within source "source id" to "value" if possible
/audio/source/\<source id>/private_variable/\<variable id> | GET | ✅ |  | gets information about the private variable "variable id" within source "source id"
/audio/source/\<source id>/private_variable/\<variable id> | PUT | ✅ | { value: "value" } | sets the value of the private variable "variable id" within source "source id" to "value" if possible
/global | GET | ✅ |  | gets global information about the instance
/global/variable/\<variable id> | GET | ✅ |  | gets information about the glboal variable "variable id"
/global/variable/\<variable id> | PUT | ✅ | { value: "value" } | sets the global variable "variable id" to "value" if possible
/output | GET | ✅ |  | get info about the output
/output/stack/\<stack id> | GET | ✅ |  | get info about 
/output/stack/\<stack id> | PUT | ✅ |  | activate stack "stack id"
/output/
/output/stack/\<stack id>/layer | PUT | ✅ | { shard_uuid: "shard_uuid" } | add a layer to the stack "stack id" using the settings in the payload
/output/stack/\<stack id>/layer/\<layer id> | DELETE | ✅ |  | remove layer "layer id" from the stack "stack id"
/output/stack/\<stack id>/layer/\<layer id>/config | PUT | ✅ | { "active": boolean, "index": int, "use_local_palette": boolean } | merge new configuration into layer "layer id" configuration
/output/stack/\<stack id>/layer/\<layer id>/variable/\<variable id> | GET | ✅ |  | get variable information for "variable id" in layer "layer id" in stack "stack id"
/output/stack/\<stack id>/layer/\<layer id>/variable/\<variable id> | PUT | ✅ | { value: "value" } | set variable value for "variable id" in layer "layer id" in stack "stack id"
/output/stack/\<stack id>/layer/\<layer id>/private_variable/\<variable id> | GET | ✅ |  | get private variable information for "variable id" in layer "layer id" in stack "stack id"
/output/stack/\<stack id>/layer/\<layer id>/private_variable/\<variable id> | PUT | ✅ | { value: "value" } | set variable value for "variable id" in layer "layer id" in stack "stack id"
/shards |  |  |  | todo
