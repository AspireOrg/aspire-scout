from scout.core import aspire
from functools import wraps
from flask import Blueprint
from flask import request
from flask import flash
from flask import render_template
from flask import redirect

from .forms import SearchForm

bp = Blueprint('views', __name__, url_prefix='/')

def check_synced(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        running = aspire.aspired('get_running_info')
        if 'result' in running:
            return func(*args, **kwds)
        else:
            return index()
    return wrapper

@bp.route('static/protocol_changes.json')
def protocol_changes():
    from flask import current_app
    return current_app.send_static_file('protocol_changes.json')

@bp.route('', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('search', methods=['POST'])
@check_synced
def search():
    search_form = SearchForm()
    if request.method == 'POST':
        if search_form.validate():
            if search_form.is_transaction:
                return redirect('/tx/' + str(search_form.search_term.data))
            if search_form.is_block:
                return redirect('/block/' + str(search_form.search_term.data))
            if search_form.is_address:
                return redirect('/address/' + str(search_form.search_term.data))
            if search_form.is_asset:
                return redirect('/asset/' + str(search_form.search_term.data))
    flash('Couldn\'t find what you searched for..', 'danger')
    return render_template('index.html')

@bp.route('block/<bindex>', methods=['GET'])
@check_synced
def block(bindex):
    bindex = bindex.strip()
    try:
        bindex = int(bindex)
        bhash = aspire.gasp('getblockhash', [bindex])
        if 'data' not in bhash:
            raise Exception(bhash)
        bhash = bhash['data']
    except ValueError:
        bhash = bindex

    block = aspire.gasp('getblock', [bhash])
    bindex = block['data']['height']
    transactions = block['data']['tx']

    block_info = aspire.aspired('get_blocks', {'block_indexes': [bindex]})
    if block_info.get('message', '') == 'Server error':
        flash('A server error occured!', 'danger')
        if block_info.get('data'):
            flash(block_info.get('data'), 'warning')
        return render_template('index.html')
    block_info = block_info['result'][0]

    return render_template('block.html',
                           bindex=bindex,
                           block_info=block_info,
                           block=block)

@bp.route('tx/<thash>', methods=['GET'])
@check_synced
def transaction(thash):
    thash = thash.strip()
    tx = aspire.aspired('getrawtransaction', params={"tx_hash": thash, 'verbose': True})
    tx = tx['result']
    # tx_info = aspire.aspired('get_tx_info', params={'tx_hex': tx['result']['hex']})

    if 'blockhash' in tx:
        block = aspire.gasp('getblock', params=[tx['blockhash']])
        if 'data' in block:
            if 'height' in block['data']:
                tx['blockheight'] = block['data']['height']
                blockheight = aspire.gasp('getblockcount')
                tx['confirmations'] = blockheight['data'] - tx['blockheight']

    new_assets = aspire.aspired('get_issuances', params={"filters": [{'field': 'tx_hash', 'op': '==', 'value': thash}]})
    sends = aspire.aspired('get_sends', params={"filters": [{'field': 'tx_hash', 'op': '==', 'value': thash}]})
    dividends = aspire.aspired('get_dividends', params={"filters": [{'field': 'tx_hash', 'op': '==', 'value': thash}]})
    broadcasts = aspire.aspired('get_broadcasts', params={"filters": [{'field': 'tx_hash', 'op': '==', 'value': thash}]})

    return render_template('transaction.html',
                           thash=thash,
                           tx=tx,
                           new_assets=new_assets,
                           sends=sends,
                           dividends=dividends,
                           broadcasts=broadcasts)

@bp.route('address/<addy>', methods=['GET'])
@check_synced
def address(addy):
    addy = addy.strip()
    credits = aspire.aspired('get_credits', params={"filters":
                             [
                             {'field': 'address', 'op': '==', 'value': addy},
                             {'field': 'calling_function', 'op': '==', 'value': 'issuance fee'}
                             ]})
    return render_template('address.html', addy=addy, credits=credits)

@bp.route('asset/<assetname>', methods=['GET'])
@check_synced
def asset(assetname):
    assetname = assetname.strip()
    issuance = aspire.aspired('get_issuances', params={
                                "filters": [
                                    {'field': 'asset', 'op': '==', 'value': assetname},
                                    {'field': 'asset_longname', 'op': '==', 'value': assetname}],
                                "filterop": 'OR'})

    if 'result' not in issuance or len(issuance['result']) == 0:
        return index()

    assetinfo = aspire.aspired('get_asset_info', params={"assets": [assetname]})
    sends = aspire.aspired('get_sends', params={"filters": [{'field': 'asset', 'op': '==', 'value': assetname}]})

    return render_template('asset.html', assetname=assetname, issuance=issuance['result'][0], assetinfo=assetinfo['result'][0], sends=sends['result'])


