# unix port

this is the unix port of city-skies.

# example filesystem

the filesystem is used to persist settings.

path | name | description
---|---|---
/system | system | generic info about the system
/system/identity | identity | identity info
/system/identity/tag | tag | a human-readable tag for the system
/system/identity/id | id | a (reasonably) unique id for the system, probably based off of MAC address or similar
/audio | audio | generic audio information
/audio/master_volume | master volume | master volume for audio modules
/audio/sources | audio sources | info about available audio sources
/audio/source/\<source\> | \<source\> | info about a specific audio source
/audio/source/\<source\>/variables | \<source\> variables | index of dynamically registered variables for this audio source
/audio/source/\<source\>/variable/\<variable\> | \<source\> \<variable\> | dynamic declaration of a variable for this audio source
