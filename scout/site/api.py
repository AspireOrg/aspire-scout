from scout.core import aspire
from flask import Blueprint
from flask import request
from flask import flash
from flask import render_template
from flask import redirect

from .forms import SearchForm

def add_asset_info(sends):
    res = list(set(dic['asset'] for dic in sends))
    assetinfos = aspire.aspired('get_asset_info', params={"assets": res})
    for i in range(len(sends)):
        assetname = sends[i]['asset']
        for asset in assetinfos['result']:
            if asset['asset'] == assetname:
                sends[i]['asset_info'] = asset
                break
        if sends[i].get('asset_info') is not None:
            if sends[i]['asset_info']['asset'] == 'ASP':
                # ASP name defaults to null for some reason
                sends[i]['asset'] = 'ASP'
            elif sends[i]['asset'][:3] == 'ASP':
                # Fix subasset names, they are stored as asset ids and not the longname..
                sends[i]['asset'] = sends[i]['asset_info']['asset_longname']
    return sends


bp = Blueprint('api', __name__, url_prefix='/api/')

@bp.route('blocks/<bindex>', methods=['GET'])
def blocks(bindex):
    # bindex = starting index
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    bindex = int(bindex) - (page * limit)
    block_info = aspire.aspired('get_blocks', {'block_indexes': [bindex] + [bindex - x for x in range(limit)]})
    if 'result' in block_info:
        block_info = list(reversed(block_info['result']))
    else:
        block_info = []
    return {'data': block_info, 'last_page': int(bindex/limit) + 1}


@bp.route('block/<bhash>', methods=['GET'])
def block(bhash):
    block_data = aspire.gasp('getblock', params=[bhash, True])
    if block_data.get('success', False):
        return {'data': block_data['data']}
    return {'data': {}}


@bp.route('block/<block_index>/broadcasts', methods=['GET'])
def block_broadcasts(block_index):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    broadcasts = aspire.aspired('get_broadcasts', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                                "filters": [{'field': 'block_index', 'op': '==', 'value': block_index}]})
    if 'result' in broadcasts:
        broadcasts = broadcasts['result']
    else:
        broadcasts = []
    return {'data': broadcasts, 'last_page': page+1}


@bp.route('block/<block_index>/sends', methods=['GET'])
def block_sends(block_index):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    sends = aspire.aspired('get_sends', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [{'field': 'block_index', 'op': '==', 'value': block_index}]})
    if 'result' in sends:
        sends = sends['result']
    else:
        sends = []

    for send in sends:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': sends, 'last_page': page+1}


@bp.route('block/<block_index>/issuances', methods=['GET'])
def block_issuances(block_index):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    issuances = aspire.aspired('get_issuances',params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [{'field': 'block_index', 'op': '==', 'value': block_index}]})
    if 'result' in issuances:
        issuances = issuances['result']
    else:
        issuances = []

    for send in issuances:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': issuances, 'last_page': page+1}


@bp.route('tx/<txid>', methods=['GET'])
def tx(txid):
    block_data = aspire.gasp('getrawtransaction', params=[txid, True])
    if block_data.get('success', False):
        return {'data': block_data['data']}
    return {'data': block_data}


@bp.route('tx/<txid>/broadcasts', methods=['GET'])
def tx_broadcasts(txid):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    broadcasts = aspire.aspired('get_broadcasts', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                                "filters": [{'field': 'tx_hash', 'op': '==', 'value': txid}]})
    if 'result' in broadcasts:
        broadcasts = broadcasts['result']
    else:
        broadcasts = []
    return {'data': add_asset_info(broadcasts), 'last_page': page+1}


@bp.route('tx/<txid>/sends', methods=['GET'])
def tx_sends(txid):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    sends = aspire.aspired('get_sends', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [{'field': 'tx_hash', 'op': '==', 'value': txid}]})
    if 'result' in sends:
        sends = sends['result']
    else:
        sends = []

    for send in sends:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': add_asset_info(sends), 'last_page': page+1}


@bp.route('tx/<tx>/issuances', methods=['GET'])
def tx_issuances(tx):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    issuances = aspire.aspired('get_issuances',params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [{'field': 'tx_hash', 'op': '==', 'value': tx}]})
    if 'result' in issuances:
        issuances = issuances['result']
    else:
        issuances = []

    for send in issuances:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': issuances, 'last_page': page+1}


@bp.route('events/<bindex>', methods=['GET'])
def events(bindex):
    events = aspire.aspired('get_messages', {'block_index': int(bindex)})
    if 'result' in events:
        events = events['result']
    else:
        events = []
    def yielder():
        for event in events:
            if event.get('category', '') in ['credits', 'debits']:
                continue
            yield event
    return {'data': list(yielder()), 'last_page': 1}


@bp.route('holders/<asset>', methods=['GET'])
def asset_holers(asset):
    events = aspire.aspired('get_holders', {'asset': asset})
    if 'result' in events:
        events = events['result']
    else:
        events = []
    return {'data': events, 'last_page': 1}


@bp.route('richlist/<asset>', methods=['GET'])
def asset_richlist(asset):
    events = aspire.aspired('get_holders', {'asset': asset})
    if 'result' in events:
        events = events['result']
    else:
        events = []
    rich = []
    i = 1
    for event in sorted(events, key=lambda t: t['address_quantity'], reverse=True):
        rich.append({'pos': i, 'address': event['address'], 'balance': float(event['address_quantity']) / 100000000})
        i += 1
    return {'data': rich}


@bp.route('transfers', methods=['GET'])
def transfers():
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    sends = aspire.aspired('get_sends', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit})
    if 'result' in sends:
        sends = sends['result']
    else:
        sends = []
    for send in sends:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']
    return {'data': add_asset_info(sends), 'last_page': page+1}


