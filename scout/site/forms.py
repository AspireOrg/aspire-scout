from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from scout.core import aspire

class SearchForm(FlaskForm):
    search_term = StringField('Search Term', [DataRequired()], render_kw={'placeholder': 'Search Transaction ID, Block #, Addresses and Assets...'})
    submit = SubmitField('Search')

    is_transaction = False
    is_block = False
    is_address = False
    is_asset = False

    def validate(self):
        term = str(self.search_term.data).strip()

        # Check for block number
        try:
            block_id = int(term)
            block_data = aspire.gasp('getblockhash', params=[block_id])
            if block_data.get('success', False):
                self.is_block = True
                return True
        except ValueError:
            pass

        # Check for block hash
        block_data = aspire.gasp('getblock', params=[term])
        if block_data.get('success', False):
            self.is_block = True
            return True

        # Check for txid
        txid = aspire.gasp('getrawtransaction', params=[term])
        if txid.get('success', False):
            self.is_transaction = True
            return True

        # Check for address
        address = aspire.gasp('validateaddress', params=[term])
        if address.get('success', False) and address.get('data', {}).get('isvalid', False):
            self.is_address = True
            return True

        # Check for asset
        assetinfo = aspire.aspired('get_asset_info', params={"assets": [term]})
        if 'result' in assetinfo and len(assetinfo['result']) > 0:
            self.is_asset = True
            return True

        return True
