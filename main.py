import simpy
from utils import load_data
from env import simulation_process
from libs import Logger


def main():
    # csv_path = "/home/thuong/data/merged_output/test_simulate.csv"  # thay bằng file thực tế
    csv_path = "/home/thuong/data/merged_output/grouped_metrics_2024-09-01.csv"
    df = load_data(csv_path)
    Logger.info("START SIMULATION")
    env = simpy.Environment()
    env.process(simulation_process(env, df))
    env.run(until = 5)
if __name__ == "__main__":
    main()
