import pymysql
from datetime import datetime
from uuid import uuid1
from coinmarketcap import Market
import config


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def isDate(s):
    if not isNumber(s):
        return False

    epoch = float(s)

    if float(epoch) < datetime(2015, 11, 21, 0, 0).timestamp() or float(epoch) > datetime.now().timestamp():
        return False

    try:
        datetime.fromtimestamp(epoch)
        return True
    except (TypeError, ValueError):
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def formatCoinField(field):
    if isinstance(field, str):
        if isNumber(field):
            if isDate(field):
                return f"'{datetime.fromtimestamp(int(float(field))).strftime('%Y-%m-%d %H:%M:%S')}'"
            return f"{field}"
        return f"'{field}'"
    elif isinstance(field, bool):
        return '1' if field else '0'
    elif field is None:
        return "NULL"
    return str(field)


def getInsertCoinSql(coin):
    fields = ['24h_volume_usd', 'available_supply', 'cached', 'id', 'last_updated', 'market_cap_usd', 'max_supply', 'name', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'price_btc', 'price_usd', 'rank', 'symbol', 'total_supply']
    fields_str = '`observation_id`, ' + ", ".join(f"`{f}`" for f in fields) + ', `timestamp`'
    uuid = uuid1()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values_str = f"'{uuid}', "  + ", ".join(formatCoinField(coin[f]) for f in fields) + f", '{now}'"
    sql = f"INSERT INTO coinmarketcap ({fields_str}) VALUES ({values_str})"
    return sql


def main():
    # Open connection to the database
    conn = pymysql.connect(host = config.mysql['host'],
                           port = config.mysql['port'],
                           user = config.mysql['user'],
                           passwd = config.mysql['passwd'],
                           db = config.mysql['db'],
                           charset = 'utf8',
                           autocommit = True)
    cur = conn.cursor()
    
    # Insert coins
    coinmarketcap = Market()
    coins = coinmarketcap.ticker(limit=None)
    for coin in coins:
        print(f'Inserting {coin["symbol"]}')
        sql = getInsertCoinSql(coin)
        cur.execute(sql)

    # Close connection to the database
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
