import random
import argparse

from fb_util import FacebookGroupPoster
from helpers import load_data

parser = argparse.ArgumentParser()
parser.add_argument("--script_ids", type=str, help="Script ids, separated by comma")

args = parser.parse_args()
script_ids = [int(x) for x in args.script_ids.split(',')]

scripts, groups, profiles = load_data('content.xlsx')

for script_id, data in scripts.items():
    if script_id in script_ids:
        content = data['content']
        img_folder = data['image_folder']
        grps = data['groups'].split('\n')


        for group in grps:
            # randomly pick a member for that group
            member_name = random.choice(groups[group]['members'])
            profile = profiles[member_name]

            poster = FacebookGroupPoster(
                profile['data_dir'],
                profile['profile_name'],
            )

            poster.post_to_group(
                group,
                content,
                img_folder
            )

            poster.close()