@bp.route('assets', methods=['GET'])
def assets():
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    assets = aspire.aspired('get_assets', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit})
    if 'result' in assets:
        assets = list(reversed(assets['result']))
    else:
        assets = []
    nassets = []
    for asset in assets:
        if asset['asset_name'] not in ['GASP', 'ASP']:
            nassets.append(asset['asset_name'])
    assets_infos = {}
    if len(assets) > 0:
        assets_infos = aspire.aspireblock('get_assets_info', {'assetsList': nassets})
    result = []
    if 'result' in assets_infos:
        result = assets_infos['result']
    return {'data': result, 'last_page': page+1}


@bp.route('assets/<assetname>/supply', methods=['GET'])
def asset_supply(assetname):
    if assetname == 'ASP':
        return '1000000000.0'  # This is just faster
    return str(int(aspire.aspired('get_asset_info', params={"assets": [assetname]})['result'][0]['supply']) / 100000000)


@bp.route('assets/<assetname>/circulating', methods=['GET'])
def asset_circulating(assetname):
    if assetname == 'ASP':
        supply = int(100000000000000000)
        premine_addys = [
            'GRCfdMktqPs6RyF7ZrN8LY2MYW5ejZG1yQ',
            'GLRN2PBSpjzrnk3zNkZv5Y3GpmK3cVThZm',
            'GW1VzXDG1TjxFeUDBvbWoLhC8DELwUAU4x',
            'GKuMfFwjQoyGy8Bm15pGhM7ZWkSLNqSEvf'
        ]
        premine_balances = aspire.aspired('get_balances', params={"filters": [
            {'field': 'address', 'op': 'IN', 'value': premine_addys},
            {'field': 'asset', 'op': '==', 'value': assetname}
        ], "filterop": "and"})
        total = sum([b['quantity'] for b in premine_balances['result']])
        return str(int(supply - total) / 100000000)
    return str(int(aspire.aspired('get_asset_info', params={"assets": [assetname]})['result'][0]['supply']) / 100000000)


@bp.route('assets/<asset>/sends', methods=['GET'])
def asset_sends(asset):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    sends = aspire.aspired('get_sends', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit, "filters": [{'field': 'asset', 'op': '==', 'value': asset}]})
    if 'result' in sends:
        sends = sends['result']
    else:
        sends = []

    for send in sends:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': sends, 'last_page': page+1}


@bp.route('address/<address>/balances', methods=['GET'])
def address_balances(address):
    gasp_balance = aspire.aspireblock('get_chain_address_info', params={"addresses": [address], "with_uxtos": False, "with_last_txn_hashes": False})
    balances = aspire.aspired('get_balances', params={"filters": [{'field': 'address', 'op': '==', 'value': address}]})
    if 'result' in balances:
        balances = balances['result']
    else:
        balances = []
    for bal in balances:
        if 'asset' in bal and 'GASP' == bal['asset']:
            break
    else:
        balances.insert(0, {'asset': 'GASP', 'quantity': int(float(gasp_balance['result'][0]['info']['balanceSat'].split('.')[0])), 'address': address})

    return {'data': add_asset_info(balances), 'last_page': 1}

@bp.route('address/<address>/sends', methods=['GET'])
def address_sends(address):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    sends = aspire.aspired('get_sends',params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [
                                {'field': 'destination', 'op': '==', 'value': address},
                                {'field': 'source', 'op': '==', 'value': address}
                            ],
                            "filterop": "or"})
    if 'result' in sends:
        sends = sends['result']
    else:
        sends = []

    for send in sends:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': add_asset_info(sends), 'last_page': page+1}


@bp.route('address/<address>/transactions', methods=['GET'])
def address_transactions(address):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 100:
            limit = 100
    except ValueError:
        limit = 15
    # params in searchrawtransactions = [verbose, skip, limit]
    txdata = aspire.gasp('searchrawtransactions', params=[address, 1, page * limit, limit, int(True)])
    if 'data' in txdata:
        return {'data': txdata['data'], 'last_page': page + 1}
    else:
        return txdata


@bp.route('address/<address>/issuances', methods=['GET'])
def address_issuances(address):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    issuances = aspire.aspired('get_issuances',params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                           "filters": [{'field': 'issuer', 'op': '==', 'value': address}]})
    if 'result' in issuances:
        issuances = issuances['result']
    else:
        issuances = []

    for send in issuances:
        txdata = aspire.gasp('getrawtransaction', params=[send['tx_hash'], True])
        send['time'] = txdata['data']['blocktime']

    return {'data': issuances, 'last_page': page+1}


@bp.route('address/<address>/broadcasts', methods=['GET'])
def address_broadcasts(address):
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    broadcasts = aspire.aspired('get_broadcasts', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit,
                                "filters": [{'field': 'source', 'op': '==', 'value': address}]})
    if 'result' in broadcasts:
        broadcasts = broadcasts['result']
    else:
        broadcasts = []
    return {'data': broadcasts, 'last_page': page+1}



@bp.route('broadcasts', methods=['GET'])
def broadcasts():
    try:
        page = int(request.args.get('page', 1)) - 1
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get('size', 15))
        if limit > 15:
            limit = 15
    except ValueError:
        limit = 15
    broadcasts = aspire.aspired('get_broadcasts', params={'order_by': 'block_index', 'order_dir': 'DESC', 'limit': limit, 'offset': page * limit})
    if 'result' in broadcasts:
        broadcasts = broadcasts['result']
    else:
        broadcasts = []
    return {'data': broadcasts, 'last_page': page+1}

