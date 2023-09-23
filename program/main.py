from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits
from func_messaging import send_message
import time
import json
import datetime


def calcul_tp(intial_price, current_price, size, side):
  tp = (float(current_price) - float(intial_price))*float(size)
  if side == "BUY":
    return tp
  else:
    return tp*-1

def send_tp():
  try:
    open_positions = open("bot_agents.json")
    open_positions_dict = json.load(open_positions)
    time.sleep(2)
    for position in open_positions_dict:
      tp_paire_1_base = calcul_tp(position["price_market_1_entry"], position["price_market_1_current"],
                                  position["order_m1_size"], position["order_m1_side"])
      tp_paire_1_quote = calcul_tp(position["price_market_2_entry"], position["price_market_2_current"],position["order_m2_size"], position["order_m2_side"])
      market_1 = position["market_1"]
      market_2 = position["market_2"]
      data_to_send = f"{market_1} take profite : {tp_paire_1_base} USD || {market_2} take profite : {tp_paire_1_quote} USD"
      send_message(data_to_send)
      time.sleep(0.1)

  except:
    print("unfound bot agents file")

# MAIN FUNCTION
if __name__ == "__main__":

  # Message on start
  send_message("Bot launch successful")

  # Connect to client
  try:
    print("Connecting to Client...")
    client = connect_dydx()
  except Exception as e:
    print("Error connecting to client: ", e)
    send_message(f"Failed to connect to client {e}")
    exit(1)

  # Abort all open positions
  if ABORT_ALL_POSITIONS:
    try:
      print("Closing all positions...")
      close_orders = abort_all_positions(client)
    except Exception as e:
      print("Error closing all positions: ", e)
      send_message(f"Error closing all positions {e}")
      exit(1)

  # Find Cointegrated Pairs
  if FIND_COINTEGRATED:

    # Construct Market Prices
    try:
      print("Fetching market prices, please allow 3 mins...")
      df_market_prices = construct_market_prices(client)
    except Exception as e:
      print("Error constructing market prices: ", e)
      send_message(f"Error constructing market prices {e}")
      exit(1)

    # Store Cointegrated Pairs
    try:
      print("Storing cointegrated pairs...")
      stores_result = store_cointegration_results(df_market_prices)
      if stores_result != "saved":
        print("Error saving cointegrated pairs")
        exit(1)
    except Exception as e:
      print("Error saving cointegrated pairs: ", e)
      send_message(f"Error saving cointegrated pairs {e}")
      exit(1)

  start_time = datetime.datetime.now()
  # Run as always on
  while True:
    
    # Place trades for opening positions
    if MANAGE_EXITS:
      try:
        print("Managing exits...")
        manage_trade_exits(client)
      except Exception as e:
        print("Error managing exiting positions: ", e)
        send_message(f"Error managing exiting positions {e}")
        exit(1)

    # Place trades for opening positions
    if PLACE_TRADES:
      try:
        print("Finding trading opportunities...")
        open_positions(client)
      except Exception as e:
        print("Error trading pairs: ", e)
        send_message(f"Error opening trades {e}")
        exit(1)
    
    current_time = heure_actuelle = datetime.datetime.now()
    difference_secondes = (heure_actuelle - start_time).total_seconds()
    
    if difference_secondes >= 5400:
      send_tp()
      start_time = datetime.datetime.now()