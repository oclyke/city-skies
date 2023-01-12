import semver
import identity
import audio
import speed
import shard
import netman
import csble


# firmware version
fw_version = semver.SemanticVersion.from_semver("0.0.0")

# create the BLE peripheral
ble = csble.CSBLE()

# data managers
identity = identity.IdentityInfo(".cfg/identity")
audio_manager = audio.AudioManager(".cfg/audio")
speed_manager = speed.SpeedManager(".cfg/speed")
shard_manager = shard.ShardManager(".cfg/shards")
network_manager = netman.NetworkManager(".cfg/network")
