import random
import os 
import shutil

before_start = bytearray([ 255, 255, 255, 255, 255, 255, 255, 255 ])
after_end_normal = bytearray("\x33\x00\x00\x00/Game/Pal/Blueprint/Spawner/BP_PalSpawner_Standard", encoding="utf-8")
after_end_boss = bytearray("\x10\x00\x00\x00SphereComponent", encoding="utf-8")

# Read all names in order.
f = open("all_names.txt")
all_names = f.read().split("\n")
f.close()

# Read boss names in order.
f = open("boss_names.txt")
boss_names = f.read().split("\n")
f.close()

# Create a shuffled list of the existing names that will act as
# the replacements for each name.
shuffled_names = all_names.copy()
random.shuffle(shuffled_names)

# Bosses are weird. We're just going to shuffle to the point where we don't have to change filesize. It's good enough.
# Note: this code assumes boss_names.txt is sorted by name length.
all_lengths = []
for boss_name in boss_names:
    if len(boss_name) not in all_lengths:
        all_lengths.append(len(boss_name))
all_boss_name_dicts = []
for length in all_lengths:
    length_dict = []
    for boss_name in boss_names:
        if len(boss_name) == length:
            length_dict.append(boss_name)
    random.shuffle(length_dict)
    all_boss_name_dicts.append(length_dict)
shuffled_boss_names = []
for boss_name_dict in all_boss_name_dicts:
    shuffled_boss_names.extend(boss_name_dict)

spawner_asset = "_NormalSpawners/Pal/Content/Pal/DataTable/Spawner/DT_PalWildSpawner.uasset"
f = open(spawner_asset, "rb")
spawner_bytes = f.read()
f.close()

# get hashes for swapping purposes
name_hashes = { }
byte_index = 0x102
while byte_index < 0x2192:
    # read name size
    starting_index = byte_index
    size = spawner_bytes[byte_index]
    byte_index += 4

    # read name
    name = bytearray()
    for name_char_index in range(byte_index, byte_index + size - 1):
        name.append(spawner_bytes[name_char_index])
    byte_index += size

    # read name hash
    name_hash = [ spawner_bytes[byte_index], spawner_bytes[byte_index + 1], spawner_bytes[byte_index + 2], spawner_bytes[byte_index + 3] ]
    byte_index += 4

    # add to dictionary
    name_hashes[name.decode()] = name_hash 

# update all spawner assets
base_folder = "_NormalSpawners/Pal/Content/Pal/Blueprint/Spawner/SheetsVariant"
boss_folder = "_BossSpawners/Pal/Content/Pal/Blueprint/Spawner/SheetsVariant"
mod_folder = "Random_P/Pal/Content/Pal/Blueprint/Spawner/SheetsVariant"
sub = ""
try:
    for subfolder in mod_folder.split("/"):
        os.mkdir(sub + subfolder)
        sub += subfolder + "/"
except:
    print("Folder exists. Continuing...")

