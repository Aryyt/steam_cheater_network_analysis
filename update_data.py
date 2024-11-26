import requests
import yaml
import pandas as pd
import pickle
from gather_user_data import get_full_data_on_player as alternative_data_gather




def main():
    with open("config/api.yaml", "r") as file:
            api = yaml.safe_load(file)
            api_key = api['api']
        
    df_full_data = pd.read_pickle('data/full_user_data_new.pkl')
    print(df_full_data)
    
    queue_path = "./data/queue.pkl"
    err_path = "./data/errors.pkl"
    
    with open(queue_path, "rb") as pkl:
        queue = pickle.load(pkl)
    itter = 0
    calls = 0
    good_response = True
    print(len(queue))
    c = alternative_data_gather(api_key, queue[1])
    print(c)
    while itter < 1000:
        
        skip = False
        itter += 1
        id = queue.pop(0)
        candidate = alternative_data_gather(api_key, id)
        calls += 5
        
        # reqquest fails
        if not isinstance(candidate, pd.DataFrame):
            with open(err_path, "rb") as pkl:
                err = pickle.load(pkl)
            err.append(id)
            with open(err_path, "wb") as pkl:
                pickle.dump(err, pkl)
            
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            df_full_data.to_pickle('./data/full_user_data_new.pkl')
            alternative = alternative_data_gather(api_key, id)
            calls += 5
            if isinstance(alternative, pd.DataFrame):
                df_full_data = pd.concat([df_full_data, alternative])
            skip = True
            
        # print(candidate)
        # Add freinds to the queue
        if skip == False:
            id_list = df_full_data['steamid']
            for friend in candidate['Friends List'].iloc[0]:
                if friend not in id_list.unique():
                    # print('hit')
                    queue.append(friend)
                
            # Concatonate dataframes
            df_full_data = pd.concat([df_full_data, candidate])
        
        # Print iteration every 50 iterations
        if itter % 25 == 0:
            print(itter)

        # Save and print every 500 calls
        if calls != 0 and calls % 500 == 0:
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            
            print("calls made: ", calls)
            df_full_data.to_pickle('./data/full_user_data_new.pkl')
        if calls == 99000:
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            
            print("calls made: ", calls)
            df_full_data.to_pickle('./data/full_user_data_new.pkl')
            break
            
    with open(queue_path, "wb") as pkl:
        pickle.dump(queue, pkl)
    df_full_data.to_pickle('./data/full_user_data_new.pkl')
            
        
    
if __name__ == "__main__":
    main()


# err = []
# err_path = "./data/errors.pkl"
# with open(err_path, "wb") as pkl:
#         pickle.dump(err, pkl)




# queue = []
# df = pd.read_pickle('./data/full_user_data.pkl')

# for friends in df['Friends List']:
#     for friend in friends:
#         queue.append(friend)
        
# queue_path = "./data/queue.pkl"

# with open(queue_path, "rb") as pkl:
#     l = pickle.load(pkl)
    
# print(l)







# MAYBE USEFULL FOR THE FUTURE


# id_list = df['steamid']
# print(id_list)
# # print(df.iloc[2])
# id = df.iloc[2]['steamid']
# friends2 = df.iloc[2]['Friends List']
# print(friends2, id)

# print('sampled user in ids: ', id in id_list.unique())
# print('first freind in ids: ', friends2[0] in id_list.unique())

# queue = []

# with open(queue_path, "a") as pkl:
#     pickle.dump(queue, pkl)
# queue_path = "./data/queue.pkl"
# with open(queue_path, "a") as pkl:
#     pickle.dump(queue, pkl)
    
# with open(queue_path, "a") as pkl:
#     queue = pickle.load(pkl)
# print(queue)


    
