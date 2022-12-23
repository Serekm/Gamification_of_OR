import streamlit as st
import random
import yaml
from math import sqrt


def nextpage(): st.session_state.page += 1


def restart(): st.session_state.page, st.session_state.turn = 0, 1


def nextturn(): st.session_state.turn += 1


def backlog_check(stock, backlog):
    if stock < 0:
        backlog += abs(stock)
        stock = 0
    return stock, backlog


def eoc(demand, stock_cost, backlog_cost):
    return round(sqrt(2 * demand * (stock_cost + backlog_cost) / (backlog_cost * stock_cost)))


def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros


config = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)

if "page" not in st.session_state:
    st.session_state.page = 0

if "player" not in st.session_state:
    st.session_state.player = 'No Player'

if 'turn' not in st.session_state:
    st.session_state.turn = 1

if 'order' not in st.session_state:
    factory_order = zerolistmaker(10)
    retailer_order = zerolistmaker(10)
    wholesaler_order = zerolistmaker(10)
    distributor_order = zerolistmaker(10)
    customer_order_list = [[100, 100, 400, 400, 400, 400, 400, 400], [100, 100, 200, 400, 100, 400, 200, 400],
                           [100, 100, 200, 400, 600, 800, 1000, 1200], [100, 100, 200, 600, 200, 600, 200, 600]]
    customer_setup = random.randint(0, 3)

    st.session_state.order = {'Manufactory': factory_order, 'Distributor': distributor_order,
                              'Wholesaler': wholesaler_order, 'Retailer': retailer_order,
                              'Customer': customer_order_list[customer_setup]}

if 'stock' not in st.session_state:
    starting_stocks = config['setup']['starting_stocks']
    factory_stocks = starting_stocks
    distributor_stocks = starting_stocks
    wholesaler_stocks = starting_stocks
    retailer_stocks = starting_stocks

    st.session_state.stock = {'Manufactory': factory_stocks, 'Distributor': distributor_stocks,
                              'Wholesaler': wholesaler_stocks, 'Retailer': retailer_stocks}

if 'backlog' not in st.session_state:
    st.session_state.backlog = {'Manufactory': 0, 'Distributor': 0,
                                'Wholesaler': 0, 'Retailer': 0}

if 'score' not in st.session_state:
    st.session_state.score = 0

delay = config['setup']['delay']
stock_cost = config['setup']['stock_cost']
backlog_cost = config['setup']['backlog_cost']
starting_stocks = config['setup']['starting_stocks']

player_order = zerolistmaker(10)
eoc_order = zerolistmaker(10)

start = st.container()
st.button('Next', on_click=nextpage, disabled=(st.session_state.page > 1))

if st.session_state.page == 0:
    start.title('Beer Game')
    start.subheader('Setup')

    player = start.radio('Which player would you like to play?',
                         ('Manufactory', 'Distributor', 'Wholesaler', 'Retailer'))

    if player == 'Manufactory':
        start.text('You are now playing Manufactory')
        st.session_state.player = 'Manufactory'
    elif player == 'Distributor':
        start.text('You are now playing Distributor')
        st.session_state.player = 'Distributor'
    elif player == 'Wholesaler':
        start.text('You are now playing Wholesaler')
        st.session_state.player = 'Wholesaler'
    else:
        start.text('You are now playing Retailer')
        st.session_state.player = 'Retailer'


elif st.session_state.page == 1:
    start.title('Game Introduction')
    start.subheader('Beer Game')
    start.write(f'In the Beer Distribution Game, the players try to order and satisfy the orders of'
                f'4 players and 1 predetermined buyer in the end. You have selected {st.session_state.player.lower()}.')
    start.write(f'The order goes as Manufactory -> Distributor -> Wholesaler -> Retailer -> Customer')
    start.write(f'When you give an order for more Beer, your order will go to the previous player and'
                f' they will send your order which will arrive in {delay} turns to your location and so on.')
    start.write(f'The scores to determine the result of the game will be calculated by multiplying '
                f'your undelivered items by {backlog_cost} and your extra stock by {stock_cost} every turn. '
                f'The goal of the game is to have the minimum points by the end of turn 8.')
    start.write(f'The starting stocks are {starting_stocks} and first order will be '
                f'{st.session_state.order["Customer"][0]}. Press Next to start!')

