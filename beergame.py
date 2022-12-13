import pandas
import numpy
import random
import yaml


# TODO Economic order quantity kullanan yapay zeka ekle oyuncular için, streamlit gibi bir araçla arayüz ekle
def backlog_check(stock, backlog):
    if stock < 0:
        backlog += abs(stock)
        stock = 0
    return stock, backlog


def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros


config = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)

delay = config['setup']['delay']
stock_cost = config['setup']['stock_cost']
backlog_cost = config['setup']['backlog_cost']
starting_stocks = config['setup']['starting_stocks']
factory_stocks = starting_stocks
distributor_stocks = starting_stocks
wholesaler_stocks = starting_stocks
retailer_stocks = starting_stocks
factory_backlog, distributor_backlog, wholesaler_backlog, retailer_backlog = 0, 0, 0, 0

factory_order = zerolistmaker(10)
consumer_order = zerolistmaker(10)
retailer_order = zerolistmaker(10)
wholesaler_order = zerolistmaker(10)
distributor_order = zerolistmaker(10)
customer_order_list = [[100, 100, 400, 400, 400, 400, 400], [100, 100, 200, 400, 100, 400, 200],
                       [100, 100, 200, 400, 600, 800, 1000], [100, 100, 200, 600, 200, 600, 200]]
customer_setup = random.randint(0, 3)

# TODO add backlog and points per turn lists

print(f'Start game, {customer_order_list[customer_setup][0]} customer orders this turn,'
      f'\nEvery location has a starting stock of {starting_stocks}, '
      f'\nCurrent delay of production and logistics is {delay} turns.')

factory_order[1] = int(input('How many beers will brewery produce?'))
distributor_order[1] = int(input('How many beers will distributor order?'))
wholesaler_order[1] = int(input('How many beers will wholesaler order?'))
retailer_order[1] = int(input('How many beers will retailer order?'))

for turn in range(1, 8):
    customer_order = customer_order_list[customer_setup][turn - 1]
    print(f'start turn {turn}, customer order is {customer_order}')

    # TODO missing unsatisfied orders: record them, deduct them from this turn and add it to next turn order
    factory_stocks = factory_stocks + factory_order[max(turn - delay, 0)] - distributor_order[turn]
    distributor_stocks = distributor_stocks + distributor_order[max(turn - delay, 0)] - wholesaler_order[turn]
    wholesaler_stocks = wholesaler_stocks + wholesaler_order[max(turn - delay, 0)] - retailer_order[turn]
    retailer_stocks = retailer_stocks + retailer_order[max(turn - delay, 0)] - customer_order

    factory_stocks, factory_backlog = backlog_check(factory_stocks, factory_backlog)
    distributor_stocks, distributor_backlog = backlog_check(distributor_stocks, distributor_backlog)
    wholesaler_stocks, wholesaler_backlog = backlog_check(wholesaler_stocks, wholesaler_backlog)
    retailer_stocks, retailer_backlog = backlog_check(retailer_stocks, retailer_backlog)

    print(f'Current stocks are as follows:\n'
          f'Factory: {factory_stocks}\n'
          f'Distributor: {distributor_stocks}\n'
          f'Wholesaler: {wholesaler_stocks}\n'
          f'Retailer: {retailer_stocks}')
    print(f'Current backlogs are as follows:\n'
          f'Factory: {factory_backlog}\n'
          f'Distributor: {distributor_backlog}\n'
          f'Wholesaler: {wholesaler_backlog}\n'
          f'Retailer: {retailer_backlog}')

    # TODO make more modular, make function that takes player as input instead
    print(
        f'Factory will get {factory_order[turn - 1]} stock for next order and {factory_order[turn]} stock for the one after.\n'
        f'Distributor ordered {distributor_order[turn]} from you last turn.\n'
        f'Cost for factory this turn was {stock_cost * factory_stocks} for stocked goods and {backlog_cost * factory_backlog} for backlog of goods')
    factory_order[turn + 1] = int(input('How many beers will brewery produce?'))

    print(
        f'Distributor will get {distributor_order[turn - 1]} stock for next order and {distributor_order[turn]} stock for the one after.\n'
        f'Wholesaler ordered {wholesaler_order[turn]} from you last turn.\n'
        f'Cost for distributor this turn was {stock_cost * distributor_stocks} for stocked goods and {backlog_cost * distributor_backlog} for backlog of goods')
    distributor_order[turn + 1] = int(input('How many beers will distributor order?'))

    print(
        f'Wholesaler will get {wholesaler_order[turn - 1]} stock for next order and {wholesaler_order[turn]} stock for the one after.\n'
        f'Retailer ordered {retailer_order[turn]} from you last turn.\n'
        f'Cost for wholesaler this turn was {stock_cost * wholesaler_stocks} for stocked goods and {backlog_cost * wholesaler_backlog} for backlog of goods')
    wholesaler_order[turn + 1] = int(input('How many beers will wholesaler order?'))

    print(
        f'Retailer will get {retailer_order[turn - 1]} stock for next order and {retailer_order[turn]} stock for the one after.\n'
        f'Customer ordered {customer_order} from you last turn.\n'
        f'Cost for retailer this turn was {stock_cost * retailer_stocks} for stocked goods and {backlog_cost * retailer_backlog} for backlog of goods')
    retailer_order[turn + 1] = int(input('How many beers will retailer order?'))

    # TODO calculate this turn total points and print them

    print(f'End of turn: {turn}')

# TODO add end game message and total score

"""
players: factory, distrubitor, wholesaler, retailer
parameters: delays, inventory cost, backorder cost
performance: individual supply chain cost, total supply chain cost

steps to code: 
1) check how many items are added start of turn
2) type how many orders was done by next player, 
3) auto deduct the beer sent (calculate costs, create backorder)
4) place how many to order for next turn (player action)
"""
