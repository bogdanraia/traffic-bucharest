import matplotlib.pyplot as plt
import seaborn as sns
import xml.etree.ElementTree as ET
import os
import numpy as np
import pandas as pd
import csv

if __name__ == "__main__":
    folders = [r"C:\self\School\Master\Disertation\code\RESCO\final_results\IDQN-tr0-unirii-0-drq-wait", r"C:\self\School\Master\Disertation\code\RESCO\final_results\IA2C-tr0-unirii-0-drq_norm-wait_norm"]
    models = ["IDQN", "IA2C", ]

    traffic_signals_names = {
        "cluster_254337786_31404743": "Unirii x Mircea Voda",
        "GS_cluster_14485274_151021003_2335517648_254337785_#1more": "Unirii x Traian",
        "cluster_537912_578689": "Unirii x Blaga",
        "2404247020": "Romana x Magheru",
        "2404247023": "Romana x Cataragiu",
        "60290346": "Romana x Dacia E",
        "6264801635": "Romana x Dacia W",
        "joinedS_2161171951_3142063530_cluster_254497599_256671507": "Pantelimon x Fundeni",
        "2191210759": "Morarilor x Vergului",
        "cluster_256681114_256681320": "Morarilor x Basarabia",
        "GS_cluster_2191222577_2191248297_256680759_256680871": "Chisinau x Basarabia",
        "GS_cluster_254429697_254429698": "Grigorescu x Brancusi",
        "6251810840": "Delfinului x Pantelimon N-E",
        "2069616278": "Deflinului x Pantelimon N-W",
        "256602972": "Delfinului x Pantelimon S-W",
        "254439046": "Pantelimon Reverse",
        "cluster_14460671_8358559169": "Iancului x Mihai Bravu (small)",
        "cluster_2160307875_6909607558_8358559154_8358559159_#1more": "Iancului x Mihai Bravu (large)",
        "123332877": "Muncii S-E",
        "123332788": "Muncii N-E",
        "J3": "Muncii W",
    }

    # Obtained by inspection in SUMO/running the models
    # Overkill to include them as folders and dataframes

    fixed_results = {
        "Unirii":{
            "fixed": 57.32,
            "maxWave": 46.12,
            "maxPressure": 58.73,
        },
        "Romana": {
            "fixed": 23.04,
            "maxWave": 14.37,
            "maxPressure": 13.10,
        },
        "Pantelimon": {
            "fixed": 73.54,
            "maxWave": 47.56,
            "maxPressure": 55.61,
        }
    }

    current_map = 'Unirii'
    junctions = ['Unirii x Mircea Voda', 'Unirii x Traian', 'Unirii x Blaga']

    nr_episodes = 100
    plt.style.use('ggplot')

    waitingTime = pd.DataFrame({
    })

    timeLoss = pd.DataFrame({
    })

    duration = pd.DataFrame({
    })

    episode_rewards = {}
    episode_maxQ = {}
    episode_queue = {}

    for idx, folder in enumerate(folders):
        episode_waitingTime = []
        episode_timeLoss = []
        episode_duration = []

        for i in range(1, nr_episodes + 1):
            trip_waitingTime = []
            trip_timeLoss = []
            trip_duration = []

            trip_rewards = {}
            trip_maxQ = {}
            trip_queue = {}
            
            current_trips = ET.parse(r"{}".format(os.path.join(folder, f"tripinfo_{i}.xml")))
            root = current_trips.getroot()
            trips_from_root = root.findall('tripinfo')
            for trip in trips_from_root:
                trip_waitingTime.append(float(trip.attrib['waitingTime']))
                trip_timeLoss.append(float(trip.attrib['timeLoss']))
                trip_duration.append(float(trip.attrib['duration']))

            episode_waitingTime.append(np.mean(trip_waitingTime))
            episode_timeLoss.append(np.mean(trip_timeLoss))
            episode_duration.append(np.mean(trip_duration))

            with open(r"{}".format(os.path.join(folder, f"metrics_{i}.csv"), mode ='r')) as file:
                current_metrics = csv.reader(file)
                for lines in current_metrics:
                    appearances = {}
                    for idx2, word in enumerate(lines):
                        if idx2 == 0 or idx2 == len(lines) - 1:
                            continue
                        word = word.split(':')
                        word[0] = word[0].strip("{")
                        word[0] = word[0].strip("}")
                        word[0] = word[0].strip('\'')
                        word[0] = word[0].strip()
                        word[0] = word[0].strip('\'')
                        word[1] = word[1].strip('}')
                        if word[0] in traffic_signals_names:
                            word[0] = traffic_signals_names[word[0]]
                        word[0] = word[0] + ' ' + models[idx]
                        if word[0] in appearances:
                            if appearances[word[0]] == 1:
                                if word[0] in trip_maxQ:
                                    trip_maxQ[word[0]].append(float(word[1]))
                                else:
                                    trip_maxQ[word[0]] = [float(word[1])]
                            else:
                                if word[0] in trip_queue:
                                    trip_queue[word[0]].append(float(word[1]))
                                else:
                                    trip_queue[word[0]] = [float(word[1])]
                            appearances[word[0]] += 1
                        else:
                            if word[0] in trip_rewards:
                                trip_rewards[word[0]].append(float(word[1]))
                            else:
                                trip_rewards[word[0]] = [float(word[1])]
                            appearances[word[0]] = 1
            file.close()

            if idx == 0 and i == 1:
                episode_rewards = pd.DataFrame.from_dict(trip_rewards)
                episode_maxQ = pd.DataFrame.from_dict(trip_maxQ)
                episode_queue = pd.DataFrame.from_dict(trip_queue)

                episode_rewards = pd.DataFrame(episode_rewards.mean().to_dict(),index=[1])
                episode_maxQ = pd.DataFrame(episode_maxQ.mean().to_dict(),index=[1])
                episode_queue = pd.DataFrame(episode_queue.mean().to_dict(),index=[1])
            elif idx == 0 and i > 1:
                temp_rewards = pd.DataFrame.from_dict(trip_rewards)
                temp_maxQ = pd.DataFrame.from_dict(trip_maxQ)
                temp_queue = pd.DataFrame.from_dict(trip_queue)

                temp_rewards = pd.DataFrame(temp_rewards.mean().to_dict(),index=[i])
                temp_maxQ = pd.DataFrame(temp_maxQ.mean().to_dict(),index=[i])
                temp_queue = pd.DataFrame(temp_queue.mean().to_dict(),index=[i])

                episode_rewards = pd.concat([episode_rewards, temp_rewards])
                episode_maxQ = pd.concat([episode_maxQ, temp_maxQ])
                episode_queue = pd.concat([episode_queue, temp_queue])
            elif idx != 0:
                temp_rewards = pd.DataFrame.from_dict(trip_rewards)
                temp_maxQ = pd.DataFrame.from_dict(trip_maxQ)
                temp_queue = pd.DataFrame.from_dict(trip_queue)

                temp_rewards = pd.DataFrame(temp_rewards.mean().to_dict(),index=[i])
                temp_maxQ = pd.DataFrame(temp_maxQ.mean().to_dict(),index=[i])
                temp_queue = pd.DataFrame(temp_queue.mean().to_dict(),index=[i])

                episode_rewards = pd.concat([episode_rewards, temp_rewards], axis = 1)
                episode_maxQ = pd.concat([episode_maxQ, temp_maxQ], axis = 1)
                episode_queue = pd.concat([episode_queue, temp_queue], axis = 1)

        waitingTime[f"{models[idx]}"] = episode_waitingTime
        timeLoss[f"{models[idx]}"] = episode_timeLoss
        duration[f"{models[idx]}"] = episode_duration

    for key, value in fixed_results[current_map].items():
        waitingTime[key] = [value] * nr_episodes

    ax = sns.lineplot(data = waitingTime, dashes=[(1, 0), (1, 0), (1, 0), (5, 3), (5, 3), (5, 3)])
    ax.set(xlabel='Episode index', ylabel='Avg. waiting time', title=f'Avg. waiting time per episode for {current_map}', ylim = (0, 100) if current_map == "Romana" else (30, 1000))
    plt.show()

    for junction in junctions:
        ax = sns.lineplot(data = episode_rewards.filter(like=junction), dashes=False)
        ax.set(xlabel='Episode index', ylabel='Avg. reward', title=f'Avg. reward per episode for {current_map} - {junction}')
        plt.show()

        ax = sns.lineplot(data = episode_maxQ.filter(like=junction), dashes=False)
        ax.set(xlabel='Episode index', ylabel='Avg. max queue length', title=f'Avg. max queue length for {current_map} - {junction}')
        plt.show()

        ax = sns.lineplot(data = episode_queue.filter(like=junction), dashes=False)
        ax.set(xlabel='Episode index', ylabel='Avg. queue length', title=f'Avg. queue length for {current_map} - {junction}')
        plt.show()

    ax = sns.lineplot(data = episode_rewards, dashes=False)
    ax.set(xlabel='Episode index', ylabel='Avg. reward', title=f'Avg. reward per episode for {current_map}')
    plt.show()

    ax = sns.lineplot(data = episode_maxQ, dashes=False)
    ax.set(xlabel='Episode index', ylabel='Avg. max queue length', title=f'Avg. max queue length for {current_map}')
    plt.show()

    ax = sns.lineplot(data = episode_queue, dashes=False)
    ax.set(xlabel='Episode index', ylabel='Avg. queue length', title=f'Avg. queue length for {current_map}')
    plt.show()
   
