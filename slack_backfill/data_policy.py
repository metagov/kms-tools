from __init__ import app
import json

data_consent_field_id = "Xf0650JBMA1Y"


def get_user_status(client):
    result = client.users_list()
    users = result["members"]

    opted_out = []
    opted_in = []
    count = 0

    print("Starting data consent monitoring tool...")
    print(f"Found {len(users)} users")

    for user in users:
        # if 'profile' in user:
        #     if 'title' in user['profile']:
        #         title = user['profile']['title']
        #         if title:
        #             if (":red_circle:" in title) or ("🔴" in title):
        #                 opted_out.append(user['id'])

        resp = client.users_profile_get(user=user["id"]).data
        fields = resp['profile']['fields']
        title = resp['profile']['title']
        data_consent_field = fields.get(data_consent_field_id, None)
        opt_out = False
        opt_in = False

        if data_consent_field:
            data_consent_value = data_consent_field["value"]
            
            if (":red_circle:" in data_consent_value) or ("🔴" in data_consent_value):
                opted_out.append(user['id'])
                opt_out = True
                reason = f"via data consent field '{data_consent_value}'"
                
            if (":large_green_circle:" in data_consent_value) or ("🟢" in data_consent_value):
                opted_in.append(user['id'])
                opt_in = True
                

        if (":red_circle:" in title) or ("🔴" in title):
            opted_out.append(user['id'])
            opt_out = True
            reason = f"via title '{title}'"

        count += 1

        print(f"{'🔴' if opt_out else '🟢' if opt_in else '❔'} {user.get('real_name', user['name'])} {reason if opt_out else ''}")
        
        # print(f"Processed {count} users") if (count % 100) == 0 else None

    print(f"{len(opted_in)} / {len(users)} ({round(len(opted_in) / len(users) * 100, 1)}%) users opted into data export")
    print(f"{len(opted_out)} / {len(users)} ({round(len(opted_out) / len(users) * 100, 1)}%) users opted out of data export")

    return opted_out, opted_in
    

opted_out_users, opted_in_users = get_user_status(app.client)

with open("user_status.json", "w") as f:
    json.dump(
        {
            "opted_in": opted_in_users,
            "opted_out": opted_out_users
        }, 
        f, 
        indent=2
    )