def do_stuff(folder_name):
    for asset_name in os.listdir(folder_name):
        if asset_name.endswith(".uexp"):
            continue

        #print("Reading " + asset_name)
        f = open(folder_name + "/" + asset_name, "rb")
        base_bytes = f.read()
        f.close()

        #print(base_bytes)
        start_index = base_bytes.index(before_start) + len(before_start)
        if folder_name == base_folder:
            end_index = base_bytes.index(after_end_normal)
        else:
            end_index = base_bytes.index(after_end_boss)

        new_bytes = bytearray()
        new_bytes.extend(bytearray(base_bytes[:start_index]))

        # change the texts
        base_chunk_byte_count = 0
        new_chunk_byte_count = 0
        byte_index = start_index
        while byte_index < end_index:
            # read name size
            starting_index = byte_index
            size = base_bytes[byte_index]
            byte_index += 4

            # read name
            name = bytearray()
            for name_char_index in range(byte_index, byte_index + size - 1):
                name.append(base_bytes[name_char_index])
            byte_index += size

            # read name hash
            name_hash = [ base_bytes[byte_index], base_bytes[byte_index + 1], base_bytes[byte_index + 2], base_bytes[byte_index + 3] ]
            byte_index += 4

            try:
                # debug
                #print("Name of length " + str(size) + " is " + str(name.decode()) + " with hash " + str(name_hash))

                # if this name has a map, swap it
                # else, copy it over
                if name.decode() in all_names:
                    shuffled_name = shuffled_names[all_names.index(str(name.decode()))]
                    shuffled_hash = name_hashes[shuffled_name]

                    new_bytes.append(len(shuffled_name) + 1)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.extend(bytearray(shuffled_name, encoding="utf-8"))
                    new_bytes.append(0)
                    new_bytes.append(shuffled_hash[0])
                    new_bytes.append(shuffled_hash[1])
                    new_bytes.append(shuffled_hash[2])
                    new_bytes.append(shuffled_hash[3])
                    new_chunk_byte_count += 4 + len(shuffled_name) + 1 + 4
                    #print("Swapped " + str(name.decode()) + " with " + shuffled_name)
                elif name.decode() in boss_names:
                    shuffled_name = shuffled_boss_names[boss_names.index(str(name.decode()))]
                    shuffled_hash = name_hashes[shuffled_name]

                    new_bytes.append(len(shuffled_name) + 1)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.extend(bytearray(shuffled_name, encoding="utf-8"))
                    new_bytes.append(0)
                    new_bytes.append(shuffled_hash[0])
                    new_bytes.append(shuffled_hash[1])
                    new_bytes.append(shuffled_hash[2])
                    new_bytes.append(shuffled_hash[3])
                    new_chunk_byte_count += 4 + len(shuffled_name) + 1 + 4
                    #print("Swapped " + str(name.decode()) + " with " + shuffled_name)
                else:
                    new_bytes.append(len(name) + 1)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.append(0)
                    new_bytes.extend(bytearray(name))
                    new_bytes.append(0)
                    new_bytes.append(name_hash[0])
                    new_bytes.append(name_hash[1])
                    new_bytes.append(name_hash[2])
                    new_bytes.append(name_hash[3])
                    new_chunk_byte_count += 4 + len(name) + 1 + 4
                    #print("Left " + str(name.decode()) + " alone")

                base_chunk_byte_count += 4 + len(name) + 1 + 4
            except:
                print("Failed to decode")

        new_bytes.extend(bytearray(base_bytes[end_index:]))

        # update magic numbers
        chunk_difference = new_chunk_byte_count - base_chunk_byte_count
        #print(str(base_chunk_byte_count) + " " + str(new_chunk_byte_count) + " " + str(chunk_difference))

        basis_name_diff = 46
        name_diff = len(asset_name) - basis_name_diff
        bytes_from_the_front = [0x1C, 0x96 + name_diff, 0x9E + name_diff, 0xA2 + name_diff, 0xFE + name_diff, 0x102 + name_diff, 0x116 + name_diff]
        for one_byte in bytes_from_the_front:
            base_byte = base_bytes[one_byte] + (base_bytes[one_byte + 1] << 8) + (base_bytes[one_byte + 2] << 16) + (base_bytes[one_byte + 3] << 24)
            base_byte += chunk_difference

            new_bytes[one_byte] = base_byte & 255
            new_bytes[one_byte + 1] = (base_byte & (255 << 8)) >> 8
            new_bytes[one_byte + 2] = (base_byte & (255 << 16)) >> 16
            new_bytes[one_byte + 3] = (base_byte & (255 << 24)) >> 24

        bytes_from_the_back = [ (0xAE0 - 0x830), (0xAE0 - 0x890), (0xAE0 - 0x8F0), (0xAE0 - 0x950), (0xAE0 - 0x9B0), (0xAE0 - 0xA10)]
        for one_byte in bytes_from_the_back:
            if folder_name == boss_folder or "sanctuary" in asset_name:
                one_byte -= 8
            base_byte = base_bytes[len(base_bytes) - one_byte] + (base_bytes[len(base_bytes) - one_byte + 1] << 8) + (base_bytes[len(base_bytes) - one_byte + 2] << 16) + (base_bytes[len(base_bytes) - one_byte + 3] << 24)
            base_byte += chunk_difference

            new_bytes[len(new_bytes) - one_byte] = base_byte & 255
            new_bytes[len(new_bytes) - one_byte + 1] = (base_byte & (255 << 8)) >> 8
            new_bytes[len(new_bytes) - one_byte + 2] = (base_byte & (255 << 16)) >> 16
            new_bytes[len(new_bytes) - one_byte + 3] = (base_byte & (255 << 24)) >> 24

        # write to file
        f = open(mod_folder + "/" + asset_name, "wb")
        f.write(bytearray(new_bytes))
        f.close()

        # copy corresponding uexp
        uexp_name = asset_name.split(".")[0] + ".uexp"
        shutil.copy(folder_name + "/" + uexp_name, mod_folder + "/" + uexp_name)

do_stuff(base_folder)
do_stuff(boss_folder)