elif st.session_state.page == 2:
    if st.session_state.turn == 1:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        start.button('Next Turn', on_click=nextturn)

        eoc_order[st.session_state.turn] = eoc(st.session_state.order["Customer"][st.session_state.turn],
                                               stock_cost, backlog_cost)
        st.session_state.order['Manufactory'][st.session_state.turn] = eoc_order[st.session_state.turn]
        st.session_state.order['Distributor'][st.session_state.turn] = eoc_order[st.session_state.turn]
        st.session_state.order['Wholesaler'][st.session_state.turn] = eoc_order[st.session_state.turn]
        st.session_state.order['Retailer'][st.session_state.turn] = eoc_order[st.session_state.turn]
        st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[
            st.session_state.turn]

    elif st.session_state.turn == 2:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 3:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 4:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 5:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 6:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 7:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'How many beers will {st.session_state.player} order?')
        player_order[st.session_state.turn] = start.number_input('Enter how many beers you would like to order',
                                                                 min_value=0)
        if start.button('Submit Turn'):
            st.session_state.order['Manufactory'][st.session_state.turn] = eoc(
                st.session_state.order["Distributor"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Distributor'][st.session_state.turn] = eoc(
                st.session_state.order["Wholesaler"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Wholesaler'][st.session_state.turn] = eoc(
                st.session_state.order["Retailer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order['Retailer'][st.session_state.turn] = eoc(
                st.session_state.order["Customer"][st.session_state.turn-1], stock_cost, backlog_cost)
            st.session_state.order[f'{st.session_state.player}'][st.session_state.turn] = player_order[st.session_state.turn]

            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

        start.write(
            f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
            f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
        start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn-1]} '
                    f'beers last turn'
                    f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn-1]} beers last turn'
                    f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn-1]} beers last turn')
        start.text(f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"]*stock_cost}'
                    f'\nYour point cost from backlog was: '
                    f'{st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}'
                    f'\nYour total point cost was: '
                    f'{st.session_state.stock[f"{st.session_state.player}"]*stock_cost + st.session_state.backlog[f"{st.session_state.player}"]*backlog_cost}')
        st.session_state.score = st.session_state.score + st.session_state.stock[st.session_state.player]*stock_cost +\
                                 st.session_state.backlog[st.session_state.player]*backlog_cost
        start.button('Next Turn', on_click=nextturn)

    elif st.session_state.turn == 8:
        start.title(f'Turn {st.session_state.turn}')
        start.text(f'Your orders will not arrive in time anymore! Press the buttons to finish the game.')
        if start.button('Submit Turn'):
            st.session_state.stock['Manufactory'] = st.session_state.stock['Manufactory'] + \
                                                    st.session_state.order['Manufactory'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Distributor'][st.session_state.turn - 1]
            st.session_state.stock['Distributor'] = st.session_state.stock['Distributor'] + \
                                                    st.session_state.order['Distributor'][
                                                        max(st.session_state.turn - delay, 0)] - \
                                                    st.session_state.order['Wholesaler'][st.session_state.turn - 1]
            st.session_state.stock['Wholesaler'] = st.session_state.stock['Wholesaler'] + \
                                                   st.session_state.order['Wholesaler'][
                                                       max(st.session_state.turn - delay, 0)] - \
                                                   st.session_state.order['Retailer'][st.session_state.turn - 1]
            st.session_state.stock['Retailer'] = st.session_state.stock['Retailer'] + \
                                                 st.session_state.order['Retailer'][
                                                     max(st.session_state.turn - delay, 0)] - \
                                                 st.session_state.order['Customer'][st.session_state.turn - 1]

            st.session_state.stock['Manufactory'], st.session_state.backlog['Manufactory'] = backlog_check(
                st.session_state.stock['Manufactory'],
                st.session_state.backlog['Manufactory'])
            st.session_state.stock['Distributor'], st.session_state.backlog['Distributor'] = backlog_check(
                st.session_state.stock['Distributor'],
                st.session_state.backlog['Distributor'])
            st.session_state.stock['Wholesaler'], st.session_state.backlog['Wholesaler'] = backlog_check(
                st.session_state.stock['Wholesaler'],
                st.session_state.backlog['Wholesaler'])
            st.session_state.stock['Retailer'], st.session_state.backlog['Retailer'] = backlog_check(
                st.session_state.stock['Retailer'],
                st.session_state.backlog['Retailer'])

            start.write(
                f'{st.session_state.player} will get {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn - 1]} '
                f'stocks of beers for next turn and {st.session_state.order[f"{st.session_state.player}"][st.session_state.turn]} for the turn after')
            start.text(f'Manufactory ordered: {st.session_state.order["Manufactory"][st.session_state.turn - 1]} '
                       f'beers last turn'
                       f'\nDistributor ordered: {st.session_state.order["Distributor"][st.session_state.turn - 1]} '
                       f'beers last turn'
                       f'\nWholesaler ordered: {st.session_state.order["Wholesaler"][st.session_state.turn - 1]} '
                       f'beers last turn'
                       f'\nRetailer ordered: {st.session_state.order["Retailer"][st.session_state.turn - 1]} beers last turn'
                       f'\nCustomer ordered: {st.session_state.order["Customer"][st.session_state.turn - 1]} beers last turn')
            start.text(
                f'Your point cost from stock was: {st.session_state.stock[f"{st.session_state.player}"] * stock_cost}'
                f'\nYour point cost from backlog was: '
                f'{st.session_state.backlog[f"{st.session_state.player}"] * backlog_cost}'
                f'\nYour total point cost was: '
                f'{st.session_state.stock[f"{st.session_state.player}"] * stock_cost + st.session_state.backlog[f"{st.session_state.player}"] * backlog_cost}')
        start.button('Next Turn', on_click=nextpage)

elif st.session_state.page == 3:
    start.title('End of the game!')
    start.subheader('Congratulations!')
    start.text(f'Your end score was: {st.session_state.score}')
    start.button('Restart', on_click=restart)
